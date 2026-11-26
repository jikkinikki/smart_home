"""Devices as they are saved in the database (not the loaded/connected ones in /devices)."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from db.database import get_session
from db.models import Device, Room

router = APIRouter(prefix="/db/devices", tags=["Database devices"])

# How high up the device is placed, e.g. "high" for ceiling lamps
Vertical = Literal["low", "medium", "high"]


class DbDeviceOut(BaseModel):
    # Everything in the Device row except local_key, which is a secret
    id: str
    name: str
    type: str
    source: str | None
    address: str | None
    version: str | None
    disabled: bool
    hidden: bool
    vertical: Vertical | None
    extra: dict
    room_id: int | None


class DbDeviceUpdate(BaseModel):
    # Only the fields that can be edited. Fields left out are not changed.
    name: str | None = None
    hidden: bool | None = None
    vertical: Vertical | None = None    # null clears it
    room_id: int | None = None          # null = not in a room


@router.get("", response_model=list[DbDeviceOut])
def get_db_devices(session: Session = Depends(get_session)):
    return session.exec(select(Device)).all()


@router.patch("/{device_id}", response_model=DbDeviceOut)
def update_db_device(device_id: str, changes: DbDeviceUpdate, request: Request,
                     session: Session = Depends(get_session)):
    device = session.get(Device, device_id)

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    values = changes.model_dump(exclude_unset=True)

    # SQLite doesn't check foreign keys by default, so check the room exists
    if values.get("room_id") is not None and session.get(Room, values["room_id"]) is None:
        raise HTTPException(status_code=404, detail="Room not found")

    # Update the stored device
    for field, value in values.items():
        setattr(device, field, value)

    session.add(device)
    session.commit()
    session.refresh(device)

    # Update the loaded device too, if it's loaded
    handler = request.app.state.device_handler

    if "name" in values:
        handler.rename_device(device_id, values["name"])

    if "hidden" in values:
        handler.set_device_hidden(device_id, values["hidden"])

    if "room_id" in values:
        handler.set_device_room(device_id, values["room_id"])

    if "vertical" in values:
        handler.set_device_vertical(device_id, values["vertical"])

    return device
