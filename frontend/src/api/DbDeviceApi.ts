import { apiRequest } from "./ApiClient";
import type { DbDevice } from "@/types/DbDevice";

export function getDbDevices(): Promise<DbDevice[]> {

    return apiRequest<DbDevice[]>("GET", "api/db/devices");
}
