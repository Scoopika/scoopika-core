"""Select a tool to execute give a task and a list of available tools"""

from typing import List, Dict
from .prompts import fill_tool_selection_prompt
from .llm_output import process_llm_json_output
from .helpers import fix_llm_stop


class ToolSelectionValidation:

    layer = "tool-selection"
    logs: List[str] = []

    def __init__(self, tools: List[str]):
        self.tools = tools

    def __call__(self, llm_output: str) -> Dict:
        llm_output = str(llm_output).strip()
        llm_output = fix_llm_stop(llm_output, "json")

        # Try to JSON parse the LLM output
        json_llm_output = process_llm_json_output(llm_output)

        success = json_llm_output["success"]

        # JSON parsing failed
        if success is False:
            err = f"Invalid LLM output: '{llm_output}'"
            return {"success": False, "errors": [err]}

        output_value = json_llm_output["value"]  # The JSON value

        # The model could return a list of selected tools
        if isinstance(output_value, list) and len(output_value) > 0:
            output_value = output_value[0]
        elif isinstance(output_value, list) and len(output_value) == 0:
            return {"success": False, "errors": ["No tools selected"]}
        elif isinstance(output_value, dict) and len(list(output_value.keys())) == 0:
            return {"success": False, "errors": ["No tools selected"]}

        wanted_tool = self.wanted_tool_from_output(output_value)

        if wanted_tool["success"] is False:
            return wanted_tool

        selected_tool = wanted_tool["tool"]

        return {
            "success": True,
            "tools": [selected_tool],
        }

    def wanted_tool_from_output(self, out) -> Dict:
        # if the model returned only the tool's name as string
        if isinstance(out, str):
            out = {"name": out}

        # in this case the model output is invalid
        if not isinstance(out, dict):
            return {"success": False}

        # Try to get the tool's name from the model JSON output
        if "name" in out:
            result = out["name"]
        elif len(out.keys()) > 0:
            result = out[list(out.keys())[0]]
        else:
            return {
                "success": False
            }  # In case of empty JSON, like: '{}', then nothing is selected

        if result == "none":
            return {"success": False, "errors": ["No tools selected"]}

        if result == "not found":
            return {"success": False, "errors": ["Wanted tool is not available"]}

        # Get a tool with the tool's name the model returned
        tools = self.tools
        wanted_tools = list(tool for tool in tools if tool == result)
        is_valid = True if len(wanted_tools) != 0 else False

        # Tool name not in list
        if is_valid is False:
            err = f"Selected tool does not exist: '{result}'"
            return {"success": False, "errors": [err]}

        return {"success": True, "tool": wanted_tools[0]}
