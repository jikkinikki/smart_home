from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/devices", tags=["Devices"])


def _get_capabilities(device) -> list[str]:
    # Device and Lamp are separate base classes, so not every device has this
    get_capabilities = getattr(device, "get_capabilities", None)
    return get_capabilities() if get_capabilities else []


@router.get("")
def get_devices(request: Request):
    handler = request.app.state.device_handler

    devices = handler.getAllDevices()

    return [
        {
            "id": device.id,
            "name": device.get_device_name(),
            "type": device.type,
            "capabilities": _get_capabilities(device),
        }
        for device in devices
    ]

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

    with ThreadPoolExecutor(max_workers=len(pairs)) as pool:
        results = list(pool.map(lambda p: _apply_values(*p), pairs))

    return {
        "results": results,
        "missing": missing,
    }


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