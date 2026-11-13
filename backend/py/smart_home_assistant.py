from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

from openrouter_client import OpenRouterClient
from person import Person
from speaker import Speaker
from speaker_manager import SpeakerManager


@dataclass
class Action:
    name: str
    description: str
    func: Callable[[], object]

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class SmartHomeAssistant:
    def __init__(self, actions: Optional[Iterable[Action]] = None, llm=None, speaker_manager=None):
        self.actions = list(actions or [])
        self.llm = llm or OpenRouterClient()
        self.speaker_manager = speaker_manager or SpeakerManager()
        self.last_response = ""
        self.last_action = None

    def handle(self, prompt: str, speaker: Optional[Speaker] = None):
        decision = self.llm.choose_action(prompt, self.actions) if hasattr(self.llm, "choose_action") else self._fallback_decision(prompt)
        action_index = int(decision.get("command_id", 0)) if isinstance(decision, dict) else 0

        if action_index < 0 or action_index >= len(self.actions):
            action_index = 0

        chosen_action = self.actions[action_index]
        self.last_action = chosen_action

        result = chosen_action.run()

        selected_person = self.speaker_manager.select_random()
        if speaker is None:
            speaker = Speaker(selected_person)

        self.last_response = self._build_response(selected_person, chosen_action.name, prompt)
        if speaker.person.prompt:
            speaker.speak(self.last_response)
        return result

    def _fallback_decision(self, prompt: str):
        return {"command_id": 0, "parameters": []}

    def _build_response(self, person: Person, action_name: str, prompt: str) -> str:
        if hasattr(self.llm, "build_response"):
            return self.llm.build_response(person, action_name, prompt)

        base = person.build_system_prompt()
        return f"{person.name}: {base} I handled '{action_name}' for your request: '{prompt}'."
