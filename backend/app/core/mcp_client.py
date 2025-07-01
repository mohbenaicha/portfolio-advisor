import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from app.db.user_session import UserSessionManager
from app.models.sql_models import Portfolio
from app.models.tool_schemas import tools
from app.utils.advisor_utils import (
    build_system_prompt,
    convert_markdown_to_html,
    call_provider_endpoint,
    increment_prompt_usage,
    count_tokens
)
from app.config import OPEN_AI_API_KEY, LLM
from app.core.provider_endpoint_map import endpoint_map

client = OpenAI(api_key=OPEN_AI_API_KEY)


async def validate_prompt(question: str, user_id: int, portfolio_id: int, db: AsyncSession | None) -> dict | None:
    # Count tokens for validation
    validation_tokens = count_tokens(question, LLM)
    print(f"Validation input tokens: {validation_tokens}")
    
    # Call validation endpoints first via HTTPfv
    validate_prompt_resp = await call_provider_endpoint(
        endpoint_map["validate_prompt"],
        {"question": question, "user_id": user_id, "portfolio_id": portfolio_id},
    )
    if not validate_prompt_resp.get("valid", False):
        response_msg = "<p>Invalid question. Please ask a relevant investment question.</p>"
        output_tokens = count_tokens(response_msg, LLM)
        print(f"Validation output tokens: {output_tokens}")
        return {
            "archived": False,
            "summary": response_msg,
            "token_counts": {
                "input_tokens": validation_tokens,
                "output_tokens": output_tokens
            },
        }

    validate_investment_goal_resp = await call_provider_endpoint(
        endpoint_map["validate_investment_goal"],
        {"question": question, "user_id": user_id, "portfolio_id": portfolio_id},
    )

    if not validate_investment_goal_resp.get("valid", False):
        if db:
            result = await db.execute(
                select(Portfolio.name).where(
                    Portfolio.id == portfolio_id, 
                    Portfolio.user_id == user_id
                )
            )
            portfolio_name = result.scalar_one_or_none()
        else:
            portfolio_name = "Unknown"
        
        response_msg = "<p>" + f"I cannot find your investment objectives in my memory for the portfolio: <code>{portfolio_name}</code>. " + "Could you please share your short-term and long-term investment objectives so I can better advise you" + "(e.g. growth, dividend income, capital preservation, etc.)." + "</p>"
        output_tokens = count_tokens(response_msg, LLM)
        print(f"Validation output tokens: {output_tokens}")
        return {
            "archived": False,
            "summary": response_msg,
            "token_counts": {
                "input_tokens": validation_tokens,
                "output_tokens": output_tokens
            },
        }
    
    print(f"Validation output tokens: 0 (no response)")
    return None


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


async def handle_tool_call(choice, messages, tool_outputs, user_id, portfolio_id, stop, total_input_tokens: int = 0, total_output_tokens: int = 0):
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

        # Extract token counts from tool responses
        if isinstance(tool_result, dict) and "token_counts" in tool_result:
            token_counts = tool_result["token_counts"]
            if isinstance(token_counts, dict):
                input_tokens = token_counts.get("input_tokens", 0)
                output_tokens = token_counts.get("output_tokens", 0)
                if isinstance(input_tokens, (int, float)):
                    total_input_tokens += int(input_tokens)
                if isinstance(output_tokens, (int, float)):
                    total_output_tokens += int(output_tokens)
                print(f"Tool '{name}' tokens added to total - Input: {input_tokens}, Output: {output_tokens}")
        # Always add tool response to messages, regardless of token counts
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
        print(f"Tool response tokens added: {tool_response_tokens}")

    return choice, messages, tool_outputs, stop, total_input_tokens, total_output_tokens


