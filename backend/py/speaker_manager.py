from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable, List, Optional

from person import Person


class SpeakerManager:
    def __init__(self, people_file: Optional[str] = None, people: Optional[Iterable[Person]] = None):
        default_file = Path(__file__).resolve().parents[1] / "json" / "people.json"
        self.people_file = Path(people_file) if people_file else default_file
        self.people = list(people) if people is not None else self.load_people()

    def load_people(self) -> List[Person]:
        if not self.people_file.exists():
            return []

        with self.people_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if isinstance(data, dict) and "people" in data:
            entries = data["people"]
        else:
            entries = data

        return [Person.from_dict(item) for item in entries]

    def select_random(self, rng: Optional[random.Random] = None) -> Person:
        if not self.people:
            raise ValueError("No people are configured. Add entries to res/json/people.json.")

        chooser = rng or random.Random()
        return chooser.choice(self.people)
