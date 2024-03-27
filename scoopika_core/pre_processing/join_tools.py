from typing import List, Dict
from .punct_clean import punct_clean


def join_tools(tools: List[Dict]):
    return list(
        punct_clean(tool["name"]) + ": " + tool["description"] for tool in tools
    )
