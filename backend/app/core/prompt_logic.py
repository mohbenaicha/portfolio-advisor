from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from app.services.openai_client import extract_entities, generate_advice
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.db.mongo import get_cached_articles, store_article_summaries
from app.db.user_session import UserSessionManager
from app.utils.portfolio_utils import get_asset_representation
from app.utils.article_scraper import extract_with_readability
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

    # 1: Prompt 1 > extract asset_types, sectors, regions, themes, keywords
    print(
        "------------------------ Extracting Entities using GPT-4o -------------------------------------------"
    )
    entities, portfolio, portfolio_summary = await extract_entities(
        question=request.question,
        portfolio_id=request.portfolio_id,
        db=db,
        user_id=user_id,
    )  # portfolio summary does not have detailed asset breakdown

    if entities["valid"] == "no":
        return {
            "archived": False,
            "summary": "<p>Invalid question. Please ask a relevant investment question.</p>",
        }

    if db is None or user_id is None:
        raise ValueError(
            "error in prompt_logic.py/handle_prompt: Database session or user id is missing"
        )

    # add latest llm memory to db and update session
    if entities["short_term_objective"] != "" or entities["long_term_objective"] != "":
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={
                "llm_memory": {
                    "short_term": entities["short_term_objective"],
                    "long_term": entities["long_term_objective"],
                    "portfolio_id": request.portfolio_id,
                }
            },
        )
    print(
        "------------------------ Entities Extracted -------------------------------------------"
    )
    print("Entities: \n", entities)
    print("short_term_objective: \n", entities["short_term_objective"])
    print("long_term_objective: \n", entities["long_term_objective"])
    print("Sessions: \n", UserSessionManager.get_session(user_id))
    # 2: Check MongoDB for recent summaries
    start_date = datetime.now(timezone.utc) - timedelta(days=8)
    end_date = datetime.now(timezone.utc)

    print(
        "------------------------ Looking for Cached Articles -------------------------------------------"
    )
    # keys: link, posted (date published), query, query_tags, source (publisher), stored_at (d/t), summary, title
    cached_articles = await get_cached_articles(
        entities["entities"], start_date=start_date, end_date=end_date
    )
    print("Found {} chached acicles".format(len(cached_articles)))

    if len(cached_articles) < 10:
        print(
            "------------------------ Fetching Articles from Google Search News -------------------------------------------"
        )

        # 3: Fetch articles from Alpha Vantage
        # list of dicts; keys: query, position, title, body, posted, source, link
        fresh_articles = await fetch_articles(entities["entities"])

        # 4: Scrape full article content using readability
        print(
            "------------------------ Extracting Article Content -------------------------------------------"
        )
        for article in fresh_articles:
            # key added added to each article dict: raw_article - full scraped article content
            try:
                article["raw_article"] = await extract_with_readability(article["link"])
            except Exception as e:
                print(f"Error extracting article content: {e}")
                article["raw_article"] = "Readability extraction failed."

        print("Starting to summarize articles...")
        # 5: Summarize articles using LangChain (Prompt 2 - multiple requests to open ai)
        # key added: summary - summarized version of each article by GPT-4o
        print(
            "------------------------ Summarizing Articles -------------------------------------------"
        )
        summarized = await summarize_articles(fresh_articles)

        print("Summarized articles:", summarized)
        print(
            "------------------------ Storing Articles -------------------------------------------"
        )
        # 6: Cache summaries in MongoDB
        await store_article_summaries(summarized)
    else:
        summarized = cached_articles
    print(
        "|--------------------------------------Finished fetching and summarizing articles.--------- -------------------|"
    )

    print(
        "------------------------ Generating Final Advice -------------------------------------------"
    )
    # 7: Prompt 3 > generate advice using gpt-4o-mini

    portfolio_summary = "\n".join(
        [get_asset_representation(portfolio), portfolio_summary]
    )
    article_summaries = "\n\n".join(
        [
            "\n".join([article["title"], article["summary"], article["link"]])
            for article in summarized
            if article["summary"] != "Readability extraction failed"
        ]
    )

    print(
        "------------------------ Generating Final Advice -------------------------------------------"
    )
    advice = await generate_advice(
        request.question, portfolio_summary, article_summaries, user_id
    )
    print("Advice:::::\n\n\n", advice)
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


