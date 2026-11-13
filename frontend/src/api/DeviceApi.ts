import { apiRequest } from "./ApiClient";
import type { Device } from "@/types/Device";

export function getDevices(): Promise<Device[]> {

    return apiRequest<Device[]>("GET", "api/devices");
}

// A device id plus only the values that should change
export type DeviceUpdate = Pick<Device, "id"> & Partial<Pick<Device, "isOn" | "brightness" | "temperature" | "color">>;

// Values left undefined are not sent, so the device keeps its current value

let lastUpdate = 0;
const waitTime = 100;
const waiting = new Map<string, DeviceUpdate>();
let delayedFunc: null | ReturnType<typeof setTimeout> = null;

export function setDevicesValues(devices: DeviceUpdate[]): void {

    // Merge into pending updates so different values for the same device aren't lost
    for (const device of devices) {
        waiting.set(device.id, { ...waiting.get(device.id), ...device });
    }

    const deltaTime = Date.now() - lastUpdate;

    if (deltaTime < waitTime) {

        if (delayedFunc == null)
            delayedFunc = setTimeout(() => {
                delayedFunc = null;
                setDevicesValues([]);
            }, waitTime - deltaTime);

        return;
    }

    lastUpdate = Date.now();

    const body = [...waiting.values()].map(device => ({
        id: device.id,
        power: device.isOn,
        brightness: device.brightness,
        temperature: device.temperature,
        color: device.color,
    }));

    waiting.clear();

    if (body.length > 0)
        apiRequest("PATCH", "api/devices", body);
}
