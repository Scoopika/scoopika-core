"""A protocol used to communicate between the core, the server layer, and the client.
to keep things stable in all processing stages."""

from typing import Literal, Dict, Callable


class Protocol:

    def __init__(self, rid: str, sid: str):
        self.rid = rid # request id
        self.sid = sid # session id

    def response(
        current_status: literal["done", "waiting", "need", "error", "communicate"],
        next_status: literal["ready", "waiting"],
        stage: str,
        main_field: str,
        reconnect: bool,
        more: dict = {}
    ):

        if main_field not in more.keys():
            raise exception(f"the main field '{main_field}' not found in data payload")

        response = {
            "$": {
                "rid": self.rid,
                "sid": self.sid,
                "current_status": current_status,
                "next_status": next_status,
                "stage": stage,
                "main_field": main_field,
                "reconnect": reconnect
            }
        }

        response.update(more)

        return response
