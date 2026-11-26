"""Rooms. Devices are put in a room with PATCH /db/devices/{id} {"room_id": ...}."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from db.database import get_session
from db.models import Room

router = APIRouter(prefix="/rooms", tags=["Rooms"])


class RoomOut(BaseModel):
    id: int
    name: str


class RoomIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def check_name(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("name can't be empty")
        return name


@router.get("", response_model=list[RoomOut])
def get_rooms(session: Session = Depends(get_session)):
    return session.exec(select(Room).order_by(Room.name)).all()


@router.post("", response_model=RoomOut, status_code=201)
def create_room(room: RoomIn, session: Session = Depends(get_session)):
    if session.exec(select(Room).where(Room.name == room.name)).first() is not None:
        raise HTTPException(status_code=409, detail=f"A room called '{room.name}' already exists")

    new_room = Room(name=room.name)
    session.add(new_room)
    session.commit()
    session.refresh(new_room)

    return new_room
