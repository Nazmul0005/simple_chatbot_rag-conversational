from typing import List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from com.mhire.app.config.config import Config
from com.mhire.app.services.ai_chat.ai_chat_schema import AIChatRequest, AIChatResponse, MessageHistory
from com.mhire.app.utils.prompt.prompt_function_calling import FUNCTION_CALLING_SYSTEM_PROMPT
from com.mhire.app.services.rag.rag_tool import RAGTool
from com.mhire.app.logger.logger import ChatEndpoint
import json

logger = ChatEndpoint.setup_chat_logger()

# Initialize services
config = Config()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config.GEMINI_API_KEY,
    temperature=0.7,
    convert_system_message_to_human=True
)

# Initialize RAG tool for function calling
rag_tool = RAGTool(similarity_threshold=0.7)


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
    """
    Process AI chat request with intelligent RAG tool calling.
    
    Hybrid approach:
    - First, use LLM to decide if RAG is needed (simple classification)
    - If RAG needed, retrieve resources
    - Then generate response with or without context
    
    This is more reliable than pure function calling with Gemini.
    """
    try:
        logger.info("Processing AI chat request with hybrid RAG approach")
        
        # Convert history to LangChain format
        history_messages = convert_to_langchain_messages(request.history)
        logger.debug(f"Converted {len(history_messages)} history messages")
        
        # Step 1: Decide if RAG is needed using keyword detection (faster and more reliable)
        logger.debug("Step 1: Determining if RAG is needed")
        category = _determine_category(request.query)
        rag_needed = category != "general"
        logger.info(f"RAG needed: {rag_needed}, category: {category}")
        
        # Step 2: Get context if RAG is needed
        context = ""
        if rag_needed:
            logger.debug("Step 2: Retrieving RAG context")
            context = rag_tool.search_resources(request.query, category)
            if not context:
                logger.debug(f"No resources found for category: {category}, trying general search")
                context = rag_tool.search_resources(request.query, "general")
            logger.debug(f"Retrieved context length: {len(context)}")
        
        # Step 3: Generate response using simple prompt
        logger.debug("Step 3: Generating response")
        
        if context:
            # Build prompt with context
            prompt_text = f"""You are Sora, a warm and supportive best friend helping with health and habits.

User Query: {request.query}

PROFESSIONAL RESOURCES:
{context}

Respond naturally based on these resources. Keep it conversational (1-2 sentences typically). For serious issues, mention consulting a professional."""
        else:
            # Build prompt without context
            prompt_text = f"""You are Sora, a warm and supportive best friend helping with health and habits.

User Query: {request.query}

Respond naturally and conversationally. Keep it brief (1-2 sentences typically)."""
        
        # Build full message list
        all_messages = history_messages + [HumanMessage(content=prompt_text)]
        
        logger.debug(f"Calling LLM with {len(all_messages)} messages")
        response = await llm.ainvoke(all_messages)
        
        logger.debug(f"Response type: {type(response)}")
        
        # Extract response content
        if hasattr(response, 'content') and response.content:
            ai_response = response.content.strip()
            logger.debug(f"Got response: {ai_response[:100]}")
        else:
            logger.error(f"Response has no content or is empty. Response: {response}")
            ai_response = "I'm having trouble processing your request. Please try again."
        
        logger.info(f"AI chat request processed successfully. Response length: {len(ai_response)}")
        return AIChatResponse(
            query=request.query,
            response=ai_response
        )
        
    except Exception as e:
        error_msg = f"Failed to process AI chat request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg) from e


async def _should_use_rag(query: str) -> bool:
    """
    Determine if RAG should be used for this query.
    
    Uses a simple LLM call to classify if the query needs professional resources.
    """
    try:
        logger.debug(f"Checking if RAG needed for: {query[:100]}")
        
        classification_prompt = f"""Analyze this user query and determine if they need professional resources/guidance.

Query: "{query}"

Respond with ONLY "YES" or "NO":
- YES if: They mention crisis/emergency, struggling with cravings, asking about treatment/medication, asking for specific resources, or any health concern that needs professional guidance
- NO if: Simple greeting, general conversation, off-topic question, or something you can answer directly

Response:"""
        
        response = await llm.ainvoke([HumanMessage(content=classification_prompt)])
        
        if not hasattr(response, 'content'):
            logger.warning("Classification response has no content, defaulting to NO")
            return False
        
        result = response.content.strip().upper()
        logger.debug(f"Classification result: {result}")
        
        return "YES" in result
        
    except Exception as e:
        logger.error(f"Error in _should_use_rag: {e}", exc_info=True)
        return False


async def _get_rag_context(query: str) -> tuple[str, str]:
    """
    Get RAG context and determine the category.
    
    Returns:
        Tuple of (context_string, category)
    """
    try:
        logger.debug(f"Getting RAG context for: {query[:100]}")
        
        # Determine category based on query
        category = _determine_category(query)
        logger.debug(f"Determined category: {category}")
        
        # Search for resources
        context = rag_tool.search_resources(query, category)
        
        if not context:
            logger.debug(f"No resources found for category: {category}, trying general search")
            context = rag_tool.search_resources(query, "general")
        
        logger.debug(f"Retrieved context length: {len(context)}")
        return context, category
        
    except Exception as e:
        logger.error(f"Error in _get_rag_context: {e}", exc_info=True)
        return "", "general"


