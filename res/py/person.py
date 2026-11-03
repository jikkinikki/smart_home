from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Person:
    name: str
    prompt: str = ""
    voice_model: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        return cls(
            name=str(data.get("name") or "Unnamed person"),
            prompt=str(data.get("prompt") or data.get("custom_prompt") or ""),
            voice_model=str(data.get("voice_model") or data.get("voice") or ""),
        )

    def build_system_prompt(self) -> str:
        if self.prompt:
            return self.prompt
        return f"You are {self.name}. Speak naturally and helpfully."
