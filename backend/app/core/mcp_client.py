import json
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from app.db.user_session import UserSessionManager
from app.models.tool_schemas import tools
from app.utils.advisor_utils import (
    build_system_prompt,
    convert_markdown_to_html,
    call_provider_endpoint,
)
from app.config import ADVICE_MODEL, OPEN_AI_API_KEY
from app.core.provider_endpoint_map import endpoint_map

client = OpenAI(api_key=OPEN_AI_API_KEY)


async def validate_prompt(question: str, user_id: int, portfolio_id: int) -> bool:
    # Call validation endpoints first via HTTPfv
    validate_prompt_resp = await call_provider_endpoint(
        endpoint_map["validate_prompt"],
        {"question": question, "user_id": user_id, "portfolio_id": portfolio_id},
    )
    if not validate_prompt_resp.get("valid", False):
        return {
            "archived": False,
            "summary": "<p>Invalid question. Please ask a relevant investment question.</p>",
        }

    validate_investment_goal_resp = await call_provider_endpoint(
        endpoint_map["validate_investment_goal"],
        {"question": question, "user_id": user_id, "portfolio_id": portfolio_id},
    )

    if not validate_investment_goal_resp.get("valid", False):
        return {
            "archived": False,
            "summary": "<p>"
            "I cannot find your investment objectives in my memory. "
            "Could you please share your short-term and long-term investment objectives so I can better advise you"
            "(e.g. growth, dividend income, capital preservation, etc.)."
            "</p>",
        }


async def construct_initial_messages(question: str, db: AsyncSession, portfolio_id: int, user_id: int) -> list:
    """Construct the initial messages for OpenAI."""
    return [
        {"role": "system", "content": await build_system_prompt(user_id, portfolio_id, db)},
        {"role": "user", "content": question},
    ]

# deprecated, to remove in future PR
# async def process_final_message(user_id: int, messages: list, db: AsyncSession) -> dict:
#     # Final message using generated advice prompt
#     response = client.chat.completions.create(
#         model=ADVICE_MODEL,
#         messages=messages,
#     )

#     final_msg = response.choices[0].message.content

#     await UserSessionManager.update_session(
#             user_id=user_id,
#             db=db,
#             updates={
#                 "total_prompts_used": await UserSessionManager.get_total_prompts_used(user_id) + 1
#             },
#         )

#     return {
#         "archived": True,
#         "summary": convert_markdown_to_html(final_msg),
#     }


async def handle_tool_call(choice, messages, tool_outputs, user_id, portfolio_id, stop):
    for tool_call in choice.message.tool_calls:
        print("Tool call: ", tool_call)
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        args.pop("user_id", None)
        args.pop("portfolio_id", None)

        payload = {
            **args,
            "user_id": user_id,
            "portfolio_id": portfolio_id,
        }

        endpoint = endpoint_map.get(name)
        if not endpoint:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": json.dumps({"error": f"Unknown tool requested: {name}"}),
                }
            )
            continue

        tool_result = await call_provider_endpoint(endpoint, payload)
        tool_outputs[name] = tool_result

        if name == "prepare_advice_template":
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": json.dumps(tool_result),
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": tool_result["advice_prompt"],
                }
            )
            stop = True
        else:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": json.dumps(tool_result),
                }
            )
    return choice, messages, tool_outputs, stop


async def run_mcp_client_pipeline(
    question: str,
    user_id: int,
    portfolio_id: int,
    db: AsyncSession = None,
) -> dict:
    
    prompt_count = await UserSessionManager.get_total_prompts_used(user_id)
    if prompt_count >= 3:
        return {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts allowed for today.</p>",
        }
    # Call validation endpoints first via HTTPfv
    validation_issue = await validate_prompt(question, user_id, portfolio_id)
    if validation_issue:
        return validation_issue

    messages = await construct_initial_messages(question, db, portfolio_id, user_id)

    tool_outputs = {}
    stop = False

    while True:
        response = client.chat.completions.create(
            model=ADVICE_MODEL, messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]
        if choice.finish_reason == "stop":
            await UserSessionManager.update_session(
                user_id=user_id,
                db=db,
                updates={
                    "total_prompts_used": await UserSessionManager.get_total_prompts_used(user_id) + 1
                },
            )

            return {
                "archived": True,
                "summary": convert_markdown_to_html(choice.message.content)
            }
         
        if choice.finish_reason == "tool_calls":
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": choice.message.tool_calls,
                }
            )

        choice, messages, tool_outputs, stop = await handle_tool_call(
            choice, messages, tool_outputs, user_id, portfolio_id, stop
        )
        print("Stop: ", stop)
        if stop:
            break

    await UserSessionManager.update_session(
        user_id=user_id,
        db=db,
        updates={
            "total_prompts_used": await UserSessionManager.get_total_prompts_used(user_id) + 1
        },
    )
    return {
            "archived": True,
            "summary": convert_markdown_to_html(choice.message.content)
        }
    # return await process_final_message(user_id, messages, db) # deprecated, to remove in future PR
