from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "res" / "py"))

from person import Person
from speaker_manager import SpeakerManager
from speaker import Speaker
from smart_home_assistant import Action, SmartHomeAssistant
from json_repair import JsonRepair


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

    def test_json_repair_repairs_common_json_issues(self):
        broken_json = "{'name': 'Ava', 'voice_model': 'bixby',}"
        repaired = JsonRepair().repair_text(broken_json)

        self.assertIsNotNone(repaired)
        self.assertEqual(repaired["name"], "Ava")

        broken_json_2 = '{"people": [{"name": "Leo", "voice_model": "bixby",}, {"name": "Nia", "voice_model": "bixby"}]}'
        repaired_2 = JsonRepair().repair_text(broken_json_2)

        self.assertIsNotNone(repaired_2)
        self.assertEqual(repaired_2["people"][0]["name"], "Leo")

        broken_json_3 = '{people: [{name: "Ava", prompt: "You are Ava.", voice_model: "bixby", active: true,}, {name: "Leo", prompt: "You are Leo.", voice_model: "bixby", active: false,}]}'
        repaired_3 = JsonRepair().repair_text(broken_json_3)

        self.assertIsNotNone(repaired_3)
        self.assertEqual(repaired_3["people"][0]["name"], "Ava")
        self.assertTrue(repaired_3["people"][0]["active"])

        broken_json_4 = '{people: [{name: "Ava" prompt: "You are Ava." voice_model: "bixby"}]}'
        repaired_4 = JsonRepair().repair_text(broken_json_4)

        self.assertIsNotNone(repaired_4)
        self.assertEqual(repaired_4["people"][0]["prompt"], "You are Ava.")


if __name__ == "__main__":
    unittest.main()
