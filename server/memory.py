from clients import db_client
from typing import Optional
from models import MessageType, ToolInvocation
import time

class Memory:
    def __init__(self, uuid, session_id):
        self.uuid = uuid
        self.session_id = session_id
        self.conversations = db_client["conversations"]

    def get_messages(self):
        conversation = self.conversations.find_one({
            "uuid": self.uuid,
            "session_id": self.session_id
        })
        if conversation:
            return conversation.get("messages", [])
        return []

    def add_message(self, type: MessageType, content: str, tool_use: Optional[ToolInvocation] = None):
        message = {
            "type": type.value,
            "content": content,
            "tool_use": tool_use,
            "timestamp": int(time.time())
        }
        
        self.conversations.update_one(
            {"uuid": self.uuid, "session_id": self.session_id},
            {"$push": {"messages": message}},
            upsert=True
        )
