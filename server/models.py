from pydantic import BaseModel

class ChatQueryInput(BaseModel):
    uuid: str
    session_id: str
    text: str
