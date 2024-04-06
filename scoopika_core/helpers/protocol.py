"""A protocol used to communicate between the core, the server layer, and the client.
to keep things stable in all processing stages."""

from typing import Literal, Dict, Callable


class Protocol:

    def __init__(self, sid: str = "global"):
        self.sid = sid  # session id

    def response(
        self,
        current_status: Literal["done", "waiting", "need", "error", "communicate"],
        next_status: Literal["ready", "waiting"],
        stage: str,
        main_field: str,
        reconnect: bool = False,
        data: dict = {},
    ):

        if main_field not in data.keys():
            raise exception(f"the main field '{main_field}' not found in data payload")

        response = {
            "$": {
                "sid": self.sid,
                "current_status": current_status,
                "next_status": next_status,
                "stage": stage,
                "main_field": main_field,
                "reconnect": reconnect,
            }
        }

        response.update({"data": data})

        return response
