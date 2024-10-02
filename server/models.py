from pydantic import BaseModel
from enum import Enum
from typing import TypedDict, List, Optional, Any

# ========= SERVER I/O ========= #

class Event(BaseModel):
    uuid: str
    event: str
    properties: Any

class ChatQueryInput(BaseModel):
    uuid: str
    session_id: str
    text: str

# ========= TOOLS ========= #

class Tool(Enum):
    CRAWL = "crawl"
    EMAILS = "emails"
    ALL_EMAILS = "allemails"
    LOCATION = "location"
    COURSES = "courses"
    CATCHALL = "catchall"
    WIDGET_DATA = "widgetdata"
    EATING_CLUBS = "eatingclubs"
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

class Message(TypedDict):
    type: str
    content: str
    tool_use: Optional[ToolInvocation]
    time: int

class Conversation(TypedDict):
    uuid: str
    session_id: str
    time: int
    messages: List[Message]
