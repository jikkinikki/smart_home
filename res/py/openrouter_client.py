from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

import keys
import settings


class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or getattr(keys, "openrouter_api_key", None)
        self.model = model or getattr(settings, "OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.api_base = getattr(settings, "OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise ValueError("No OpenRouter API key. Set openrouter_api_key in res/py/keys.py or the OPENROUTER_API_KEY env var.")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "Smart Home Assistant",
        }

    def generate(self, system_prompt: str, user_prompt: str, response_format: Optional[str] = "text") -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=90,
        )

        if not response.ok:
            raise RuntimeError(f"OpenRouter API error: {response.status_code} - {response.text}")

        body = response.json()
        return body["choices"][0]["message"]["content"]

    @staticmethod
    def parse_json_response(text: str):
        if not text:
            return {}
        try:
            return json.loads(text)
        except (TypeError, ValueError):
            return {"text": text}
