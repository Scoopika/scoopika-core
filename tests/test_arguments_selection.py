import unittest
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from scoopika_core.arguments_selection import ArgumentsSelection

load_dotenv()


class Test(unittest.TestCase):

    def test_args(self):

        test_tool = {
            "name": "search-song",
            "description": "search for songs or artists",
            "parameters": {
                "app": {
                    "type": "string",
                    "description": "The app to use to search for results",
                    "match_context": True,
                    "accept": ["spotify", "youtube"],
                    "ask": True,
                    "invalid_default_fallback": False,
                    "missing_default_fallback": False,
                    "default": "youtube",
                    "required": True,
                },
                "title": {
                    "description": "the song title or name (not required)",
                    "type": "string",
                    "required": False,
                },
                "artists": {
                    "description": "The artists of the song",
                    "type": {"root": "array", "items": "string"},
                    "required": False,
                },
                "query": {
                    "description": "The search query",
                    "type": "string",
                    "required": True,
                },
                "order": {
                    "description": "The order to sort search results based on",
                    "type": {"root": "object"},
                    "required": True,
                    "properties": {
                        "field": {
                            "description": "The field to sort results based on",
                            "type": "string",
                            "required": True,
                            "accept": ["views", "date"],
                            "default": "views",
                        },
                        "descending": {
                            "description": "Whether to sort results in descending order or not",
                            "type": "bool",
                            "required": True,
                            "default": True,
                        },
                    },
                },
            },
            "examples": [
                [
                    "Main user input: Look up Hotel California by The Eagles",
                    {
                        "title": "Hotel California",
                        "artists": ["The Eagles"],
                        "query": "Hotel California by The Eagles",
                    },
                ],
                [
                    "Main user input: Search for recent songs by Metallica",
                    {
                        "artists": ["Metallica"],
                        "query": "songs by Metallica",
                        "order": {"field": "date", "descending": True},
                    },
                ],
                [
                    "Main user input: Search for most viewed songs by Queen",
                    {
                        "artists": ["Queen"],
                        "query": "songs by Queen",
                        "order": {"field": "views", "descending": True},
                    },
                ],
            ],
        }

        llm = ChatOpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ.get("TOGETHER_KEY"),
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0,
            max_tokens=2000,
            model_kwargs={"frequency_penalty": 0, "presence_penalty": 0, "top_p": 1.0},
        )

        inputs = {
            "input": "Look up most viewed songs made by The Eagles",
        }

        args_selection = ArgumentsSelection(llm, inputs, test_tool)
        selection = args_selection.selection()
        print(selection)
