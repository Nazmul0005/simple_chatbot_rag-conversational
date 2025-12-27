from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from com.mhire.app.config.config import Config
from com.mhire.app.services.ai_chat.ai_chat_schema import AIChatRequest, AIChatResponse, MessageHistory
from com.mhire.app.utils.prompt.prompt_short import HEALTH_SYSTEM_PROMPT
from com.mhire.app.utils.prompt.prompt_templates import AUGMENTED_SYSTEM_PROMPT, PROFESSIONAL_REDIRECT_PROMPT
from com.mhire.app.services.rag.query_classifier import QueryClassifier
from com.mhire.app.services.rag.retriever import RetrieverService
from com.mhire.app.logger.logger import ChatEndpoint

logger = ChatEndpoint.setup_chat_logger()

# Initialize services
config = Config()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config.GEMINI_API_KEY,
    temperature=0.7,
    convert_system_message_to_human=True
)

# Initialize RAG components
query_classifier = QueryClassifier()
retriever = RetrieverService(similarity_threshold=0.7)


def convert_to_langchain_messages(messages: List[MessageHistory]):
    """Convert message list to LangChain message format"""
    try:
        logger.debug(f"Converting {len(messages)} messages to LangChain format")
        langchain_messages = []
        
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        
        logger.debug(f"Successfully converted {len(langchain_messages)} messages")
        return langchain_messages
    except Exception as e:
        error_msg = f"Failed to convert messages to LangChain format: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg) from e


async def process_ai_chat(request: AIChatRequest) -> AIChatResponse:
    """Process AI chat request with RAG-augmented responses for critical queries"""
    try:
        logger.info(f"Processing AI chat request")
        
        # Step 1: Classify query
        classification = await query_classifier.classify(request.query)
        logger.info(f"Query classification: {classification}")
        
        # Convert history to LangChain format
        history_messages = convert_to_langchain_messages(request.history)
        
        # Step 2: Handle based on classification
        if classification == "NORMAL":
            # Normal conversation flow (existing logic)
            logger.debug("Processing as normal conversation")
            prompt = ChatPromptTemplate.from_messages([
                ("system", HEALTH_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
            
            formatted_messages = prompt.format_messages(
                history=history_messages,
                input=request.query
            )
            
            response = await llm.ainvoke(formatted_messages)
            ai_response = response.content
            
        else:  # CRITICAL
            logger.debug("Processing as critical query with RAG")
            
            # Step 3: Retrieve relevant resources
            search_results = retriever.search(request.query, top_k=3)
            
            if search_results:
                # Resources found - use augmented prompt
                logger.info(f"Found {len(search_results)} relevant resources")
                context = retriever.format_context(search_results)
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", AUGMENTED_SYSTEM_PROMPT),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{input}")
                ])
                
                formatted_messages = prompt.format_messages(
                    context=context,
                    history=history_messages,
                    input=request.query
                )
                
                response = await llm.ainvoke(formatted_messages)
                ai_response = response.content
                
            else:
                # No relevant resources - redirect to professional
                logger.info("No relevant resources found, redirecting to professional")
                
                redirect_prompt = PROFESSIONAL_REDIRECT_PROMPT.format(query=request.query)
                response = await llm.ainvoke(redirect_prompt)
                ai_response = response.content
        
        logger.info(f"AI chat request processed successfully")
        return AIChatResponse(
            query=request.query,
            response=ai_response
        )
        
    except Exception as e:
        error_msg = f"Failed to process AI chat request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg) from e