from typing import List, Dict


def join_user_actions(actions: List[Dict[str, str]]):
    return "\n".join(list(f"user action: {action}." for action in actions))
