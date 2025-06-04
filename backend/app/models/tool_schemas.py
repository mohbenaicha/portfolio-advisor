determine_tool_schema = {
    "name": "determine_if_augmentation_required",
    "description": "Decide if current news data is needed to answer the investment question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The user's investment question.",
            },
            "portfolio_id": {
                "type": "integer",
                "description": "The user's portfolio ID.",
            },
            "user_id": {"type": "integer", "description": "The user's ID."},
        },
        "required": ["question", "portfolio_id", "user_id"],
    },
}

retrieve_tool_schema = {
    "name": "retrieve_news",
    "description": "Fetch and summarize relevant news articles based on the user's question and portfolio exposure.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The user's investment question.",
            },
            "portfolio_id": {
                "type": "integer",
                "description": "The user's portfolio ID.",
            },
            "user_id": {"type": "integer", "description": "The user's ID."},
        },
        "required": ["question", "portfolio_id", "user_id"],
    },
}
prepare_advice_prompt_schema = {
    "name": "prepare_advice_prompt",
    "description": "Build a complete prompt that summarizes the user's investment context and question for final advice generation.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The user's investment question.",
            },
            "portfolio_id": {
                "type": "integer",
                "description": "The user's portfolio ID.",
            },
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
        "required": ["question", "portfolio_summary", "objectives"],
    },
}

tools = [
    {"type": "function", "function": determine_tool_schema},
    {"type": "function", "function": retrieve_tool_schema},
    {"type": "function", "function": prepare_advice_prompt_schema},
]
