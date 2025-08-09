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
    "description": (
        "Always call this tool before answering if you need any information about "
        "the user's portfolio of assets (asset types, regions, and sectors) for "
        "the selected portfolio. Do not ask the user — fetch it here."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

scrape_news_tool_schema = {
    "name": "retrieve_news",
    "description": (
        "Always call this tool before answering if you need any information about "
        "the the latest news related to the user's portfolio or investment profile for "
        "the selected portfolio. Do not ask the user — fetch it here."
    ),
    
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

get_user_profile_tool_schema = {
    "name": "get_user_profile",
    "description": (
        "Always call this tool before answering if you need any information about "
        "the user's investment profile (investment goals, and asset, sector and regional preferences) for "
        "the selected portfolio. Do not ask the user — fetch it here."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

tools = [
    {"type": "function", "function": get_portfolio_tool_schema},
    {"type": "function", "function": scrape_news_tool_schema},
    {"type": "function", "function": get_user_profile_tool_schema},
]
