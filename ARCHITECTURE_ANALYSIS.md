# Architecture Analysis: Current vs. Desired RAG Implementation

## Executive Summary

**Current Implementation**: ❌ **DOES NOT** fully match the desired architecture
**Gap Level**: Moderate - The system has the right components but uses a suboptimal approach

---

## Desired Architecture (Your Specification)

```
User message
    ↓
Single LLM call with RAG as a "tool"
    ↓
LLM decides: "Do I need RAG for this?"
    ├─→ YES → Calls RAG function → Gets context → Responds
    └─→ NO → Responds directly

Benefits:
- Only 1 LLM call (cost-efficient)
- LLM intelligently decides when RAG is needed
- More natural conversation flow
- No need for separate classification logic
```

---

## Current Implementation

### Architecture Flow

```
User message
    ↓
[SEPARATE LLM CALL #1] Query Classifier
    ├─→ Analyzes: Is this CRITICAL or NORMAL?
    ├─→ Uses: gemini-2.0-flash-lite (separate model)
    └─→ Returns: "CRITICAL" or "NORMAL" label
    ↓
Decision Logic (Hard-coded if/else)
    ├─→ If NORMAL:
    │   └─→ [LLM CALL #2] Direct response with HEALTH_SYSTEM_PROMPT
    │
    └─→ If CRITICAL:
        ├─→ [RAG SEARCH] Retrieve resources (FAISS similarity search)
        ├─→ If resources found:
        │   └─→ [LLM CALL #2] Response with AUGMENTED_SYSTEM_PROMPT + context
        └─→ If no resources:
            └─→ [LLM CALL #2] Response with PROFESSIONAL_REDIRECT_PROMPT
    ↓
Response to user
```

### Key Code References

**File**: `com/mhire/app/services/ai_chat/ai_chat.py`

```python
# Step 1: SEPARATE LLM CALL for classification
classification = await query_classifier.classify(request.query)

# Step 2: Hard-coded decision logic
if classification == "NORMAL":
    # Direct response
    response = await llm.ainvoke(formatted_messages)
else:  # CRITICAL
    # RAG search
    search_results = retriever.search(request.query, top_k=3)
    if search_results:
        # RAG-augmented response
        response = await llm.ainvoke(formatted_messages)
    else:
        # Professional redirect
        response = await llm.ainvoke(redirect_prompt)
```

**File**: `com/mhire/app/services/rag/query_classifier.py`

```python
async def classify(self, query: str) -> str:
    """Classify query as CRITICAL or NORMAL"""
    classification_prompt = f"""Classify the following query as either CRITICAL or NORMAL.
    
    CRITICAL means: Mental health crisis, medical emergencies, abuse, addiction...
    NORMAL means: General health, habit building, motivation...
    
    Respond with ONLY one word: CRITICAL or NORMAL"""
    
    response = await self.llm.ainvoke(classification_prompt)
    return response.content.strip().upper()
```

---

## Detailed Comparison

### 1. **LLM Call Count**

| Aspect | Current | Desired |
|--------|---------|---------|
| **Calls per request** | 2-3 calls | 1 call |
| **Call 1** | Query classification (separate LLM) | Single LLM with tool access |
| **Call 2** | Response generation | (included in Call 1) |
| **Call 3** | (Optional) RAG search | (LLM decides internally) |
| **Cost** | Higher (multiple API calls) | Lower (single call) |
| **Latency** | Higher (sequential calls) | Lower (single call) |

### 2. **Decision Logic**

| Aspect | Current | Desired |
|--------|---------|---------|
| **Who decides RAG?** | Hard-coded if/else logic | LLM with function calling |
| **Classification method** | Separate LLM call | LLM reasoning + tool use |
| **Flexibility** | Binary (CRITICAL/NORMAL) | Nuanced (LLM decides granularly) |
| **Adaptability** | Fixed rules | Dynamic based on context |
| **Maintainability** | Requires prompt updates in 2 places | Single prompt definition |

