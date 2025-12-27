"""
FAISS vector store operations
"""
from pathlib import Path
from langchain_community.vectorstores import FAISS
from com.mhire.app.services.rag.embedding import EmbeddingService
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()


class VectorStoreService:
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
            # Get embeddings
            embedding_service = EmbeddingService()
            self.embeddings = embedding_service.get_embeddings()
            
            # Load FAISS index
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
            faiss_path = project_root / "com/mhire/app/data/vector_db/faiss_index"
            
            if not faiss_path.exists():
                error_msg = f"FAISS index not found at {faiss_path}. Please run index_resources.py first."
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            self.vectorstore = FAISS.load_local(
                str(faiss_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            self._initialized = True
            logger.info("Vector store loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}", exc_info=True)
            raise
    
    def get_vectorstore(self):
        """Get the FAISS vectorstore instance"""
        return self.vectorstore