import requests
from random import choice
from app.core.prompt_logic import handle_prompt

async def test_handle_prompt_with_real_data():
    question = "How does the market news and sentiment affect my portfolio?"
    response = requests.get("http://localhost:8000/portfolios")
    selected_portfolio = choice(response.json())

    summary = {
        "asset_names": [a["name"] for a in selected_portfolio["assets"]],
        "asset_types": list({a["asset_type"] for a in selected_portfolio["assets"]}),
        "sectors": list({a["sector"] for a in selected_portfolio["assets"]}),
        "regions": list({a["region"] for a in selected_portfolio["assets"]}),
    }

    prompt_request = type("PromptRequest", (), {
        "question": question,
        "portfolio_summary": summary
    })()
    
    result = await handle_prompt(prompt_request)
    print(result)


