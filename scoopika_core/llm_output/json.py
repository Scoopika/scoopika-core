import re
import json


def process_llm_json_output(output: str):
    json_tags_match = re.search(r"<json>(.*?)</json>", output, re.DOTALL)
    if json_tags_match:
        output = json_tags_match.group(1)
        try:
            output = json.loads(output)
            return {"success": True, "value": output}
        except:
            return {"success": False}

    try:
        output = JsonOutputParser(output)
        return {"success": True, "value": output}
    except:
        return {"success": False}
