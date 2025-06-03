# app/core/mcp_client.py

import json
from fastapi.encoders import jsonable_encoder
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.openai_client import validate_prompt, validate_investment_goal
from app.models.tool_schemas import tools
from app.core.tool_function_map import TOOL_FUNCTION_MAP
from app.utils.memory_utils import get_investment_objective
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary

openai = OpenAI()


async def run_mcp_client_pipeline(
    question: str,
    user_id: int,
    portfolio_id: int,
    db: AsyncSession,
) -> dict:
    """
    MCP Client: Executes post-validation LLM-driven tool workflow
    """

    # Step 1: Validation (hardcoded / deterministic logic)
    if not (await validate_prompt(question, portfolio_id, user_id, db)).get(
        "valid", False
    ):
        return {
            "archived": False,
            "summary": "<p>Invalid question. Please ask a relevant investment question.</p>",
        }

    if not (await validate_investment_goal(question, user_id, portfolio_id, db)).get(
        "valid", False
    ):
        return {
            "archived": False,
            "summary": "<p>Unable to determine your investment objective. Please clarify your goals.</p>",
        }

    # Step 2: Initial context for the LLM
    exporsure_summary = get_exposure_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    portfolio_summary = get_portfolio_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    objectives = get_investment_objective(user_id, portfolio_id)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional investment advisor. "
                "Given the user's question, portfolio information, and investment objectives, "
                "use available tools to determine the best course of action."
            ),
        },
        {"role": "user", "content": question},
        {
            "role": "assistant",
            "content": (
                f"Here is the user's portfolio summary:\n{portfolio_summary}\n\n"
                f"Here is the user's exposure summary:\n{exporsure_summary}\n\n"
                f"And their investment objectives:\n{objectives}"
            ),
        },
    ]

    # Step 3: Tool execution loop
    tool_outputs = {}
    while True:
        response = openai.chat.completions.create(
            model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
        )

        choice = response.choices[0]
        if choice.finish_reason == "stop":
            return {"archived": True, "summary": choice.message.content}

        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # Merge context args (always needed)
                args.update(
                    {"user_id": user_id, "portfolio_id": portfolio_id, "db": db}
                )

                # Dispatch tool
                tool_result = await TOOL_FUNCTION_MAP[name](**args)

                # Record and feed result back into LLM
                tool_outputs[name] = tool_result
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(tool_result),
                    }
                )
        else:
            # Unexpected finish_reason
            return {
                "archived": False,
                "summary": "<p>Ran into an error. Please try again later or contact the administrator.</p>",
            }
