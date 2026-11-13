// What a device can do. Names match the backend's PATCH /devices fields.
export type Capability = "power" | "brightness" | "temperature" | "color";

export interface Device {

    id: string,
    name: string,
    type: string,
    capabilities: Capability[],

    isOn?: boolean,
    brightness?: number,
    temperature?: number,
    color?: [number, number, number]
}

export function hasCapability(device: Device, capability: Capability): boolean {

    return device.capabilities.includes(capability);
}

export function canToggle(device: Device): boolean {

    return hasCapability(device, "power");
}
