from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple

from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/devices", tags=["Devices"])


def _get_capabilities(device) -> list[str]:
    # Device and Lamp are separate base classes, so not every device has this
    get_capabilities = getattr(device, "get_capabilities", None)
    return get_capabilities() if get_capabilities else []


@router.get("")
def get_devices(request: Request):
    handler = request.app.state.device_handler

    # Hidden devices are still loaded, they're just not shown in device control
    devices = [device for device in handler.getAllDevices() if not device.hidden]

    return [
        {
            "id": device.id,
            "name": device.get_device_name(),
            "type": device.type,
            "capabilities": _get_capabilities(device),
            "room_id": getattr(device, "room_id", None),
            "vertical": getattr(device, "vertical", None),
        }
        for device in devices
    ]

# Must come before /{device_id}, or "state" would be taken as a device id
@router.get("/state")
def get_devices_state(request: Request, ids: Optional[List[str]] = Query(None)):
    """
    The devices' current values (ids = only these, leave out for all shown devices).
    They come from memory, which is kept up to date in the background (see control/device_states.py).
    A value is null when the device doesn't have it or hasn't answered yet.
    """
    return request.app.state.device_states.get(ids)


@router.get("/{device_id}")
def get_device(device_id: str, request: Request):
    handler = request.app.state.device_handler

    device = handler.getDeviceById(device_id)

    if device == "null":
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "id": device.id,
        "name": device.get_device_name(),
        "type": device.type,
        "capabilities": _get_capabilities(device),
    }


class DeviceValues(BaseModel):
    id: str
    power: Optional[bool] = None
    brightness: Optional[int] = Field(None, ge=0, le=100)
    temperature: Optional[int] = Field(None, ge=0, le=100)
    color: Optional[Tuple[int, int, int]] = None


@router.patch("")
def set_devices_values(updates: List[DeviceValues], request: Request):
    handler = request.app.state.device_handler

    pairs = []
    missing = []
    for values in updates:
        device = handler.getDeviceById(values.id)
        if device == "null":
            missing.append(values.id)
        else:
            pairs.append((device, values))

    if not pairs:
        raise HTTPException(status_code=404, detail="No devices found")

    device_states = request.app.state.device_states

    with ThreadPoolExecutor(max_workers=len(pairs)) as pool:
        results = list(pool.map(lambda p: _apply_and_remember(*p, device_states), pairs))

    return {
        "results": results,
        "missing": missing,
    }


def _apply_and_remember(device, values: DeviceValues, device_states):
    # Remembered while holding the lock, so a state read can't overwrite it with older values
    with device.connection_lock:
        results = _apply_values(device, values)

        capabilities = _get_capabilities(device)
        sent = values.model_dump(exclude={"id"}, exclude_none=True)
        device_states.remember(device, {key: value for key, value in sent.items() if key in capabilities})

    return results


def _apply_values(device, values: DeviceValues):
    results = {}

    if values.power is not None:
        if values.power:
            device.turn_on()
        else:
            device.turn_off()
        results["power"] = True

    if values.brightness is not None:
        results["brightness"] = bool(device.set_brightness(values.brightness))

    if values.temperature is not None:
        results["temperature"] = bool(device.set_temperature(values.temperature))

    if values.color is not None:
        results["color"] = bool(device.set_color(values.color))

    return {
        "id": device.id,
        "results": results,
    }