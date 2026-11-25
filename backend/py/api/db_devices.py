"""Devices as they are saved in the database (not the loaded/connected ones in /devices)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from db.database import get_session
from db.models import Device

router = APIRouter(prefix="/db/devices", tags=["Database devices"])


class DbDeviceOut(BaseModel):
    # Everything in the Device row except local_key, which is a secret
    id: str
    name: str
    type: str
    source: str | None
    address: str | None
    version: str | None
    disabled: bool
    extra: dict
    room_id: int | None


@router.get("", response_model=list[DbDeviceOut])
def get_db_devices(session: Session = Depends(get_session)):
    return session.exec(select(Device)).all()
