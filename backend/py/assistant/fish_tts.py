"""
Fish Audio text-to-speech (Drama 3).

Voices, moods and the engine are configured in settings.py. The API key goes in keys.py.

    tts = FishTTS()
    tts.speak("[happy] Lights are on!")                       # default voice
    tts.speak("[whispering] goodnight", voice="narrator")     # voice by name from settings
    tts.speak("<|speaker:0|>[calm] Hi.<|speaker:1|>[excited] Hey!",
              voice=["bixby", "narrator"])                    # multi-speaker dialogue
"""

import os
import re
import tempfile
import time
import warnings

import requests

from config import settings

API_BASE = "https://api.fish.audio"

# Matches [mood] tags. Paired tags like <whisper>..</whisper> and <|speaker:0|> are not matched.
MOOD_TAG = re.compile(r"\[([^\[\]]+)\]")


def _load_api_key():
    try:
        from config import keys  # config/keys.py (gitignored), see keys.example.py
        if getattr(keys, "fish_api_key", None):
            return keys.fish_api_key
    except ImportError:
        pass
    return os.environ.get("FISH_API_KEY")


class FishTTS:
    def __init__(self, api_key=None):
        self.api_key = api_key or _load_api_key()
        if not self.api_key:
            raise ValueError("No Fish Audio API key. Set fish_api_key in config/keys.py or the FISH_API_KEY env var.")

        self.engine = settings.TTS_ENGINE
        self.audio_format = settings.TTS_AUDIO_FORMAT
        self.moods = {mood.lower() for mood in settings.MOODS}
        self.voice_models = {name: model_id for name, model_id in settings.VOICE_MODELS.items() if model_id}
        self.default_voice = settings.DEFAULT_VOICE

        empty = [name for name, model_id in settings.VOICE_MODELS.items() if not model_id]
        if empty:
            warnings.warn(f"Voice models without an id in settings.py are skipped: {empty}", stacklevel=2)

        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    # ---------- moods ----------

    def get_moods(self):
        return sorted(self.moods)

    def find_invalid_moods(self, text):
        return [tag for tag in MOOD_TAG.findall(text) if tag.strip().lower() not in self.moods]

    # ---------- voice models ----------

    def get_voice_models(self):
        """Voice models loaded from settings.py, as {name: model_id}."""
        return dict(self.voice_models)

    def resolve_voice(self, voice):
        """Turn a voice name from settings into its model id. Raw model ids pass through unchanged."""
        if voice in self.voice_models:
            return self.voice_models[voice]
        if re.fullmatch(r"[0-9a-f]{32}", voice):
            return voice
        raise ValueError(f"Unknown voice '{voice}'. Loaded voices: {list(self.voice_models)}")

    def search_voice_models(self, search=None, own_only=False, language=None, limit=50):
        """
        Search Fish Audio's voice model catalog, for finding ids to put in settings.VOICE_MODELS.
        Returns a list of dicts: {"id", "title", "description", "languages", "tags", "author"}.
        """
        models = []
        page = 1
        while len(models) < limit:
            params = {"page_size": min(100, limit - len(models)), "page_number": page, "self": own_only}
            if search:
                params["title"] = search
            if language:
                params["language"] = language

            response = self.session.get(f"{API_BASE}/model", params=params, timeout=30)
            self._raise_for_error(response)
            items = response.json().get("items", [])
            if not items:
                break

            models += [{
                "id": m["_id"],
                "title": m["title"],
                "description": m.get("description", ""),
                "languages": m.get("languages", []),
                "tags": m.get("tags", []),
                "author": m.get("author", {}).get("nickname", ""),
            } for m in items]
            page += 1

        return models[:limit]

    # ---------- speech ----------

    def speak(self, text, voice=None, output_path=None, speed=1.0):
        """
        Convert text to speech. Blocks until the audio is ready and returns the path to the saved file.

        text:         text to speak, may contain [mood] tags
        voice:        voice name from settings (or a raw model id). Pass a list for multi-speaker
                      text, where <|speaker:0|> uses the first voice, <|speaker:1|> the second, etc.
                      Defaults to settings.DEFAULT_VOICE.
        output_path:  where to save; defaults to a temp file
        speed:        0.5 - 2.0
        """
        if not text or not text.strip():
            raise ValueError("Text is empty")

        invalid = self.find_invalid_moods(text)
        if invalid:
            warnings.warn(f"Unknown mood(s) {invalid}. Valid moods: {', '.join(self.get_moods())}", stacklevel=2)

        voice = voice or self.default_voice
        if isinstance(voice, (list, tuple)):
            reference_id = [self.resolve_voice(v) for v in voice]
        else:
            reference_id = self.resolve_voice(voice)

        body = {
            "text": text,
            "reference_id": reference_id,
            "format": self.audio_format,
            "prosody": {"speed": speed},
        }

        response = self.session.post(
            f"{API_BASE}/v1/tts",
            json=body,
            headers={"model": self.engine},
            stream=True,
            timeout=120,
        )
        self._raise_for_error(response)

        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"fish_tts_{int(time.time() * 1000)}.{self.audio_format}")

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    @staticmethod
    def _raise_for_error(response):
        if response.ok:
            return
        try:
            message = response.json().get("message", response.text)
        except ValueError:
            message = response.text
        raise RuntimeError(f"Fish Audio API error {response.status_code}: {message}")


if __name__ == "__main__":
    import sys

    tts = FishTTS()
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        for m in tts.search_voice_models(search=sys.argv[2] if len(sys.argv) > 2 else None, limit=20):
            print(f"{m['id']}  {m['title']}  {m['languages']}")
    else:
        text = " ".join(sys.argv[1:]) or "[happy] Hello! [whispering] This is Fish Audio."
        print("Saved to", tts.speak(text))
