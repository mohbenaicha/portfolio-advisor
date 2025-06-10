import json
from openai import OpenAI
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
            "Could you please share your short-term and long-term investment objectives so I can better advise you."
            "</p>",
        }


def construct_initial_messages(question: str) -> list:
    """Construct the initial messages for OpenAI."""
    return [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": question},
    ]

def process_final_message(messages: list) -> dict:
    # Final message using generated advice prompt
    response = client.chat.completions.create(
        model=ADVICE_MODEL,
        messages=messages,
    )

    final_msg = response.choices[0].message.content

    return {
        "archived": True,
        "summary": convert_markdown_to_html(final_msg),
    }


async def handle_tool_call(choice, messages, tool_outputs, user_id, portfolio_id, stop):
    for tool_call in choice.message.tool_calls:
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
                    "content": json.dumps(
                        {"error": f"Unknown tool requested: {name}"}
                    ),
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
) -> dict:
    # Call validation endpoints first via HTTPfv
    validation_issue = await validate_prompt(question, user_id, portfolio_id)
    if validation_issue:
        return validation_issue

    messages = construct_initial_messages(question)

    tool_outputs = {}
    stop = False


    while True:
        response = client.chat.completions.create(
            model=ADVICE_MODEL, messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            return {
            "archived": False,
            "summary": "<p>"
            "Given your portfolio and investment objective, I could not figure out a clear instruction from your prompt."
            " Please provide a clear prompt for me to advise you properly."
            "</p>",
            }

        if choice.finish_reason == "tool_calls":
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": choice.message.tool_calls,
                }
            )

        choice, messages, tool_outputs, stop = await handle_tool_call(choice, messages, tool_outputs, user_id, portfolio_id, stop)
        if stop:
            break

    return process_final_message(messages)
