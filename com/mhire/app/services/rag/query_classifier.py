"""
Classify queries as CRITICAL or NORMAL
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from com.mhire.app.config.config import Config
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()


class QueryClassifier:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",  # Faster model for classification
            google_api_key=config.GEMINI_API_KEY,
            temperature=0,  # Deterministic classification
        )
        logger.info("Query classifier initialized")
    
    async def classify(self, query: str) -> str:
        """
        Classify query as CRITICAL or NORMAL
        
        Args:
            query: User's query text
            
        Returns:
            "CRITICAL" or "NORMAL"
        """
        try:
            logger.debug(f"Classifying query: {query[:100]}...")
            
            classification_prompt = f"""Classify the following query as either CRITICAL or NORMAL.

CRITICAL means the query involves:
- Mental health crisis (suicidal thoughts, severe depression/anxiety, self-harm)
- Medical emergencies or serious health concerns
- Severe financial distress or bankruptcy
- Legal trouble or rights violations
- Abuse (physical, emotional, sexual)
- Addiction issues requiring professional intervention
- Any situation requiring immediate professional help

NORMAL means:
- General health and wellness questions
- Building healthy habits
- Breaking minor bad habits
- Motivation and accountability
- Routine advice
- General lifestyle improvements

Query: "{query}"

Respond with ONLY one word: CRITICAL or NORMAL"""

            response = await self.llm.ainvoke(classification_prompt)
            classification = response.content.strip().upper()
            
            # Ensure valid response
            if classification not in ["CRITICAL", "NORMAL"]:
                logger.warning(f"Invalid classification response: {classification}. Defaulting to NORMAL")
                classification = "NORMAL"
            
            logger.info(f"Query classified as: {classification}")
            return classification
            
        except Exception as e:
            logger.error(f"Classification failed: {e}. Defaulting to NORMAL", exc_info=True)
            return "NORMAL"  # Fail safe to normal conversation



