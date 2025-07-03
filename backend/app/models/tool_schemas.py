# Validation schemas not by the LLM orchestrator loop
validate_prompt_schema = {
    "name": "validate_prompt",
    "description": "Validate if user question is relevant and investment objective is clear.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


# Tool schemas for the LLM orchestrator
get_portfolio_tool_schema = {
    "name": "get_user_portfolio",
    "description": "Retrieve the user's portfolio for reference when providing investment advice.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

scrape_news_tool_schema = {
    "name": "retrieve_news",
    "description": "Fetch and summarize relevant news articles based on the user's question and portfolio exposure.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

get_user_profiles_tool_schema = {
    "name": "get_user_profiles",
    "description": "Return a text summary of the user's investment profile for a selected portfolio, including both the specific profile and the 'All Portfolios' profile, with reconciliation logic if they conflict.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

tools = [
    {"type": "function", "function": get_portfolio_tool_schema},
    {"type": "function", "function": scrape_news_tool_schema},
    {"type": "function", "function": get_user_profiles_tool_schema},
]
