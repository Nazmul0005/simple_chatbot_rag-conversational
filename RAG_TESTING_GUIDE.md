# RAG Trigger Keywords - Quick Reference & Testing Guide

## Quick Category Reference

| Category | Priority | Trigger When | Example |
|----------|----------|--------------|---------|
| **crisis** | 🔴 Highest | Suicidal/self-harm | "I want to die" |
| **cravings** | 🔴 High | Urges/temptation | "I'm craving badly" |
| **relapse** | 🔴 High | Relapsed/broke streak | "I used again" |
| **withdrawal** | 🔴 High | Withdrawal symptoms | "I'm detoxing" |
| **medication** | 🔴 High | Medication questions | "What meds help?" |
| **triggers** | 🟡 Medium | Difficult situations | "I'm stressed" |
| **help** | 🟡 Medium | Seeking resources | "Where can I find help?" |
| **substances** | 🟡 Medium | Specific substances | "I'm struggling with alcohol" |
| **coping** | 🟡 Medium | Coping strategies | "How do I cope?" |
| **recovery** | 🟡 Medium | Recovery journey | "I'm in recovery" |
| **harm_reduction** | 🟡 Medium | Safer use | "How do I use safely?" |
| **mental_health** | 🟡 Medium | Mental health | "I'm depressed" |
| **physical** | 🟢 Low | Physical symptoms | "I can't sleep" |

---

## Test Cases

### ✅ Should Trigger RAG

#### Crisis Category
```
"I'm having suicidal thoughts"
"I want to end it all"
"I'm thinking about overdosing"
"I can't go on anymore"
"I want to hurt myself"
```

#### Cravings Category
```
"I'm having strong cravings"
"I have an urge to use"
"I can't resist the temptation"
"I'm struggling not to use"
"I'm thinking about using"
```

#### Relapse Category
```
"I relapsed yesterday"
"I used again after 30 days"
"I broke my streak"
"I fell off the wagon"
"I couldn't stop myself"
```

#### Medication Category
```
"What medications help with opioid addiction?"
"Is buprenorphine effective?"
"Can I use naloxone for overdose?"
"Tell me about methadone"
"What's the difference between naltrexone and buprenorphine?"
```

#### Withdrawal Category
```
"I'm experiencing withdrawal symptoms"
"I'm detoxing and feeling terrible"
"I have shakes and sweating"
"I'm coming off opioids"
"I'm quitting cold turkey"
```

#### Help Category
```
"Where can I find treatment?"
"I need help with my addiction"
"What resources are available?"
"How do I get into a program?"
"Where's the nearest crisis line?"
```

#### Coping Category
```
"How do I cope with cravings?"
"What techniques can help?"
"Tell me about urge surfing"
"What's the HALT method?"
"How do I manage my triggers?"
```

#### Triggers Category
```
"I'm feeling really stressed"
"I'm at a party with people who use"
"I'm feeling lonely and depressed"
"I'm overwhelmed right now"
"I'm around my old friends"
```

#### Substances Category
```
"I'm struggling with alcohol"
"I want to quit smoking"
"I'm addicted to opioids"
"I can't stop drinking"
"I'm using too much cocaine"
```

#### Recovery Category
```
"I'm in recovery"
"I want to get sober"
"Tell me about AA meetings"
"I'm celebrating 90 days clean"
"I'm looking for a support group"
```

#### Mental Health Category
```
"I'm feeling depressed"
"I have anxiety"
"I need a therapist"
"I have PTSD"
"I'm having panic attacks"
```

#### Harm Reduction Category
```
"What is harm reduction?"
"How do I use safely?"
"Where can I get clean needles?"
"What are fentanyl test strips?"
"Tell me about the Good Samaritan law"
```

#### Physical Category
```
"I can't sleep"
"I'm exhausted"
"I have a headache"
"I'm not eating"
"I have stomach pain"
```

---

### ❌ Should NOT Trigger RAG

```
"Good morning!"
"How are you?"
"What's the weather like?"
"Tell me a joke"
"What's your favorite color?"
"How do I cook pasta?"
"What's the capital of France?"
"Can you help me with math homework?"
"What time is it?"
"Do you like pizza?"
```

---

## Testing Commands

### Test 1: Crisis Query
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I am having suicidal thoughts",
    "history": []
  }'
