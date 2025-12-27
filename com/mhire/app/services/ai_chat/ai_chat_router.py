from fastapi import APIRouter, HTTPException
from com.mhire.app.services.ai_chat.ai_chat import process_ai_chat
from com.mhire.app.services.ai_chat.ai_chat_schema import AIChatRequest, AIChatResponse
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_router_logger()

router = APIRouter(prefix="/api/v1", tags=["AI_Chat"])

@router.post("/ai_chat", response_model=AIChatResponse)
async def ai_chat_endpoint(request: AIChatRequest):
    """
    AI Chat endpoint that processes user query with provided conversation history
    
    Parameters:
    - query: User's current question/message (required)
    - history: Conversation history as a list of messages (optional)
    
    Returns:
    - query: The user's query
    - response: AI generated response
    
    Note: This endpoint does NOT perform any database operations.
    """
    try:
        logger.info(f"AI chat endpoint called")
        logger.debug(f"Query: {request.query}")
        logger.debug(f"History length: {len(request.history)}")
        
        result = await process_ai_chat(request)
        
        logger.info(f"AI chat endpoint completed successfully")
        return result
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error processing AI chat: {error_str}", exc_info=True)
        
        # Custom error messages for specific errors
        if "API_KEY_INVALID" in error_str or "API key not valid" in error_str:
            raise HTTPException(
                status_code=500, 
                detail="AI service configuration error. Please contact support."
            )
        elif "quota" in error_str.lower() or "rate limit" in error_str.lower():
            raise HTTPException(
                status_code=429, 
                detail="Service temporarily unavailable. Please try again later."
            )
        elif "timeout" in error_str.lower():
            raise HTTPException(
                status_code=504, 
                detail="Request timeout. Please try again."
            )
        else:
            # Generic error for unknown issues
            raise HTTPException(
                status_code=500, 
                detail="Unable to process your request. Please try again later."
            )