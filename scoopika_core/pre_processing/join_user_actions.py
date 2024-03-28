from typing import List, Dict


def join_user_actions(actions: List[str]):
    return "\n".join(list(f"Past user action: {action}." for action in actions))
