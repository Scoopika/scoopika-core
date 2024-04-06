def fix_llm_stop(value: str, keyword: str):
    if value.startswith(f"<{keyword}>"):
        value += f"</{keyword}>"
    elif f"<{keyword}>" in value:
        value += f"</{keyword}>"

    return value
