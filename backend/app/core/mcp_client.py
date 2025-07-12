import json
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from app.db.user_session import UserSessionManager
from app.models.tool_schemas import tools
from app.utils.advisor_utils import (
    build_system_prompt,
    convert_markdown_to_html,
    call_provider_endpoint,
    increment_prompt_usage,
    count_tokens,
    check_prompt_limit
)
from app.config import OPEN_AI_API_KEY, LLM
from app.core.provider_endpoint_map import endpoint_map

client = OpenAI(api_key=OPEN_AI_API_KEY)


async def validate_prompt(question: str, user_id: int, portfolio_id: int, db: AsyncSession | None) -> dict | None:
    
    # Call validation endpoints first via HTTPfv
    validate_prompt_resp = await call_provider_endpoint(
        endpoint_map["validate_prompt"],
        {"question": question, "user_id": user_id, "portfolio_id": portfolio_id},
    )
    if not validate_prompt_resp.get("valid", False):
        response_msg = "<p>Invalid question. Please ask a relevant investment question.</p>"
        return {
            "archived": False,
            "summary": response_msg,
            
        }
    
    return {}


async def construct_initial_messages(
    question: str, portfolio_id: int, user_id: int
) -> list:
    """Construct the initial messages for OpenAI."""
    return [
        {
            "role": "system",
            "content": await build_system_prompt(user_id, portfolio_id),
        },
        {"role": "user", "content": question},
    ]


async def handle_tool_call(choice, messages, tool_outputs, user_id, portfolio_id, stop, question: str | None = None, total_input_tokens: int = 0, total_output_tokens: int = 0):
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

        # Pass the actual question manually for all tools
        if question:
            payload["question"] = question

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

        print(f"[TOOL CALL] Invoking tool: {name}")
        tool_result = await call_provider_endpoint(endpoint, payload)
        tool_outputs[name] = tool_result


        # Add tool response to messages
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": json.dumps(tool_result),
            }
        )

        tool_response_tokens = count_tokens(json.dumps(tool_result), LLM)
        total_input_tokens += tool_response_tokens

    return choice, messages, tool_outputs, stop


async def run_mcp_client_pipeline(
    question: str,
    user_id: int,
    portfolio_id: int,
    db: AsyncSession | None = None,
) -> dict:
    # Check both prompt and failed prompt limits
    limit_hit, limit_response = await check_prompt_limit(user_id)
    if limit_hit:
        if isinstance(limit_response, dict):
            limit_response["final_message"] = True
        return limit_response
    # Call validation endpoints first via HTTPfv
    validation_issue = await validate_prompt(question, user_id, portfolio_id, db)
    if validation_issue:
        if db:
            await UserSessionManager.increment_failed_prompts(user_id, db)
            # Re-check limit after increment
            limit_hit, limit_response = await check_prompt_limit(user_id)
            if limit_hit:
                if isinstance(limit_response, dict):
                    limit_response["final_message"] = True
                return limit_response
        if isinstance(validation_issue, dict):
            validation_issue["final_message"] = False
        return validation_issue

    prompt_count = await UserSessionManager.get_total_prompts_used(user_id)
    if prompt_count >= 3:
        return {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts allowed for today.</p>",
            "final_message": False,
        }

    messages = await construct_initial_messages(question, portfolio_id, user_id)

    tool_outputs = {}
    stop = False

    while True:
        
        # Send messages to OpenAI API
        response = client.chat.completions.create(
            model=LLM, messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]
        
        # If the conversation is over, increment the prompt usage and return the summary
        if choice.finish_reason == "stop":
            if db:
                await increment_prompt_usage(user_id, db)
      
            
            return {
                "archived": True,
                "summary": convert_markdown_to_html(choice.message.content),
                "final_message": True,
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
            choice, messages, tool_outputs, user_id, portfolio_id, stop, question
        )

    # For all other returns (prompt limit, validation, etc), add final_message: False if not already present
    # (add this to each return dict that doesn't have final_message)