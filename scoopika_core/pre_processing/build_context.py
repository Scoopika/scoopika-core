# ----- Build full context from user input and past actions
def build_context(inputs):
    context = ""
    if "user_actions" in inputs:
        context += "\n".join(
            [
                join_user_actions(inputs["user_actions"]),
            ]
        )
        context += "\n"
    context += f"Main user input: {inputs['input']}"

    return context
