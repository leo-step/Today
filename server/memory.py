from clients import db_client
from typing import Optional, List
from models import MessageType, ToolInvocation, Message, Conversation
import time

class Memory:
    def __init__(self, uuid, session_id, last_n=6):
        self.uuid = uuid
        self.session_id = session_id
        self.conversations = db_client["conversations"]
        self.last_n = last_n

    def _message_to_str(self, message: Message):
        return f"{message['type']}: {message['content']}"

    def get_messages(self):
        conversation: Conversation = self.conversations.find_one({
            "uuid": self.uuid,
            "session_id": self.session_id
        },
        {
            "messages": {"$slice": -self.last_n}
        })
        if conversation:
            messages: List[Message] = conversation.get("messages", [])
            texts = [self._message_to_str(message) for message in messages]
            return texts
        return []

    def add_message(self, type: MessageType, content: str, tool_use: Optional[ToolInvocation] = None):
        message: Message = {
            "type": type,
            "content": content,
            "tool_use": tool_use,
            "time": int(time.time())
        }
        
        self.conversations.update_one(
            {"uuid": self.uuid, "session_id": self.session_id, "time": int(time.time())},
            {"$push": {"messages": message}},
            upsert=True
        )
