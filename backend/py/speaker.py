from __future__ import annotations

from typing import Optional


class Speaker:
    def __init__(self, person, tts_client=None):
        self.person = person
        self.tts_client = tts_client or self._build_default_tts()

    @staticmethod
    def _build_default_tts():
        try:
            from fish_tts import FishTTS

            return FishTTS()
        except Exception:
            return None

    def get_voice_model(self) -> str:
        return self.person.voice_model or "default"

    def speak(self, text: str, output_path: Optional[str] = None):
        if not text or not text.strip():
            return None

        if self.tts_client is None:
            print(text)
            return None

        voice_name = self.get_voice_model()
        return self.tts_client.speak(text, voice=voice_name, output_path=output_path)
