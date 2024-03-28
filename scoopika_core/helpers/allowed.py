from typing import Dict


# ----- Check if a bool option is not allowed in options (set to False)
def is_notallowed(options: Dict, key: str) -> bool:
    return True if key in options and options[key] is False else False


# ----- Check if a bool option is allowed in options
def is_allowed(options: Dict, key: str) -> bool:
    return True if key in options and options[key] is True else False
