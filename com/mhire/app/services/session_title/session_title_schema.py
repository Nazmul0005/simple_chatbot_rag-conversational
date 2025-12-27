from pydantic import BaseModel, Field
from typing import List, Literal

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class SessionTitleRequest(BaseModel):
    history: List[Message] = Field(..., min_length=1, description="Chat history messages")

class SessionTitleResponse(BaseModel):
    session_title: str = Field(..., description="3-word session title")