async def run_mcp_client_pipeline(
    question: str,
    user_id: int,
    portfolio_id: int,
    db: AsyncSession | None = None,
) -> dict:

    prompt_count = await UserSessionManager.get_total_prompts_used(user_id)
    if prompt_count >= 3:
        return {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts allowed for today.</p>",
        }

    # Initialize token counters for the entire pipeline
    total_input_tokens = 0
    total_output_tokens = 0
    cumulative_api_input_tokens = 0
    cumulative_api_output_tokens = 0

    # Call validation endpoints first via HTTPfv
    validation_issue = await validate_prompt(question, user_id, portfolio_id, db)
    if validation_issue:
        # Extract token counts from validation response
        if isinstance(validation_issue, dict) and "token_counts" in validation_issue:
            total_input_tokens += validation_issue["token_counts"]["input_tokens"]
            total_output_tokens += validation_issue["token_counts"]["output_tokens"]
            print(f"Validation tokens added to total - Input: {validation_issue['token_counts']['input_tokens']}, Output: {validation_issue['token_counts']['output_tokens']}")
        return validation_issue

    messages = await construct_initial_messages(question, portfolio_id, user_id)

    tool_outputs = {}
    stop = False

    while True:
        # Count input tokens for this iteration - include tools
        input_text = " ".join([msg.get("content", "") for msg in messages if msg.get("content") is not None])
        message_tokens = count_tokens(input_text, LLM)
        tool_tokens = count_tool_tokens(tools, LLM)
        input_tokens = message_tokens + tool_tokens
        total_input_tokens += input_tokens
        
        # DEBUG: Log the actual messages being sent
        print("=" * 60)
        print("DEBUG: Messages being sent to API:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content")
            tool_calls = msg.get("tool_calls", [])
            print(f"Message {i+1} - Role: {role}")
            if content is not None:
                print(f"Content length: {len(content)} chars")
                print(f"Content preview: {content[:200]}...")
            else:
                print("Content: None")
            if tool_calls:
                print(f"Tool calls: {len(tool_calls)}")
            print("-" * 40)
        
        print(f"Message tokens this iteration: {message_tokens}")
        print(f"Tool definition tokens: {tool_tokens}")
        print(f"Total input tokens this iteration: {input_tokens}")
        print(f"Total input tokens so far: {total_input_tokens}")
        print("=" * 60)

        response = client.chat.completions.create(
            model=LLM, messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]
        
        # Get token usage from OpenAI API response and accumulate
        if response.usage:
            input_tokens_api = response.usage.prompt_tokens
            output_tokens_api = response.usage.completion_tokens
            total_tokens_api = response.usage.total_tokens
            cumulative_api_input_tokens += input_tokens_api
            cumulative_api_output_tokens += output_tokens_api
            print(f"[API COST] OpenAI API tokens this iteration - Input: {input_tokens_api}, Output: {output_tokens_api}, Total: {total_tokens_api}")
            print(f"[API COST] Cumulative OpenAI API tokens - Input: {cumulative_api_input_tokens}, Output: {cumulative_api_output_tokens}")
        
        # Count output tokens for this iteration
        output_tokens = response.usage.completion_tokens if response.usage else 0
        total_output_tokens += output_tokens
        
        print(f"Output tokens this iteration: {output_tokens}")
        print(f"Total output tokens so far: {total_output_tokens}")

        if choice.finish_reason == "stop":
            if db:
                await increment_prompt_usage(user_id, db)
                print(f"Total prompts used: {await UserSessionManager.get_total_prompts_used(user_id)}")
            
            # Final comprehensive token summary
            print("=" * 60)
            print("FINAL TOKEN USAGE SUMMARY")
            print("=" * 60)
            print(f"Total Input Tokens:  {total_input_tokens}")
            print(f"Total Output Tokens: {total_output_tokens}")
            print(f"Total Tokens Used:   {total_input_tokens + total_output_tokens}")
            print(f"OpenAI API Cumulative - Input: {cumulative_api_input_tokens}, Output: {cumulative_api_output_tokens}")
            print("=" * 60)
            print("Breakdown:")
            print("- Validation tokens (if any)")
            print("- Tool call tokens (news retrieval, etc.)")
            print("- Main conversation loop tokens")
            print("- Summary/embedding tokens (logged separately per article)")
            print("=" * 60)
            
            return {
                "archived": True,
                "summary": convert_markdown_to_html(choice.message.content),
            }

        if choice.finish_reason == "tool_calls":
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": choice.message.tool_calls,
                }
            )

        choice, messages, tool_outputs, stop, total_input_tokens, total_output_tokens = await handle_tool_call(
            choice, messages, tool_outputs, user_id, portfolio_id, stop, total_input_tokens, total_output_tokens
        )
        # Debug: Print tool call names and result sizes/keys
        for tool_name, tool_result in tool_outputs.items():
            if isinstance(tool_result, dict):
                keys = list(tool_result.keys())
                print(f"[DEBUG] Tool '{tool_name}' result keys: {keys}")
                for k in keys:
                    v = tool_result[k]
                    if isinstance(v, list):
                        print(f"[DEBUG] Tool '{tool_name}' key '{k}' is a list of length {len(v)}")
                    elif isinstance(v, str):
                        print(f"[DEBUG] Tool '{tool_name}' key '{k}' is a string of length {len(v)}")
                    else:
                        print(f"[DEBUG] Tool '{tool_name}' key '{k}' type: {type(v)}")
            else:
                print(f"[DEBUG] Tool '{tool_name}' result type: {type(tool_result)}")

            if tool_name == "retrieve_news" and isinstance(tool_result, dict):
                articles = tool_result.get("articles", [])
                print(f"[DEBUG] 'retrieve_news' articles field details:")
                for i, article in enumerate(articles):
                    if isinstance(article, dict):
                        for k, v in article.items():
                            if isinstance(v, str):
                                print(f"  Article {i} key '{k}' string length: {len(v)}")


# Add this function to count tool definition tokens
def count_tool_tokens(tools_list, model: str = LLM) -> int:
    """Count tokens in tool definitions."""
    import json
    tools_json = json.dumps(tools_list)
    return count_tokens(tools_json, model)
        
