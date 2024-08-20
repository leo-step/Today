from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from pymongo import errors
from typing import List
import logging
import time
import json

logger = logging.getLogger(__name__)

MAX_DOCUMENTS = 5

class MongoDBConversationMemory(MongoDBChatMessageHistory):
    @property
    def messages(self) -> List[BaseMessage]:
        try:
            cursor = self.collection.find({self.session_id_key: self.session_id}).sort("time", -1).limit(MAX_DOCUMENTS)
        except errors.OperationFailure as error:
            logger.error(error)

        if cursor:
            items = [json.loads(document[self.history_key]) for document in cursor][::-1]
        else:
            items = []

        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        try:
            self.collection.insert_one(
                {
                    self.session_id_key: self.session_id,
                    self.history_key: json.dumps(message_to_dict(message)),
                    "time": int(time.time())
                }
            )
        except errors.WriteError as err:
            logger.error(err)
