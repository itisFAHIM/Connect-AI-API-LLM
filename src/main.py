import os
from fastapi import FastAPI, HTTPException
from src.schemas import TriageInput, TriageOutput, CategoryEnum, UrgencyEnum
from src.llm_client import ReliableLLMClient

app = FastAPI(title="Support Triage API")
llm_client = ReliableLLMClient()

@app.post("/triage", response_model=TriageOutput)
def triage_message(payload: TriageInput):
    # Stub mode check
    if os.getenv("LLM_STUB", "0") == "1":
        return TriageOutput(
            category=CategoryEnum.OTHER,
            urgency=UrgencyEnum.LOW,
            confidence=0.99,
            reason="Stub mode active."
        )

    # Kill switch check
    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        return TriageOutput(
            category=CategoryEnum.OTHER,
            urgency=UrgencyEnum.LOW,
            confidence=0.0,
            reason="Kill switch triggered: LLM disabled."
        )

    result, status_code, message = llm_client.generate_triage(payload.text)
    if status_code != 200 or result is None:
        raise HTTPException(status_code=status_code, detail=message)

    return result