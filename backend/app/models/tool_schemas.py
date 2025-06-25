# Validation schemas not by the LLM orchestrator loop
validate_prompt_schema = {
    "name": "validate_prompt",
    "description": "Validate if user question is relevant and investment objective is clear.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            # user_id and portfolio_id removed from properties
        },
        "required": ["question"],
    },
}


validate_investment_goal_schema = {
    "name": "validate_investment_goal",
    "description": "Validate user's investment goal clarity.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
        },
        "required": ["question"],
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

determine_tool_schema = {
    "name": "determine_if_augmentation_required",
    "description": "Decide if current news data is needed to answer the investment question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
        },
        "required": ["question"],
    },
}

retrieve_tool_schema = {
    "name": "retrieve_news",
    "description": "Fetch and summarize relevant news articles based on the user's question and portfolio exposure.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
        },
        "required": ["question"],
    },
}


tools = [
    {"type": "function", "function": get_portfolio_tool_schema},
    # {"type": "function", "function": determine_tool_schema},
    {"type": "function", "function": retrieve_tool_schema},
]
