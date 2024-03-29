from typing import Dict, Any


def setup_parameters_schema(parameters: Dict[str, Any]) -> Dict:
    schema = {key: setup_param(key, value) for key, value in parameters.items()}
    return schema


def setup_param(key: str, param_options: Dict) -> Dict:
    if "type" not in param_options:
        param_options["type"] = {"root": "string"}

    if not isinstance(param_options["type"], dict):
        param_options["type"] = {"root": param_options["type"]}

    param_options["id"] = key

    if param_options["type"]["root"] in ["bool", "boolean"]:
        param_options["accept"] = [True, False]
        param_options["description"] += " (one of 'True', 'False')"

    if param_options["type"]["root"].lower() in ["dict", "object", "json"]:
        if "properties" not in param_options:
            return param_options

        param_options["properties"] = {
            nested_key: setup_param(
                f"{key}.{nested_key}", param_options["properties"][nested_key]
            )
            for nested_key in param_options["properties"].keys()
        }

    return param_options
