from .prompts import dynamic_prompt
from .llm_output import process_llm_json_output 


prompt = """You are an agent to help an AI system with some tool's inputs.

The AI system has a tool's arguments, but the exact user input does not exist in the list of accepted values.
If one of the accepted values can represent what the user means, respond with the accepted value, otherwise respond with INVALID.

Respond with a JSON blob with 'result' key wrapped in <json> tags.

Examples:
<json>{"result": "INVALID"}</json>
<json>{"result": "the accepted value"}</json>

The data is about <about>."""

task = {
    "name": "accepted",
    "description": "get accepted value based on input",
    "type": "prompt",
    "prompt": prompt,
    "inputs": [
        {
            {"key": "about", "required": True},
        }
    ]
}

def get_accepted(llm, input, accepted_values, about):
    this_prompt = dynamic_prompt(task, {"about": about})

    if this_prompt["success"] is False:
        return this_prompt

    try:
        output = llm.onvoke([
            {"role": "system", "content": this_prompt},
            {"role": "user", "content": f"Input: {str(input)}\nAccepted values: {str(accepted_values)}"}
        ])

        json_llm_output = process_llm_json_output(str(output.content))

        if json_llm_output["success"] is False:
            return {"success": False, "error": f"Invalid LLM output: {str(output.content)}"}

        json_llm_output = json_llm_output["value"]

        return {"success": True, "value": json_llm_output}

    except (Exception, ValueError, TypeError) as e:
        return {"success": False, "error": f"Unable to process accepted value: {e}"}
