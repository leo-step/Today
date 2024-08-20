from pydantic import BaseModel
from typing import List

class ChatQueryInput(BaseModel):
    uuid: str
    session_id: str
    text: str
