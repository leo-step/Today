from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory.buffer import ConversationBufferMemory
from langchain_core.agents import AgentAction
from langchain.memory.utils import get_prompt_input_key
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from pymongo import errors
from typing import List, Dict, Any, Tuple
import logging
import time
import json
import pymongo
import os

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
            items = [json.loads(document[self.history_key]) for document in cursor][::-1] # is this right?
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


class ChatMemoryWithIntermediates(ConversationBufferMemory):
    def _save_intermediates_to_mongo(self, actions: List[Tuple[AgentAction, str]]):
        client = pymongo.MongoClient(os.getenv("MONGO_CONN"))
        collection = client["today"]["intermediate_steps"]
        data = []
        for action in actions:
            agent_action, output = action[0], action[1]
            agent_action = agent_action.to_json()
            data.append({
                "tool": agent_action["kwargs"]["tool"],
                "tool_input": agent_action["kwargs"]["tool_input"],
                "tool_output": output["result"]
            })
        document = {
            'session_id': self.chat_memory.session_id,
            'actions': data
        }
        collection.insert_one(document)

    def _get_input_output(
        self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> Tuple[str, str]:
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) == 1:
                output_key = list(outputs.keys())[0]
            elif "output" in outputs:
                output_key = "output"
                intermediate_steps_key = "intermediate_steps"
                self._save_intermediates_to_mongo(outputs[intermediate_steps_key])
                # warnings.warn(
                #     f"'{self.__class__.__name__}' got multiple output keys:"
                #     f" {outputs.keys()}. The default 'output' key is being used."
                #     f" If this is not desired, please manually set 'output_key'."
                # )
            else:
                raise ValueError(
                    f"Got multiple output keys: {outputs.keys()}, cannot "
                    f"determine which to store in memory. Please set the "
                    f"'output_key' explicitly."
                )
        else:
            output_key = self.output_key
        return inputs[prompt_input_key], outputs[output_key]
