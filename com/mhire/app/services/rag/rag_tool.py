"""
RAG Tool for LLM function calling
Provides search_resources function that LLM can autonomously call
"""
from typing import List, Dict, Literal
from com.mhire.app.services.rag.retriever import RetrieverService
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()


class RAGTool:
    """Wrapper for RAG functionality as an LLM tool"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """Initialize RAG tool with retriever"""
        self.retriever = RetrieverService(similarity_threshold=similarity_threshold)
        logger.info("RAG tool initialized")
    
    def search_resources(
        self,
        query: str,
        category: Literal["emergency", "coping_strategies", "treatment", "general"] = "general",
        top_k: int = 3
    ) -> str:
        """
        Search professional resources for health/habit topics
        
        This function is called by the LLM when it determines that RAG context is needed.
        
        Args:
            query: What to search for (e.g., "coping with cravings", "emergency help")
            category: Resource category to prioritize
                - "emergency": Crisis resources, immediate help
                - "coping_strategies": Techniques for managing urges/struggles
                - "treatment": Medical/professional treatment options
                - "general": General health and habit information
            top_k: Number of results to retrieve (default: 3)
            
        Returns:
            Formatted context string with relevant resources, or empty string if none found
            
        Examples:
            >>> tool.search_resources("managing anxiety", category="coping_strategies")
            >>> tool.search_resources("suicidal thoughts", category="emergency")
            >>> tool.search_resources("medication options", category="treatment")
        """
        try:
            logger.debug(f"RAG tool called: query='{query}', category='{category}'")
            
            # Enhance query with category context for better semantic search
            enhanced_query = self._enhance_query(query, category)
            logger.debug(f"Enhanced query: '{enhanced_query}'")
            
            # Perform semantic search
            search_results = self.retriever.search(enhanced_query, top_k=top_k)
            
            if not search_results:
                logger.info(f"No resources found for: {query}")
                return ""
            
            # Format results for LLM consumption
            context = self.retriever.format_context(search_results)
            logger.info(f"Retrieved {len(search_results)} resources for category: {category}")
            
            return context
            
        except Exception as e:
            logger.error(f"RAG tool search failed: {e}", exc_info=True)
            return ""
    
    def _enhance_query(self, query: str, category: str) -> str:
        """
        Enhance query with category context for better semantic search
        
        Args:
            query: Original query
            category: Resource category
            
        Returns:
            Enhanced query string
        """
        category_keywords = {
            "emergency": "crisis emergency urgent help immediate",
            "coping_strategies": "coping strategies techniques manage handle",
            "treatment": "treatment medication therapy professional medical",
            "general": "health habit wellness information"
        }
        
        keywords = category_keywords.get(category, "")
        if keywords:
            return f"{query} {keywords}"
        return query
    
    def get_tool_definition(self) -> Dict:
        """
        Get tool definition for LLM function calling
        
        Returns:
            Tool definition in OpenAI format
        """
        return {
            "type": "function",
            "function": {
                "name": "search_resources",
                "description": "Search professional resources and guidance materials for health and habit-related topics. Use this when the user needs specific information about coping strategies, emergency resources, treatment options, or general health guidance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for (e.g., 'coping with cravings', 'emergency help', 'sleep tips')"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["emergency", "coping_strategies", "treatment", "general"],
                            "description": "Resource category: 'emergency' for crisis help, 'coping_strategies' for managing struggles, 'treatment' for medical options, 'general' for health info"
                        }
                    },
                    "required": ["query", "category"]
                }
            }
        }
