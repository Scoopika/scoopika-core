# Select a tool to execute given a task

from typing import List, Dict
from .logger import logger
from .pre_processing import join_tools
from .prompts import fill_tool_selection_prompt
from .llm_output import process_llm_json_output
import time


class ToolSelection:

    layer = "tool-selection"
    logs: List[str] = []

    def __init__(
        self, llm, logger=logger, multi_tools: bool = False, verbose: bool = True
    ):
        self.llm = llm
        self.llm.model_kwargs["stop"] = "</json>"
        self.logger = logger
        self.multi_tools = multi_tools
        self.verbose = verbose

    def selection(self, task: str, tools: List):
        start = time.time()
        tools_str = join_tools(
            tools
        )  # Join tools as a string in 'name: description' format

        # Create a filled system prompted with the list of available tools
        system_prompt = fill_tool_selection_prompt(tools_str)
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]

        try:
            llm_output = self.llm.invoke(prompt)
        except (ValueError, TypeError) as e:
            err = f"Can't invoke LLM chain: {e}"
            self.logger(self, err, "error")
            return {"success": False, "error": err}

        llm_output = str(llm_output.content).strip()
        if llm_output.startswith("<json>"):
            llm_output += "</json>"

        # Try to JSON parse the LLM output
        json_llm_output = process_llm_json_output(llm_output)

        success = json_llm_output["success"]

        # JSON parsing failed
        if success is False:
            err = f"Invalid LLM output: '{llm_output.content}'"
            self.logger(self, err, "error")
            return {"success": False, "error": err}

        output_value = json_llm_output["value"]  # The JSON value

        # The model could return a list of selected tools
        if isinstance(output_value, list) and len(output_value) > 0:
            output_value = output_value[0]
        elif isinstance(output_value, list) and len(output_value) == 0:
            return {"success": True, "tools": []}
        elif isinstance(output_value, dict) and len(list(output_value.keys())) < 1:
            return {"success": True, "tools": []}

        wanted_tool = self.wanted_tool_from_output(output_value, tools)

        if wanted_tool["success"] is False:
            return wanted_tool

        selected_tool = wanted_tool["tool"]
        tool_name = selected_tool["name"]

        self.logger(
            self, f"Selected tool: '{tool_name}' in {time.time() - start}s", "success"
        )

        return {
            "success": True,
            "tools": [selected_tool],
        }

    def wanted_tool_from_output(self, out, tools) -> Dict:
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
            return {"success": False, "error": "No tools selected"}

        if result == "not found":
            return {"success": False, "error": "Wanted tool is not available"}

        # Get a tool with the tool's name the model returned
        wanted_tools = list(tool for tool in tools if tool["name"] == result)
        is_valid = True if len(wanted_tools) != 0 else False

        # Tool name not in list
        if is_valid is False:
            err = f"Selected tool does not exist: '{result}'"
            self.logger(self, err, "error")
            return {"success": False}

        return {"success": True, "tool": wanted_tools[0]}


test_tools = [
    {
        "name": "print",
        "description": "print values to the console",
        "parameters": {
            "values": {
                "type": {"root": "array", "items": "string"},
                "description": "The values to print to the console",
            }
        },
    },
    {
        "name": "clear",
        "description": "clear the console output",
        "parameters": {},
    },
]
