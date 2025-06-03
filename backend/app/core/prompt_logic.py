from sqlalchemy.ext.asyncio import AsyncSession
from app.services.openai_client import (
    validate_prompt,
    validate_investment_goal,
    determine_if_augmentation_required,
    retrieve_news,
    generate_advice,
)
from app.db.user_session import UserSessionManager
from app.utils.advisor_utils import convert_markdown_to_html


async def handle_prompt(request, db: AsyncSession, user_id: int):
    """
    Pipeline to handle user prompt through RAG including:
     1. extracting entities usin gpt-4o-mini,
     2. fetching news data using mongodb, or using alpha vantage if no keyword articles are stored in mongodb;
     3. summarizing news data, and caching summaries
     4. making final prompt to get investment advice with more detailed protfolio presentation and summary news (gpt-4o-mini)
    """
    # Check the number of prompts used by the user
    session = UserSessionManager.get_session(user_id)
    if session["total_prompts_used"] >= 3:
        return {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts you can use today, please check back tomorrow. "
            "If you need additional quota for today, you can request additional quota by emailing mohamed.benaicha@hotmail.com</p>",
        }

    print(" Extracting Entities using GPT-4o mini ")

    # step 1: Validate the question
    is_question_valid = await validate_prompt(request.question, request.portfolio_id, user_id, db)[
        "valid"
    ]
    if not is_question_valid:
        return {
            "archived": False,
            "summary": "<p>Invalid question. Please ask a relevant investment question.</p>",
        }

    # step 2: Validate the investment objective
    is_objective_clear = await validate_investment_goal(request.question, user_id)[
        "valid"
    ]
    if not is_objective_clear:
        return {
            "archived": False,
            "summary": "<p>Unable to determine your investment objective. Please clarify your investment goals.</p>",
        }

    # step 3: Determine if augmentation is required
    is_augmentation_required = await determine_if_augmentation_required(
        request.question,
        request.portfolio_id,
        db,
        user_id,
    )["additional_data_required"]

    additional_context = {
        "article_summaries": [],
    }
    if is_augmentation_required:
        article_summaries = await retrieve_news(
            request.question,
            request.portfolio_id,
            db,
            user_id,
        )
        additional_context["article_summaries"] = article_summaries

    # step 4: generate advice
    advice = await generate_advice(
        request.question,
        db,
        request.portfolio_id,
        user_id,
        additional_context["article_summaries"] or [],
    )

    await UserSessionManager.update_session(
        user_id=user_id,
        db=db,
        updates={
            "total_prompts_used": UserSessionManager.get_session(user_id)[
                "total_prompts_used"
            ]
            + 1
        },
    )

    return {"archived": True, "summary": convert_markdown_to_html(advice)}
