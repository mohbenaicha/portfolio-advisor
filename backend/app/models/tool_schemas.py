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

prepare_advice_template_schema = {
    "name": "prepare_advice_template",
    "description": "Build a complete prompt that summarizes the user's investment context and question for final advice generation.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "article_summaries": {
                "type": "array",
                "description": "List of summarized news articles.",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "source": {"type": "string"},
                        "link": {"type": "string"},
                        "posted": {"type": "string", "format": "date-time"},
                    },
                    "required": ["title", "summary"],
                },
            },
        },
        "required": ["question", "article_summaries"],
    },
}

tools = [

    {"type": "function", "function": determine_tool_schema},
    {"type": "function", "function": retrieve_tool_schema},
    # {"type": "function", "function": prepare_advice_template_schema}, # deprecated, will be removed in future PRs
]
