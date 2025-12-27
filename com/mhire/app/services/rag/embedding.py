"""
Embedding generation using Google Gemini
"""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from com.mhire.app.config.config import Config
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()


class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            config = Config()
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=config.GEMINI_API_KEY
            )
            self._initialized = True
            logger.info("Embedding service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}", exc_info=True)
            raise
    
    def get_embeddings(self):
        """Get the embeddings instance"""
        return self.embeddings