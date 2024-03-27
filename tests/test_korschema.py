import unittest
from scoopika_core import kor_schema


class Test(unittest.TestCase):
    def test_kor_schema_build(self):

        schema = {
            "name": "test",
            "description": "this is a test",
            "parameters": {
                "id": {
                    "type": {"root": "string"},
                    "description": "The user ID",
                    "required": True,
                },
                "action": {
                    "type": {"root": "array", "items": "string"},
                    "description": "The user action",
                    "accept": ["idle", "playing", "looking_for_game"],
                    "default": "idle",
                },
                "documents": {
                    "type": {"root": "array", "items": "object"},
                    "description": "The user wanted documents",
                    "parameters": {
                        "id": {
                            "type": "string",
                            "description": "The document ID",
                            "required": True,
                        }
                    },
                },
            },
        }

        schema = kor_schema.build(schema)

        self.assertEqual(len(schema["attributes"]), 3)
        self.assertEqual(schema["attributes"][0]["$type"], "Text")
