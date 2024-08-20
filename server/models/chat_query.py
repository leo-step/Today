from pydantic import BaseModel
from typing import List

class ChatQueryInput(BaseModel):
    text: str

class ChatQueryOutput(BaseModel):
    output: str