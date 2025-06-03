# core/tool_function_map.py
from app.services.openai_client import (
    determine_if_augmentation_required,
    retrieve_news,
    generate_advice,
)

TOOL_FUNCTION_MAP = {
    "determine_if_augmentation_required": determine_if_augmentation_required,
    "retrieve_news": retrieve_news,
    "generate_advice": generate_advice,
}
