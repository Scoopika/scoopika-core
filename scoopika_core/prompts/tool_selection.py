from typing import List


system_prompt = """You are an AI agent that has access to the following set of tools:

<tools>

Your role is to choose the name of the tool to use in order to achieve the user request.
Maybe the user does not have a task, in that case just respond with "none".
If the user has a request but it can't be done using the tools you have repond with "not found".

Return your response as a JSON blob with 'name' key wrapped inside <json> tags.

Example if selected a tool: <json>{"name": "tool name"}</json>.
Example if did not select a tool: <json>{"name": "none"}</json>"""


def fill_tool_selection_prompt(tools: List[str]):
    this_prompt = str(system_prompt)
    this_prompt = this_prompt.replace("<tools>", "\n".join(tools))

    return this_prompt
