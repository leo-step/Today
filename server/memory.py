from enum import Enum

class MessageType(Enum):
    HUMAN = "human"
    AI = "ai"

class Memory:
    def __init__(self, uuid, session_id):
        self.uuid = uuid
        self.session_id = session_id

    def get_messages(self):
        pass

    def add_message(self, type: MessageType, content: str):
        pass


'''
document = {
        'uuid': query.uuid,
        'session_id': query.session_id,
        # 'time': int(time.time())
    }
    update_fields = {
        '$set': document
    }
    
    # for i in range(100):
    #     start_time = time.time()
    user_conversations.update_one(document, update_fields, upsert=True)
        # end_time = time.time()
        # print(end_time-start_time)

    # TODO: ignore mongo for now

'''