from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from com.mhire.app.services.ai_chat.ai_chat_router import router as ai_chat_router  # NEW
from com.mhire.app.services.session_title.session_title_router import router as session_title_router

# Initialize FastAPI
app = FastAPI(title="Gemini Chatbot API")

# Global exception handler for 422 validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle all 422 validation errors globally with custom message"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request format. Please check your input and try again."
        }
    )


# Include routers
app.include_router(ai_chat_router)  
app.include_router(session_title_router)


@app.get("/")
async def root():
    return {
        "message": "Sora Chatbot API with Long-term Memory",
        "endpoints": {
            "ai_chat": "POST /api/v1/ai-chat", }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)