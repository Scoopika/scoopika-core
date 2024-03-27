# ----- Build full context from user input, actions, and more...
def build_context(inputs):
    context = ""
    if "user_actions" in inputs:
        context += "\n".join(
            [
                "Recent user actions (use if needed to extract data):",
                join_user_actions(inputs["user_actions"]),
            ]
        )
        context += "\n"
    context += f"Main user input: {inputs['input']}"

    return context