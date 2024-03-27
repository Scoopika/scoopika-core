# LLM Configurations.

from typing import Optional, Dict
from pydantic import BaseModel, Field


class Model_conf(BaseModel):
    base_url: Optional[str] = Field(default="https://api.together.xyz/v1")
    api_key: str = None
    model: Optional[str] = Field(default="mistralai/Mixtral-8x7B-Instruct-v0.1")
    temperature: Optional[int] = Field(default=0)
    max_tokens: Optional[int] = Field(default=2000)
    model_kwargs: Optional[Dict[str, float]] = Field(
        default={"frequency_penalty": 0, "presence_penalty": 0, "top_p": 1.0}
    )
