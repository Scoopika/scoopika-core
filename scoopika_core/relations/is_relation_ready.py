def is_relation_ready(relation, completed_args):
    return (
        True
        if len(
            list(target for target in relation["targets"] if target in completed_args)
        )
        == len(relation["targets"])
        else False
    )
