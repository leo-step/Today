from pydantic import BaseModel

class SingleTextInput(BaseModel):
    input: str
