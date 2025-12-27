from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
from com.mhire.app.config.config import Config

class SessionTitleService:
    def __init__(self):
        config = Config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.3
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating concise, descriptive session titles for health and habit-related conversations.
        Analyze the conversation and generate EXACTLY 3 words that capture the main health topic or habit discussed.
        Rules:
        - EXACTLY 3 words only
        - Use title case (capitalize each word)
        - Be specific and descriptive about the health/habit topic
        - No punctuation or special characters
        - Focus on the primary health concern or habit being addressed
        - Prefer actionable or condition-specific terms (e.g., "Quit Smoking Plan", "Sleep Schedule Fix", "Reduce Sugar Intake")
        Respond with ONLY the 3-word title, nothing else."""),
            ("human", "Conversation:\n{conversation}\n\nGenerate a 3-word title:")
        ])
            
    def generate_session_title(self, history: List[Dict[str, str]]) -> str:
        """
        Generate a 3-word session title based on chat history using LangChain
        
        Args:
            history: List of message dictionaries with 'role' and 'content'
            
        Returns:
            A 3-word session title string
        """
        try:
            # Format the chat history
            formatted_history = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}" 
                for msg in history
            ])
            
            # Create the chain
            chain = self.prompt | self.llm
            
            # Invoke the chain
            response = chain.invoke({"conversation": formatted_history})
            
            # Extract title from response
            title = response.content.strip()
            
            # Validate and clean the title
            words = title.split()
            if len(words) > 3:
                title = " ".join(words[:3])
            elif len(words) < 3:
                # Fallback if model doesn't return 3 words
                title = "Chat Session History"
            
            return title
            
        except Exception as e:
            # Fallback title in case of error
            print(f"Error generating title: {e}")
            return "Chat Session History"

# Singleton instance
session_title_service = SessionTitleService()