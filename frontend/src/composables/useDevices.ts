import { getDevices, setDevicesValues, type DeviceUpdate } from '@/api/DeviceApi';
import { computed, ref } from 'vue';
import { canToggle, hasCapability, type Device } from '@/types/Device';
import type { Vertical } from '@/types/DbDevice';

// roomId = only load the devices in that room. Leave it out to load all devices.
export function useDevices(roomId?: number) {

    const devices = ref<Device[]>([]);
    const selectedDevices = ref<Device[]>([]);

    async function loadDevices() {
        const allDevices = await getDevices();

        devices.value = roomId === undefined
            ? allDevices
            : allDevices.filter(device => device.room_id == roomId);

        selectedDevices.value.length = 0;

        for (const device of devices.value) {

            selectedDevices.value.push(device);
        }
    }

    function getIsSelected(deviceId: string) {

        return selectedDevices.value.some(device => device.id == deviceId);
    }

    function toggleSelectedDevice(deviceId: string) {

        const isSelected = getIsSelected(deviceId);

        if (isSelected) {

            selectedDevices.value = selectedDevices.value.filter(device => device.id != deviceId);
        }
        else {

            const device = devices.value.find(device => device.id == deviceId);

            if (device) {

                selectedDevices.value.push(device);
            }
        }

    }

    const isAllSelected = computed(() =>
        devices.value.length > 0 && devices.value.every(device => getIsSelected(device.id))
    );

    // Deselects all if everything is selected, otherwise selects all
    function toggleSelectAll() {

        selectedDevices.value = isAllSelected.value ? [] : [...devices.value];
    }

    // Selects only the devices placed at that height
    function selectByVertical(vertical: Vertical) {

        selectedDevices.value = devices.value.filter(device => device.vertical == vertical);
    }

    function toggleIsOn(isOn: boolean) {

        const toggleable = selectedDevices.value.filter(canToggle);

        for (const device of toggleable) {

            device.isOn = isOn;
        }

        updateDevices(toggleable.map(device => ({ id: device.id, isOn })));
    }

    function setHue(hue: number) {

        const hasHue = selectedDevices.value.filter(device => hasCapability(device, "temperature"));

        for (const device of hasHue) {

            device.temperature = hue;
        }

        updateDevices(hasHue.map(device => ({ id: device.id, temperature: hue })));
    }

    function setBrightness(brightness: number) {

        const dimmable = selectedDevices.value.filter(device => hasCapability(device, "brightness"));

        for (const device of dimmable) {

            device.brightness = brightness;
        }

        updateDevices(dimmable.map(device => ({ id: device.id, brightness })));
    }

    function updateDevices(devices: DeviceUpdate[]) {

        setDevicesValues(devices);
    }

    return {
        devices,
        selectedDevices,
        loadDevices,
        getIsSelected,
        toggleSelectedDevice,
        isAllSelected,
        toggleSelectAll,
        selectByVertical,
        toggleIsOn,
        setBrightness,
        setHue
    };
}
