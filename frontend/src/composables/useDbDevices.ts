import { getDbDevices, updateDbDevice, type DbDeviceUpdate } from '@/api/DbDeviceApi';
import { ref } from 'vue';
import type { DbDevice } from '@/types/DbDevice';

export function useDbDevices() {

    const devices = ref<DbDevice[]>([]);
    const error = ref<string | null>(null);

    async function loadDevices() {

        try {
            devices.value = await getDbDevices();
            error.value = null;
        }
        catch (e) {
            error.value = e instanceof Error ? e.message : String(e);
        }
    }

    function getDeviceById(deviceId: string) {

        return devices.value.find(device => device.id == deviceId);
    }

    async function updateDevice(deviceId: string, changes: DbDeviceUpdate) {

        try {
            const saved = await updateDbDevice(deviceId, changes);
            const index = devices.value.findIndex(device => device.id == deviceId);

            if (index != -1) {
                devices.value[index] = saved;
            }

            error.value = null;
        }
        catch (e) {
            error.value = e instanceof Error ? e.message : String(e);
        }
    }

    return {
        devices,
        error,
        loadDevices,
        getDeviceById,
        updateDevice
    };
}
