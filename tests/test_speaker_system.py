from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "res" / "py"))

from person import Person
from speaker_manager import SpeakerManager
from speaker import Speaker
from smart_home_assistant import Action, SmartHomeAssistant


class FakeLLM:
    def __init__(self):
        self.calls = []

    def choose_action(self, prompt, actions):
        self.calls.append((prompt, [a.name for a in actions]))
        return {"command_id": 0, "parameters": []}

    def build_response(self, person, action_name, prompt):
        return f"{person.name} says: I handled '{action_name}' for you."


class SpeakerSystemTests(unittest.TestCase):
    def test_person_from_dict_loads_values(self):
        person = Person.from_dict({
            "name": "Nia",
            "voice_model": "demo-voice",
            "prompt": "Respond warmly and clearly.",
        })

        self.assertEqual(person.name, "Nia")
        self.assertEqual(person.voice_model, "demo-voice")
        self.assertEqual(person.prompt, "Respond warmly and clearly.")

    def test_speaker_manager_reads_people_json(self):
        manager = SpeakerManager(
            people_file=Path(__file__).resolve().parents[1] / "res" / "json" / "people.json"
        )

        self.assertTrue(manager.people)
        self.assertTrue(all(isinstance(person, Person) for person in manager.people))
        self.assertTrue({person.name for person in manager.people})

    def test_speaker_uses_person_voice_model(self):
        speaker = Speaker(Person(name="Test Speaker", voice_model="voice-123"))
        self.assertEqual(speaker.person.voice_model, "voice-123")
        self.assertEqual(speaker.get_voice_model(), "voice-123")

    def test_smart_home_assistant_executes_selected_action_and_generates_line(self):
        calls = []

        def turn_on_lights():
            calls.append("lights on")
            return "lights on"

        pipeline = SmartHomeAssistant(
            actions=[Action("turn_on_lights", "turn on the lights", turn_on_lights)],
            llm=FakeLLM(),
            speaker_manager=SpeakerManager(
                people_file=Path(__file__).resolve().parents[1] / "res" / "json" / "people.json"
            ),
        )

        result = pipeline.handle("turn on the lights")

        self.assertEqual(result, "lights on")
        self.assertEqual(calls, ["lights on"])
        self.assertTrue(pipeline.last_response)
        self.assertIn("says:", pipeline.last_response)


if __name__ == "__main__":
    unittest.main()
