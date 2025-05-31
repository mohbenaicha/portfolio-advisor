from typing import List, Dict, Union

def parse_memories(memories: List[Dict[str, Union[str, int]]]) -> str:
    parsed_memories = "\n".join(
        [
            "\n".join(
                [
                    f"date: {memory.date}",
                    f"short_term: {memory.short_term_goal}",
                    f"long_term: {memory.long_term_goal}",
                ]
            )
            for memory in memories if memory is not None
        ]
    )
    return parsed_memories