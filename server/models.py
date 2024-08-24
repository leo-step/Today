from pydantic import BaseModel
from enum import Enum
from typing import TypedDict, List

# ========= SERVER I/O ========= #

class ChatQueryInput(BaseModel):
    uuid: str
    session_id: str
    text: str

# ========= TOOLS ========= #

class Tool(Enum):
    CRAWL = "crawl"
    EMAILS = "emails"
    NONE = None

class ToolDetails(TypedDict):
    name: Tool
    description: str

Tools = List[ToolDetails]

# ========= MEMORY ========= #

class MessageType(Enum):
    HUMAN = "human"
    AI = "ai"

class ToolInvocation(TypedDict):
    tool: Tool
    input: str
    output: str
