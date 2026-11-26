"""Fetch the devices again (Tuya + Zigbee), see what changed, and apply the chosen changes.

    POST /db/devices/refetch         start fetching (takes a while, runs in the background)
    GET  /db/devices/refetch         state + the changes found
    POST /db/devices/refetch/apply   save the chosen changes and restart the devices
"""
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/db/devices/refetch", tags=["Device refetch"])


class FieldChange(BaseModel):
    field: str          # e.g. "address", "extra.capabilities"
    old: Any
    new: Any


class DeviceChange(BaseModel):
    id: str
    name: str
    source: str | None
    status: Literal["new", "changed"]
    fields: list[FieldChange]


class RefetchStatus(BaseModel):
    state: Literal["idle", "running", "done"]
    started_at: float | None
    finished_at: float | None
    errors: dict[str, str]          # source -> error, e.g. {"tuya": "..."}
    changes: list[DeviceChange]


class ApplyIn(BaseModel):
    ids: list[str]                  # the devices whose changes should be saved


class ApplyOut(BaseModel):
    applied: int


@router.post("", response_model=RefetchStatus)
def start_refetch(request: Request):
    refetch = request.app.state.device_refetch

    if not refetch.start():
        raise HTTPException(status_code=409, detail="Already fetching devices")

    return refetch.get_status()


@router.get("", response_model=RefetchStatus)
def get_refetch(request: Request):
    return request.app.state.device_refetch.get_status()


@router.post("/apply", response_model=ApplyOut)
def apply_refetch(body: ApplyIn, request: Request):
    try:
        applied = request.app.state.device_refetch.apply(body.ids)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {"applied": applied}
