import requests
from random import choice
from app.core.prompt_logic import handle_prompt

async def test_handle_prompt_with_real_data():
    question = "How does the market news and sentiment affect my portfolio?"
    # response = requests.get("http://localhost:8000/portfolios")
    # if response.status_code == 200:
    #     portfolios = response.json()
    #     print("Portoflios: \n", portfolios)
    #     if portfolios:
    #         selected_portfolio = choice(portfolios)  # Pick a random portfolio
    #         summary = "\n".join([get_portfolio_summary(selected_portfolio), get_exposure_summary(selected_portfolio)])
    #     else:
    #         print("No portfolios available to select.")
    #         summary = {}
    #         return
    # else:
    #     print(f"Failed to fetch portfolios: {response.status_code}")
    #     summary = {}
    #     return


    prompt_request = type("PromptRequest", (), {
        "question": question,
        "portfolio_id": choice([1,2,3])
    })()
    
    result = await handle_prompt(prompt_request)
    


