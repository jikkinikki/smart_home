"""Base class for device importers.

An importer takes the JSON data of one device, checks that nothing is missing, and adds
it to the database. There is one subclass per source ("zigbee", "tuya", ...); each one
only says how to validate its own data and how to turn it into a Device row. Saving is
done here, so it's the same for every source.

Usage:
    ZigbeeImporter().add(data)   # raises ValueError if the data isn't valid
"""
from abc import ABC, abstractmethod
from sqlmodel import Session
from db.database import engine
from db.models import Device


class BaseImporter(ABC):
    # Set by each subclass, e.g. "zigbee". Must match data["source"].
    source: str

    # Fields every device needs, no matter the source
    REQUIRED_FIELDS = ("dev_id", "type", "source")

    def add(self, data: dict) -> Device:
        """Validate the data and insert it, or update the device if dev_id already exists."""
        valid = self.validate(data)
        device = self.to_device(valid)

        with Session(engine) as session:
            device = session.merge(device)  # insert or update by primary key (dev_id)
            session.commit()
            session.refresh(device)

        return device

    def validate(self, data: dict) -> dict:
        """Check the fields every device needs, then the source specific ones."""
        missing = [field for field in self.REQUIRED_FIELDS if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        if data["source"] != self.source:
            raise ValueError(f"{type(self).__name__} can't import source '{data['source']}'")

        return self.validate_source(data)

    @abstractmethod
    def validate_source(self, data: dict) -> dict:
        """
        Check the fields this source needs. Raise ValueError (pydantic's ValidationError
        is one) if something is missing or wrong, otherwise return the cleaned data.
        """

    @abstractmethod
    def to_device(self, data: dict) -> Device:
        """Turn the validated data into a Device row."""