#     return {
#         "archived": True,
#         "summary": convert_markdown_to_html(
#             """
# ## 1‑Sentence Answer – the punch line.
# Shift from current tech exposure in AAPL and options to a diversified portfolio of US-focused renewable energy equities and ETFs, emphasizing grid modernization, offshore wind, and solar sectors supported by robust policy and infrastructure investments.

# ## Portfolio Impact Analysis
# Your current portfolio is 100% concentrated in US technology through Apple stock and options, with no exposure to renewables. Recent news underscores accelerated investments in US grid upgrades (Avangrid), large-scale offshore wind projects (Empire Wind), and risks from potential federal budget cuts threatening tax credits that underpin solar and storage growth. The US market remains a critical growth arena for renewables amid strong policy and private capital flows, but volatility in federal support necessitates diversification within green-energy sub-sectors and consideration of infrastructure-related firms.

# ## Recommendations (Numbered)
# 1. **Liquidate Apple stock and call options fully; reallocate 100% to renewable energy ETFs within 1 month.** Use funds to build a concentrated exposure to sector thematic ETFs like iShares Global Clean Energy ETF (ICLN) or Invesco Solar ETF (TAN) to gain diversified, immediate exposure to US and global renewables.
# 2. **Add 20% allocation to US grid infrastructure firms (e.g., Avangrid, NextEra Energy),** reflecting the $20B grid modernization plan and ongoing investment in grid resiliency and capacity. Hold >1 year.
# 3. **Invest 15-20% in offshore wind developers/operators (e.g., Equinor, Orsted),** capitalizing on Empire Wind project resumption and US offshore wind growth potential. Medium to long-term hold (2-3 years).
# 4. **Allocate 10-15% to high-growth US solar and energy storage companies,** balancing exposure to manufacturing and technology innovation, mindful of legislative risks to tax credits. Medium term hold (1-3 years).
# 5. **Maintain 10-15% in emerging green hydrogen and energy storage-focused funds or companies,** to capture longer-term innovation-driven returns and diversify sub-sector risk. Long-term hold (3-5 years).

# ## Key Risks & Unknowns
# - Potential rollback of US clean energy tax credits threatens solar/storage growth and manufacturing.
# - Regulatory and permitting delays for offshore wind or grid upgrades could impact project timelines.
# - Political risk in state/federal energy funding and infrastructure spending.
# - Market volatility in renewable sectors due to policy or commodity price cycles.
# - Exposure to global supply chain constraints affecting renewable tech manufacturing.

# ## Confidence (0‑100%)
# 85% – Strong empirical support from recent infrastructure investments, project restarts, and sector policy dynamics; however, federal policy uncertainty tempers conviction.

# ## References & Assumptions
# - Assumes US policy remains broadly supportive despite potential budget bill threats (solar tax credits critical).
# - Leverages details on Avangrid’s grid investment and Empire Wind offshore project progress as tangible opportunities.
# - Assumes ETFs like ICLN and TAN offer immediate diversification and liquidity to replace Apple exposure.
# - Assumes portfolio size and liquidity allow full rollover within 1 month without significant market impact.

# ## Citations
# - “Avangrid Commits $41 Million To Rebuild New York’s Outdated Grid Infrastructure,” SolarQuarter
# - “Empire Wind project proceeds as United States lifts stop work order,” Daily Energy Insider
# - “Budget bill could block renewable energy boost to U.S. economy,” Solar Builder Mag
# - “Powering The Global Energy Transition,” Global Finance Magazine
# - “State Funding and Financing Strategies for Advancing Energy Projects,” NGA.org
#             """
#         )
#     }
