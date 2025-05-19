import requests
from random import choice
from app.core.prompt_logic import handle_prompt

async def test_handle_prompt_with_real_data():
    question = "How does the market news and sentiment affect my portfolio?"

    prompt_request = type("PromptRequest", (), {
        "question": question,
        "portfolio_id": 1#choice([1,2,3])
    })()
    
    result = await handle_prompt(prompt_request)

    print("-------------------------- OPEN AI's response -------------------------------------------")
    print(result["summary"])
    


