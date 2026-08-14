Job Card

Input: {"text": "string (1-2000 characters)"}
Output:
  json
  {
    "category": "billing | bug | feature | other",
    "urgency": "low | normal | high",
    "confidence": 0.0 - 1.0,
    "reason": "string"
  }


**Start

Bash

pip install -r requirements.txt

cp .env.example .env

uvicorn src.main:app --reload


Request:

Bash
    curl.exe -X POST "[http://127.0.0.1:8000/triage](http://127.0.0.1:8000/triage)" \
    -H "Content-Type: application/json" \
    -d '{"text": "I was charged twice for my subscription this month!"}'

Real Response (200 OK)

JSON

{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.95,
  "reason": "User is requesting assistance regarding their monthly payment invoice."
}


Evaluation Results

Run the evaluation suite using- 
 python evals/run_eval.py

Date: August 14, 2026  
Prompt Version: triage-v1 (prompts/triage-v1.md)  
Model: gemma3:4b (Ollama)  
Score: 8/8 (100.0%)

COST
Basically 0 cost on locally downloaded Self hosted Model on GPU via Ollama
10,000+ Requests/Day Projection: $0.00/day on Ollama