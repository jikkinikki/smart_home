// One field that would change, e.g. { field: "address", old: "0x4F53", new: "0x5A01" }
// Secrets (local_key) only come as "***", so you can see that they changed.
export interface FieldChange {

    field: string,
    old: unknown,
    new: unknown
}

// A device the refetch found that is new or differs from the database
export interface DeviceChange {

    id: string,
    name: string,
    source: string | null,
    status: "new" | "changed",
    fields: FieldChange[]
}

// GET /db/devices/refetch
export interface RefetchStatus {

    state: "idle" | "running" | "done",
    started_at: number | null,      // unix seconds
    finished_at: number | null,
    errors: Record<string, string>, // source -> error, e.g. { tuya: "..." }
    changes: DeviceChange[]
}
