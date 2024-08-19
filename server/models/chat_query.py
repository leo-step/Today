from pydantic import BaseModel
from typing import List

class ChatQueryInput(BaseModel):
    text: str

class ChatQueryOutput(BaseModel):
    input: str
    output: str
    links: List[str]