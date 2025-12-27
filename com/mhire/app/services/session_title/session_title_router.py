from fastapi import APIRouter, HTTPException, status
from com.mhire.app.services.session_title.session_title_schema import (
    SessionTitleRequest,
    SessionTitleResponse
)
from com.mhire.app.services.session_title.session_title import session_title_service

router = APIRouter(
    prefix="/api/v1",
    tags=["session_title"]
)

@router.post("/session-title", response_model=SessionTitleResponse)
async def generate_session_title(request: SessionTitleRequest):
    """
    Generate a 3-word session title from chat history
    
    - **history**: List of chat messages with role and content
    
    Returns a 3-word title that summarizes the conversation
    """
    try:
        # Convert Pydantic models to dict for service
        history_dict = [msg.model_dump() for msg in request.history]
        
        # Generate title using Gemini via LangChain
        title = session_title_service.generate_session_title(history_dict)
        
        return SessionTitleResponse(session_title=title)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate session title: {str(e)}"
        )