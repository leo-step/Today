from pydantic import BaseModel

class ChatQueryInput(BaseModel):
    text: str

class ChatQueryOutput(BaseModel):
    input: str
    output: str