def _determine_category(query: str) -> str:
    """
    Determine the resource category based on query keywords.
    """
    query_lower = query.lower()
    
    # Emergency keywords
    emergency_keywords = [
        "overdose", "suicidal", "suicide", "self-harm", "harm myself",
        "emergency", "urgent", "crisis", "dying", "death", "kill myself",
        "severe", "critical", "immediate help", "911", "ambulance"
    ]
    
    # Coping keywords
    coping_keywords = [
        "craving", "urge", "struggling", "struggling with", "hard time",
        "difficult", "tempted", "want to", "can't stop", "help me",
        "manage", "cope", "deal with", "handle"
    ]
    
    # Treatment keywords
    treatment_keywords = [
        "medication", "medicine", "drug", "treatment", "therapy",
        "doctor", "professional", "help", "cure", "heal", "recover",
        "prescription", "antidepressant", "anxiety", "depression"
    ]
    
    # Check emergency first (highest priority)
    if any(keyword in query_lower for keyword in emergency_keywords):
        return "emergency"
    
    # Check treatment
    if any(keyword in query_lower for keyword in treatment_keywords):
        return "treatment"
    
    # Check coping
    if any(keyword in query_lower for keyword in coping_keywords):
        return "coping_strategies"
    
    # Default to general
    return "general"


async def _handle_llm_response(response: Any, messages: List, original_query: str) -> str:
    """
    Handle LLM response, which may include tool calls.
    
    Args:
        response: Response from LLM (may contain tool_calls)
        messages: Original message list for context
        original_query: Original user query
        
    Returns:
        Final AI response text
    """
    try:
        logger.debug(f"Response object: {response}")
        logger.debug(f"Response type: {type(response)}")
        logger.debug(f"Has tool_calls: {hasattr(response, 'tool_calls')}")
        
        # Check if response contains tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"LLM called {len(response.tool_calls)} tool(s)")
            
            # Process each tool call
            tool_results = []
            for tool_call in response.tool_calls:
                logger.debug(f"Processing tool call: {tool_call}")
                logger.debug(f"Tool call type: {type(tool_call)}")
                
                # Handle both dict and object formats
                tool_name = tool_call.get('name') if isinstance(tool_call, dict) else getattr(tool_call, 'name', None)
                tool_args = tool_call.get('args') if isinstance(tool_call, dict) else getattr(tool_call, 'args', {})
                
                logger.debug(f"Tool name: {tool_name}, args: {tool_args}")
                
                if tool_name == 'search_resources':
                    # Extract arguments
                    query = tool_args.get('query', original_query) if isinstance(tool_args, dict) else getattr(tool_args, 'query', original_query)
                    category = tool_args.get('category', 'general') if isinstance(tool_args, dict) else getattr(tool_args, 'category', 'general')
                    
                    logger.info(f"Tool call: search_resources(query='{query}', category='{category}')")
                    
                    # Call the RAG tool
                    context = rag_tool.search_resources(query, category)
                    tool_results.append({
                        'tool_name': 'search_resources',
                        'context': context,
                        'query': query,
                        'category': category
                    })
                    logger.debug(f"Retrieved context length: {len(context)}")
            
            # If we have tool results, get final response with context
            if tool_results:
                logger.debug("Getting final response with tool results")
                final_response = await _get_final_response_with_context(
                    response, 
                    tool_results, 
                    messages
                )
                return final_response
            else:
                logger.warning("Tool was called but no results were processed")
        
        # No tool calls - return direct response
        if hasattr(response, 'content') and response.content:
            logger.debug(f"Returning direct LLM response (no tool calls): {response.content[:100]}")
            return response.content
        
        # Fallback
        logger.warning(f"Could not extract response content. Response: {response}")
        return ""
        
    except Exception as e:
        logger.error(f"Error handling LLM response: {e}", exc_info=True)
        logger.error(f"Response object was: {response}")
        return ""


async def _get_final_response_with_context(
    initial_response: Any,
    tool_results: List[dict],
    messages: List
) -> str:
    """
    Get final response from LLM with tool context incorporated.
    
    Args:
        initial_response: Initial LLM response with tool calls
        tool_results: Results from tool calls
        messages: Original message list
        
    Returns:
        Final response text
    """
    try:
        # Format tool results for LLM
        context_str = "\n\n".join([
            f"[Resource Search Results - {result['category']}]\n{result['context']}"
            for result in tool_results
            if result['context']
        ])
        
        if not context_str:
            logger.debug("No context from tool results, using initial response")
            if hasattr(initial_response, 'content'):
                return initial_response.content
            return ""
        
        logger.debug(f"Incorporating {len(tool_results)} tool result(s) into response")
        
        # Create follow-up message with context
        follow_up_prompt = f"""Based on the professional resources below, provide your response to the user's query.

PROFESSIONAL RESOURCES:
{context_str}

Remember to:
1. Give specific, actionable advice based on the resources
2. For serious issues: "This is based on professional guidance, but please consult a qualified professional for your specific situation."
3. Keep your response natural and conversational (1-2 sentences typically)
4. Don't just repeat the resources - synthesize them into helpful advice"""
        
        # Get final response with context
        final_messages = messages + [
            HumanMessage(content=follow_up_prompt)
        ]
        
        final_response = await llm.ainvoke(final_messages)
        
        if hasattr(final_response, 'content'):
            logger.debug("Successfully generated final response with context")
            return final_response.content
        
        return ""
        
    except Exception as e:
        logger.error(f"Error getting final response with context: {e}", exc_info=True)
        # Fallback to initial response
        if hasattr(initial_response, 'content'):
            return initial_response.content
        return ""