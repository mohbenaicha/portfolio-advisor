import json
from openai import OpenAI
from app.models.tool_schemas import tools
from app.utils.advisor_utils import build_system_prompt, convert_markdown_to_html, call_provider_endpoint
from app.config import ADVICE_MODEL
from app.core.provider_endpoint_map import endpoint_map

openai = OpenAI()

async def run_mcp_client_pipeline(
    question: str,
    user_id: int,
    portfolio_id: int,
) -> dict:
    # Call validation endpoints first via HTTP
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
            "summary": "<p>Unable to determine your investment objective. Please clarify your goals.</p>",
        }

    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": question},
    ]

    tool_outputs = {}
    stop_after_advice_template = False
    while True:
        response = openai.chat.completions.create(
            model=ADVICE_MODEL, messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            return {
                "archived": True,
                "summary": convert_markdown_to_html(choice.message.content),
            }

        if choice.finish_reason == "tool_calls":
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": choice.message.tool_calls,
            })

            print("\n[MCP client loop] Received tool calls:", [tc.function.name for tc in choice.message.tool_calls])
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
                    print(f"[MCP client loop] No endpoint found for tool: {name}")
                    print(f"[MCP client loop] Appending tool response for: {name}")
                    print(f"[MCP client loop] Appending tool response message for: {name}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps({"error": f"Unknown tool requested: {name}"}),
                    })
                    continue

                # print(f"[MCP client loop] Calling endpoint: {endpoint} with payload: {payload}")
                tool_result = await call_provider_endpoint(endpoint, payload)
                print(f"[MCP client loop] Tool result for {name}: {tool_result}")
                tool_outputs[name] = tool_result

                if name == "prepare_advice_template":
                    print("[MCP client loop] Appending user message with advice_prompt")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(tool_result),
                    })
                    messages.append({
                        "role": "user",
                        "content": tool_result["advice_prompt"],
                    })
                    stop_after_advice_template = True
                else:
                    print(f"[MCP client loop] Appending tool response for: {name}")
                    print(f"[MCP client loop] Appending tool response message for: {name}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(tool_result),
                    })

        if stop_after_advice_template:
            print("[MCP client loop] Breaking loop after prepare_advice_template")
            break

    # Final message using generated advice prompt
    response = openai.chat.completions.create(
        model=ADVICE_MODEL,
        messages=messages,
    )

    final_msg = response.choices[0].message.content

    return {
        "archived": True,
        "summary": convert_markdown_to_html(final_msg),
    }
