from collections import defaultdict

session_store = defaultdict(
    lambda: {"llm_memory": [], "timestamp": None, "total_prompts_used": 0}
)  # Key: user_id, Value: {"llm_memory": ..., "timestamp": ..., "total_prompts_used": ...}
