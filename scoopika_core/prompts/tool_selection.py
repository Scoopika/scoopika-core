from typing import List


system_prompt = """You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:

<tools>

Given the user input, return the name of the tool to use.
If no tool needs to be used or no tool exist in the tools list repond with 'not found'.
Return your response as a JSON blob with 'name' key wrapped inside <json> tags.

Example: <json>{"name": "tool name"}</json>."""


def fill_tool_selection_prompt(tools: List[str]):
    this_prompt = str(system_prompt)
    this_prompt = this_prompt.replace("<tools>", "\n".join(tools))

    return this_prompt