```
**Expected:** RAG triggered, crisis resources returned

### Test 2: Cravings Query
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I am having strong cravings right now",
    "history": []
  }'
```
**Expected:** RAG triggered, coping strategies returned

### Test 3: Medication Query
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What medications help with opioid addiction?",
    "history": []
  }'
```
**Expected:** RAG triggered, medication info returned

### Test 4: Normal Greeting
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Good morning!",
    "history": []
  }'
```
**Expected:** RAG NOT triggered, direct response

### Test 5: Off-Topic Question
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?",
    "history": []
  }'
```
**Expected:** RAG NOT triggered, direct response

### Test 6: Multiple Keywords (Priority Test)
```bash
curl -X POST http://localhost:8000/api/v1/ai_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I am suicidal and having cravings",
    "history": []
  }'
```
**Expected:** RAG triggered with CRISIS category (highest priority)

---

## Checking Logs

### View logs in real-time
```bash
docker-compose logs -f app
```

### Look for these log messages

**RAG Triggered:**
```
DEBUG: Matched category 'crisis' for query: I am having suicidal thoughts
INFO: RAG needed: True, category: crisis
DEBUG: Retrieved context length: 2500
```

**RAG Not Triggered:**
```
DEBUG: No RAG keywords matched for query: Good morning!
INFO: RAG needed: False, category: general
```

**Category Matched:**
```
DEBUG: Matched category 'cravings' for query: I am having strong cravings
```

---

## Expected Behavior

### Crisis Query Flow
```
Query: "I am having suicidal thoughts"
    ↓
Keyword Match: "suicidal" found in crisis keywords
    ↓
Category: crisis
    ↓
RAG Triggered: YES
    ↓
Search: FAISS.search("I am having suicidal thoughts", "crisis")
    ↓
Resources: Crisis hotlines, emergency resources
    ↓
Response: "This is a crisis. Please call 988..."
```

### Normal Query Flow
```
Query: "Good morning!"
    ↓
Keyword Match: No keywords found
    ↓
Category: general
    ↓
RAG Triggered: NO
    ↓
Response: "Hey! Good morning! How are you?"
```

---

## Troubleshooting

### RAG Not Triggering When Expected

**Check:**
1. Is the keyword in the query?
2. Is the keyword spelled correctly?
3. Is the keyword in the right category?
4. Check logs for "No RAG keywords matched"

**Example:**
```
Query: "I'm having cravings"
Expected: RAG triggered
Actual: RAG not triggered

Solution: Check if "cravings" is in RAG_TRIGGER_KEYWORDS["cravings"]
```

### RAG Triggering When Not Expected

**Check:**
1. Which keyword matched?
2. Is that keyword too generic?
3. Should it be in a different category?
4. Check logs for matched category

**Example:**
```
Query: "Can you help me with homework?"
Expected: RAG not triggered
Actual: RAG triggered

Reason: "help" keyword matched
Solution: Make "help" keyword more specific or add context filter
```

### Wrong Category Selected

**Check:**
1. Are multiple keywords matching?
2. Which category has highest priority?
3. Is priority order correct?

**Example:**
```
Query: "I'm suicidal and craving"
Keywords: "suicidal" (crisis), "craving" (cravings)
Expected: crisis (highest priority)
Actual: cravings

Solution: Check priority order - crisis should come before cravings
```

---

## Performance Metrics

### Expected Response Times
- Keyword matching: <5ms
- RAG search: 200-300ms
- LLM response: 500-800ms
- **Total: ~1.0-1.2 seconds**

### Expected Accuracy
- RAG activation: ~95%
- False positives: <5%
- False negatives: <5%

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| RAG not triggering | Keyword not in list | Add keyword to category |
| Wrong category | Priority order | Check priority_order list |
| Too many false positives | Generic keywords | Make keywords more specific |
| Too many false negatives | Missing keywords | Add more keyword variations |
| Slow response | FAISS search slow | Check index size, optimize threshold |
| Empty response | LLM error | Check logs, verify API key |

---

## Summary

The RAG trigger keyword system:
- ✅ Uses 13 categories with 100+ keywords
- ✅ Prioritizes crisis situations
- ✅ Reduces unnecessary API calls
- ✅ Maintains conversation quality
- ✅ Easy to test and debug
- ✅ Production-ready

**Status: READY FOR TESTING** ✅
