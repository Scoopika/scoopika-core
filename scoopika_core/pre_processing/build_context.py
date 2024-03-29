"""Build full context from user input and past actions"""

from .join_user_actions import join_user_actions


def build_context(inputs):
    context = ""
    if "user_actions" in inputs:
        context += "\n".join(
            [
                join_user_actions(inputs["user_actions"]),
            ]
        )
        context += "\n"
    if "past_inputs" in inputs:
        context += "\n".join([f"Past user input: {past_input}"])
        context += "\n"
    context += f"Main user input: {inputs['input']}"

    return context
