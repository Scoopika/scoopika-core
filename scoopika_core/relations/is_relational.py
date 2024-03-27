def is_relational(value):
    if not isinstance(value, dict):
        return False

    return True if "relation" in value.keys() and value["relation"] is True else False