### 3. **RAG Triggering**

| Scenario | Current | Desired |
|----------|---------|---------|
| **"I'm craving badly"** | Classified as CRITICAL → RAG triggered | LLM recognizes need → calls search_resources() |
| **"Good morning!"** | Classified as NORMAL → No RAG | LLM responds directly |
| **"What's a good sleep routine?"** | Classified as NORMAL → No RAG | LLM might call search_resources() if it decides |
| **"I feel suicidal"** | Classified as CRITICAL → RAG triggered | LLM recognizes crisis → calls search_resources() |
| **Nuanced cases** | May misclassify | LLM handles intelligently |

### 4. **Resource Retrieval**

| Aspect | Current | Desired |
|--------|---------|---------|
| **Trigger** | Classification result | LLM function call |
| **Search method** | FAISS similarity (0.7 threshold) | Same (FAISS similarity) |
| **Context injection** | Via AUGMENTED_SYSTEM_PROMPT | Via function return value |
| **Fallback** | PROFESSIONAL_REDIRECT_PROMPT | LLM decides fallback |

---

## Specific Gaps

### Gap 1: Separate Classification LLM Call
**Current**: Uses `gemini-2.0-flash-lite` for classification
```python
classification = await query_classifier.classify(request.query)  # LLM Call #1
```

**Desired**: LLM decides internally
```python
# Single LLM call with tool access
response = await llm.ainvoke(
    messages,
    tools=[search_resources],  # LLM decides if it needs this
)
```

**Impact**: 
- ❌ Extra API call cost
- ❌ Extra latency
- ❌ Duplicate LLM reasoning

---

### Gap 2: Hard-coded Decision Logic
**Current**: Binary if/else routing
```python
if classification == "NORMAL":
    # Path A
else:  # CRITICAL
    # Path B
```

**Desired**: LLM-driven decision
```python
# LLM autonomously decides:
# "User said 'I'm craving badly'" → calls search_resources("coping with cravings")
# "User said 'good morning!'" → responds directly
```

**Impact**:
- ❌ Less flexible for edge cases
- ❌ Requires manual prompt updates for new scenarios
- ❌ No nuanced understanding

---

### Gap 3: Classification Criteria
**Current**: Only 2 categories (CRITICAL/NORMAL)
```
CRITICAL: Mental health crisis, medical emergencies, abuse, addiction
NORMAL: General health, habit building, motivation
```

**Desired**: Granular LLM reasoning
```
LLM can decide:
- "This needs coping strategies" → search_resources("coping")
- "This needs treatment info" → search_resources("treatment")
- "This needs emergency resources" → search_resources("emergency")
- "This is just conversation" → respond directly
```

**Impact**:
- ❌ Cannot distinguish between different types of critical queries
- ❌ All critical queries get same RAG treatment
- ❌ No category-specific resource retrieval

---

### Gap 4: Function Calling Not Implemented
**Current**: Manual RAG orchestration
```python
search_results = retriever.search(request.query, top_k=3)
if search_results:
    # Use results
```

**Desired**: LLM function calling
```python
# Define tool for LLM
def search_resources(query: str, category: str) -> str:
    return retriever.search(query, category, top_k=3)

# LLM autonomously calls it
response = await llm.ainvoke(
    messages,
    tools=[search_resources],
)
```

**Impact**:
- ❌ LLM cannot autonomously decide when to use RAG
- ❌ No tool-use capability
- ❌ Requires external orchestration

---

## Current Implementation Strengths

✅ **Semantic similarity search**: Uses FAISS with embeddings (good foundation)
✅ **Threshold-based filtering**: 0.7 similarity threshold prevents irrelevant results
✅ **Context formatting**: Properly formats retrieved resources for LLM
✅ **Fallback handling**: Has professional redirect for no-resource scenarios
✅ **Logging**: Comprehensive logging for debugging
✅ **Error handling**: Graceful error handling with defaults

---

## Current Implementation Weaknesses

