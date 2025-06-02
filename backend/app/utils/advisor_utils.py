import markdown
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_asset_representation, get_exposure_summary, get_portfolio_summary
from fastapi.encoders import jsonable_encoder
from app.utils.advisor_utils import convert_markdown_to_html, preprocess_final_prompt

def preprocess_markdown(markdown_text):
    # Example: Normalize spacing and fix common issues
    markdown_text = markdown_text.strip()
    markdown_text = markdown_text.replace("**;", "**")  # Fix malformed bold syntax
    markdown_text = markdown_text.replace("\n\n", "\n")  # Remove excessive newlines
    return markdown_text


def convert_markdown_to_html(markdown_text):
    markdown_text = preprocess_markdown(markdown_text)  # Preprocess markdown

    html_content = markdown.markdown(markdown_text, extensions=["extra", "smarty"])
    styled_html = f"""
    <html>
        <style>
            ul, ol {{
                margin-left: 30px; /* Indent list items */
            }}
            li {{
                margin-bottom: 10px; /* Add spacing between items */
            }}
            p {{
                margin-left: 10px;
            }}
        </style>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html


async def preprocess_final_prompt(db, portfolio_id, user_id, article_simmaries):

    portfolio = jsonable_encoder(
        await get_portfolio_by_id(db, portfolio_id, user_id)
    )
    portfolio_summary = "\n".join(
        [
            get_asset_representation(portfolio),
            get_portfolio_summary(portfolio),
            get_exposure_summary(portfolio),
        ]
    )

    article_summaries = "\n\n".join(
        [
            "\n".join([article["title"], article["summary"], article["link"]])
            for article in article_simmaries
            if article["summary"] != "Readability extraction failed"
        ]
    )
    return  portfolio_summary, article_summaries
