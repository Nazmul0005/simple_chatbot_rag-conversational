"""
Semantic search and retrieval logic
"""
from typing import List, Dict
from com.mhire.app.services.rag.vector_store import VectorStoreService
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()


class RetrieverService:
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize retriever with similarity threshold
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider a result relevant
        """
        self.similarity_threshold = similarity_threshold
        vector_store_service = VectorStoreService()
        self.vectorstore = vector_store_service.get_vectorstore()
        logger.info(f"Retriever initialized with threshold: {similarity_threshold}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant resources based on query
        
        Args:
            query: User's query text
            top_k: Number of top results to retrieve
            
        Returns:
            List of relevant document chunks with metadata and scores
        """
        try:
            logger.debug(f"Searching for query: {query[:100]}...")
            
            # Perform similarity search with scores
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=top_k
            )
            
            # Filter by similarity threshold and format results
            relevant_results = []
            for doc, score in results:
                # FAISS returns distance, lower is better
                # Convert to similarity (1 - normalized_distance)
                similarity = 1 - (score / 2)  # Rough normalization
                
                if similarity >= self.similarity_threshold:
                    relevant_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'similarity_score': round(similarity, 3)
                    })
                    logger.debug(f"Found relevant chunk with score: {similarity:.3f}")
            
            logger.info(f"Retrieved {len(relevant_results)} relevant results above threshold")
            return relevant_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []
    
    def format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved results into context string for LLM
        
        Args:
            results: List of search results
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'Unknown')
            resource_type = result['metadata'].get('resource_type', 'general')
            content = result['content']
            score = result['similarity_score']
            
            context_parts.append(
                f"[Resource {i} - {resource_type} - {source} - Relevance: {score}]\n{content}\n"
            )
        
        return "\n".join(context_parts)