❌ **Multiple LLM calls**: 2-3 calls per request (inefficient)
❌ **Separate classification**: Duplicate reasoning in classification LLM
❌ **Binary classification**: Only CRITICAL/NORMAL, no nuance
❌ **Hard-coded routing**: if/else logic, not LLM-driven
❌ **No function calling**: LLM cannot autonomously trigger RAG
❌ **Fixed decision tree**: Cannot adapt to new scenarios without code changes
❌ **Cost inefficiency**: Multiple API calls increase costs
❌ **Latency**: Sequential calls add latency

---

## Recommended Architecture (Function Calling Approach)

### Implementation Strategy

```python
# 1. Define RAG as a tool
tools = [
    {
        "name": "search_resources",
        "description": "Search professional resources for health/habit topics",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for"
                },
                "category": {
                    "type": "string",
                    "enum": ["coping_strategies", "emergency", "treatment", "general"],
                    "description": "Resource category"
                }
            },
            "required": ["query", "category"]
        }
    }
]

# 2. Single LLM call with tool access
response = await llm.ainvoke(
    messages,
    tools=tools,
    tool_choice="auto"  # LLM decides when to use tools
)

# 3. Handle tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        if tool_call["name"] == "search_resources":
            results = retriever.search(
                tool_call["args"]["query"],
                tool_call["args"]["category"]
            )
            # Continue conversation with results
else:
    # LLM responded directly without tools
    return response.content
```

### Benefits

✅ **Single LLM call**: Only 1 API call per request
✅ **LLM-driven decisions**: LLM decides when RAG is needed
✅ **Natural conversation**: No hard-coded routing
✅ **Cost-efficient**: Fewer API calls
✅ **Lower latency**: Single call instead of sequential
✅ **Flexible**: LLM can handle nuanced scenarios
✅ **Maintainable**: Single prompt definition
✅ **Scalable**: Easy to add new tools

---

## Migration Path

### Phase 1: Add Function Calling (Minimal Changes)
1. Define `search_resources` as a tool
2. Update LLM initialization to support tool calling
3. Modify `process_ai_chat()` to handle tool responses
4. Keep existing RAG logic as fallback

### Phase 2: Remove Classification Service
1. Remove `QueryClassifier` class
2. Remove separate classification LLM call
3. Update prompts to guide LLM tool usage

### Phase 3: Optimize Prompts
1. Update system prompt to explain when to use `search_resources`
2. Add examples of tool usage
3. Fine-tune tool descriptions

### Phase 4: Add More Tools (Optional)
1. `get_emergency_contacts()`
2. `get_treatment_options(category)`
3. `get_coping_strategies(situation)`

---

## Summary Table

| Criterion | Current | Desired | Gap |
|-----------|---------|---------|-----|
| **LLM Calls** | 2-3 | 1 | ❌ |
| **Decision Logic** | Hard-coded | LLM-driven | ❌ |
| **Function Calling** | No | Yes | ❌ |
| **Classification** | Binary | Granular | ❌ |
| **Cost Efficiency** | Low | High | ❌ |
| **Latency** | High | Low | ❌ |
| **Flexibility** | Low | High | ❌ |
| **Semantic Search** | Yes | Yes | ✅ |
| **Threshold Filtering** | Yes | Yes | ✅ |
| **Error Handling** | Good | Good | ✅ |

---

## Conclusion

The current architecture has a **solid foundation** with good RAG components (FAISS, embeddings, retrieval), but uses a **suboptimal orchestration approach**. 

**Key Issue**: The system makes 2-3 LLM calls per request with hard-coded routing, when it could make 1 intelligent LLM call with function calling.

**Recommendation**: Migrate to a **function calling approach** where the LLM autonomously decides when to use RAG tools. This would:
- Reduce API calls by 50-66%
- Lower latency
- Improve flexibility
- Reduce costs
- Provide more natural conversation flow

The migration is straightforward and can be done incrementally without breaking existing functionality.
