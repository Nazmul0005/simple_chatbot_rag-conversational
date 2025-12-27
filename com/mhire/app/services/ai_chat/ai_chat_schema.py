from pydantic import BaseModel, field_validator
from typing import List, Optional
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_schema_logger()

class MessageHistory(BaseModel):
    role: str
    content: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            error_msg = "Role must be either 'user' or 'assistant'"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v

class AIChatRequest(BaseModel):
    query: str
    history: Optional[List[MessageHistory]] = []
    
    @field_validator('query')
    @classmethod
    def validate_not_empty(cls, v):
        try:
            if not v or not v.strip():
                error_msg = "query cannot be empty"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug(f"Validated query: {v[:50]}...")
            return v
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

class AIChatResponse(BaseModel):
    query: str
    response: str
    
    def __init__(self, **data):
        try:
            super().__init__(**data)
            logger.debug(f"AIChatResponse created for query: {self.query[:50]}...")
        except Exception as e:
            error_msg = f"Failed to create AIChatResponse: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise