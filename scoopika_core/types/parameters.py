from typing import Dict, Optional, List, Literal, Callable, TypedDict, Any
from enum import Enum
from pydantic import BaseModel, Field
from rich import print_json

class ParameterProperty(BaseModel):
	id: str # The ID of the parameter
	description: Optional[str] # The description of the parameters (recommended)
	type: str | Dict # The type of the parameter (type: string or type: {root: string} or type: {root: list, items: string})
	required: Optional[bool] = False # Whether the parameter is required or not
	ask: Optional[bool] = True # Can the system ask the user about invalid or missing parameters values

	default: Optional[Any] # a default value to fallback to in some cases
	invalid_default_fallback: Optional[bool] = False # Can the system fallback to the default value if LLM output for the parameter is invalid
	missing_default_fallback: Optional[bool] = True # Can the system fallback to the default value if LLM output is missing the parameter

	accept: Optional[List] # A list of the values the parameter's value can be (similar to enum)
	similar_values: Optional[bool] = False # if LLM output does not exist in the list of accpeted value, use similarity model to get the closest one

	important: Optional[bool] = False # If the parameter is important (check for its value as is in the user's input)
	match_context: Optional[bool] = False # If the parameter should appear in the user's context
	only_latest: Optional[bool] = False # check for the parameter value only in the latest user input
	case_sensetive: Optional[bool] = False # if the value is case sensetive
	match_tokens: Optional[List[str]] # what are the exact tokens positions to check for. e.g: ["VERB", "NOUN"]
	as_whole: Optional[bool] = False # Whether to validate lists and dicts as whole (all items), instead validate each item alone

class ParameterSchema(ParameterProperty):
	properties: Optional[Dict[str, ParameterProperty]]