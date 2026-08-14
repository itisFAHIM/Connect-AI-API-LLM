# Job Card: Support Message Triaging

**What it does:** Classifies incoming customer support messages to route them to the appropriate team.
**Input:** `{ "text": "string, 1-2000 characters" }`
**Output:** 
```json
{
  "category": "billing | bug | feature | other",
  "urgency": "low | normal | high",
  "confidence": 0.0-1.0,
  "reason": "one short sentence"
}