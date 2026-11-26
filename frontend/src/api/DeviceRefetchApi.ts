import { apiRequest } from "./ApiClient";
import type { RefetchStatus } from "@/types/DeviceRefetch";

// Starts fetching the devices again (Tuya + Zigbee). Runs in the background, poll getRefetch.
export function startRefetch(): Promise<RefetchStatus> {

    return apiRequest<RefetchStatus>("POST", "api/db/devices/refetch");
}

export function getRefetch(): Promise<RefetchStatus> {

    return apiRequest<RefetchStatus>("GET", "api/db/devices/refetch");
}

// Saves the changes of these devices and restarts all devices with the new data
export function applyRefetch(deviceIds: string[]): Promise<{ applied: number }> {

    return apiRequest<{ applied: number }>("POST", "api/db/devices/refetch/apply", { ids: deviceIds });
}
