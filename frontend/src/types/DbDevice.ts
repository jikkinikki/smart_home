// How high up the device is placed, e.g. "high" for ceiling lamps
export type Vertical = "low" | "medium" | "high";

// A device as it is saved in the database (GET /db/devices)
export interface DbDevice {

    id: string,
    name: string,
    type: string,
    source: string | null,
    address: string | null,
    version: string | null,
    disabled: boolean,
    hidden: boolean,      // still loaded, just not shown in device control
    vertical: Vertical | null,  // null = not set
    extra: Record<string, unknown>,
    room_id: number | null
}
