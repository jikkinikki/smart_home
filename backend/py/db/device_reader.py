"""Read devices from the database.

Usage:
    from db.device_reader import DeviceReader

    reader = DeviceReader()
    reader.get_all_devices()       # list of Device rows
    reader.get_device(dev_id)      # one Device row, or None
"""
from sqlmodel import Session, select

from db.database import engine
from db.models import Device


class DeviceReader:
    def get_all_devices(self) -> list[Device]:
        with Session(engine) as session:
            return list(session.exec(select(Device)).all())

    def get_device(self, dev_id: str) -> Device | None:
        with Session(engine) as session:
            return session.get(Device, dev_id)
