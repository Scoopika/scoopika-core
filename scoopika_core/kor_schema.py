# Transform a tool config schema to a Kor schema (to use later with arguments selection with an extraction chain)

from typing import Dict, Any, List
from kor.nodes import Object


kor_types = ["Text", "Number"]
kor_types_mappings = {}

kor_types_mappings.update({key.casefold(): kor_types[0] for key in ("string", "str")})
kor_types_mappings.update(
    {key.casefold(): kor_types[1] for key in ("int", "float", "number")}
)


# Build a Kor schema from a tool schema
def build(schema: Dict):
    id = schema["name"]
    description = schema["description"]
    parameters = schema["parameters"]
    examples = [] if "examples" not in schema.keys() else schema["examples"]

    attributes = list(param_to_attr(key, parameters[key]) for key in parameters.keys())
    required = list(
        key
        for key in parameters.keys()
        if "required" in parameters[key] and parameters[key]["required"] is True
    )

    kor_schema = {
        "id": id,
        "description": description,
        "attributes": attributes,
        "required": required,
        "examples": examples,
    }

    return kor_schema


# Create a Kor attribute from a tool parameter
def param_to_attr(param_key: str, param: Dict[str, Any]):
    kor_attr = {"id": param_key}
    if isinstance(param["type"], str):
        param["type"] = {"root": param["type"]}

    param_type = str(param["type"]["root"])

    if param_type in ["array", "list"]:
        if "items" not in param["type"].keys():
            param_type = "string"
        else:
            param_type = param["type"]["items"]
        kor_attr["many"] = True
    else:
        kor_attr["many"] = False

    if param_type in kor_types:
        kor_attr["$type"] = param_type
    elif param_type.lower() in kor_types_mappings.keys():
        kor_attr["$type"] = kor_types_mappings[param_type.lower()]
    elif param_type not in ["dict", "object", "json"]:
        kor_attr["$type"] = "Text"

    if "description" in param:
        kor_attr["description"] = param["description"]

    if "examples" in param:
        kor_attr["examples"] = param["examples"]

    if "null_examples" in param:
        kor_attr["null_examples"] = param["null_examples"]

    if "accept" in param:
        kor_attr["options"] = accept_to_kor_options(param["accept"])

    if "options" in kor_attr.keys() and len(kor_attr["options"]) > 0:
        kor_attr["$type"] = "Selection"

    if (
        param_type.lower() in ["dict", "object", "json"]
        and "properties" in param.keys()
    ):
        nested_attributes = list(
            param_to_attr(key, param["properties"][key])
            for key in param["properties"].keys()
        )
        kor_attr["attributes"] = nested_attributes

    return kor_attr


# Build Kor options from parameter's accepted values
def accept_to_kor_options(accept: List):
    are_str = (
        True
        if len(list(acc for acc in accept if isinstance(acc, str))) == len(accept)
        else False
    )

    if are_str is False:
        return []

    return list({"id": acc, "$type": "Text"} for acc in accept)
