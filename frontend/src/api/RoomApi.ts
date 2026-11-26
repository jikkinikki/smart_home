import { apiRequest } from "./ApiClient";
import type { Room } from "@/types/Room";

// Devices are put in a room with updateDbDevice(id, { room_id })
export function getRooms(): Promise<Room[]> {

    return apiRequest<Room[]>("GET", "api/rooms");
}

export function createRoom(name: string): Promise<Room> {

    return apiRequest<Room>("POST", "api/rooms", { name });
}
