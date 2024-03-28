from typing import Dict, Optional, List, Literal, Callable, TypedDict, Any
from pydantic import BaseModel, Field
from .parameters import ParameterSchema


class PromptTaskInputs(TypedDict):
    key: str
    required: Optional[bool]
    default: Optional[Any]


class TaskSchema(BaseModel):
    name: str
    description: Optional[str]
    type: Literal["function", "prompt"]


class FunctionTaskSchema(TaskSchema):
    type: Literal["function"]
    function: Callable
    parameters: Optional[ParameterSchema]


class PromptTaskSchema(TaskSchema):
    type: Literal["prompt"]
    prompt: str
    inputs: Optional[List[PromptTaskInputs]] = []
