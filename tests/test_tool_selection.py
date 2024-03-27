import unittest
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from scoopika_core.tool_selection import Selection

load_dotenv()


class Test(unittest.TestCase):

    def test_tool(self):
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

        llm = ChatOpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ.get("TOGETHER_KEY"),
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0,
            max_tokens=2000,
            model_kwargs={"frequency_penalty": 0, "presence_penalty": 0, "top_p": 1.0},
        )

        my_selection = Selection(llm)

        run = my_selection.selection(
            "could you clear the console and then print Hello World and the clear it again",
            test_tools,
        )

        self.assertEqual(run["success"], True)
        self.assertEqual(len(run["tools"]), 1)
        self.assertEqual(run["tools"][0]["name"], "clear")
