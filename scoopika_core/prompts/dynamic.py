from ..types import TaskSchema, FunctionTaskSchema, PromptTaskSchema


def dynamic_prompt(task_schema, inputs):
    """
    Replaces placeholders in a prompt with input values,
    validates required inputs, and returns the updated prompt.
    NOTICE: This code is so bad and was written by AI, but no one gives a shit anyways
    """

    task_schema = PromptTaskSchema(**task_schema).dict()

    try:
        for input_def in task_schema["inputs"]:
            key = input_def["key"]
            if input_def["required"] and key not in inputs:
                if input_def.get("default") is not None:
                    value = input_def["default"]
                    inputs[key] = value
                else:
                    return {"success": False, "error": f"Missing required input: {key}"}

        prompt = task_schema["prompt"]
        for input_def in task_schema["inputs"]:
            key = input_def["key"]
            value = inputs.get(key, input_def.get("default"))
            prompt = prompt.replace(f"<{key}>", str(value))

        return {"success": True, "prompt": prompt}

    except ValueError as e:
        return {"success": False, "error": f"Invalid prompt task: {e}"}
