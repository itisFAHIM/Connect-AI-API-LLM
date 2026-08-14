import os
import re
import json
import time
import logging
from openai import OpenAI, APIError, APITimeoutError
from src.schemas import TriageOutput

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ReliableLLMClient:
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/")
        self.api_key = os.getenv("LLM_API_KEY", "ollama")
        self.model = os.getenv("LLM_MODEL", "gemma3:4b")
        self.prompt_version = "triage-v1"
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=30.0)

    def _load_prompt(self) -> str:
        with open("prompts/triage-v1.md", "r", encoding="utf-8") as f:
            return f.read()

    def _clean_json_text(self, text: str) -> str:
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
        return re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()

    def _quarantine(self, raw_input: str, raw_output: str, error_msg: str):
        os.makedirs("logs", exist_ok=True)
        record = {
            "prompt_version": self.prompt_version,
            "input": raw_input,
            "raw_output": raw_output,
            "error": error_msg,
            "timestamp": time.time()
        }
        with open("logs/quarantine.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def generate_triage(self, text: str) -> tuple[TriageOutput | None, int, str]:
        system_prompt = self._load_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps({"text": text})}
        ]

        try:
            start_time = time.time()
            res = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.1)
            duration_ms = (time.time() - start_time) * 1000
            
            raw_text = res.choices[0].message.content or ""
            cleaned = self._clean_json_text(raw_text)

            try:
                parsed = TriageOutput.model_validate_json(cleaned)
                return parsed, 200, "Success"
            except Exception as val_err:
                # Repair retry once
                repair_messages = messages + [
                    {"role": "assistant", "content": raw_text},
                    {"role": "user", "content": f"Previous answer failed validation: {val_err}. Return valid JSON only."}
                ]
                repair_res = self.client.chat.completions.create(model=self.model, messages=repair_messages, temperature=0.1)
                repair_cleaned = self._clean_json_text(repair_res.choices[0].message.content or "")
                
                parsed = TriageOutput.model_validate_json(repair_cleaned)
                return parsed, 200, "Success (Repaired)"

        except APITimeoutError:
            return None, 504, "LLM provider timed out."
        except Exception as e:
            self._quarantine(text, str(e), "Execution/Validation failure")
            return None, 422, f"Failed: {str(e)}"