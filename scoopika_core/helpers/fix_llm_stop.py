
def fis_llm_stop(value: str, keyword: str):
    if value.startswith(f"<{keyword}>"):
        value += f"</{keyword}>"

    return value

