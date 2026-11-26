import { apiRequest } from "./ApiClient";
import type { DbDevice } from "@/types/DbDevice";

export function getDbDevices(): Promise<DbDevice[]> {

    return apiRequest<DbDevice[]>("GET", "api/db/devices");
}

// The fields that can be edited. Fields left out are not changed.
export type DbDeviceUpdate = Partial<Pick<DbDevice, "name">>;

// Saves the changes in the database (and on the loaded device). Returns the saved device.
export function updateDbDevice(deviceId: string, changes: DbDeviceUpdate): Promise<DbDevice> {

    return apiRequest<DbDevice>("PATCH", `api/db/devices/${encodeURIComponent(deviceId)}`, changes);
}
