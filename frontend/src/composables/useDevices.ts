import { getDevices, setDevicesValues, type DeviceUpdate } from '@/api/DeviceApi';
import { ref } from 'vue';
import { canToggle, hasCapability, type Device } from '@/types/Device';

export function useDevices() {

    const devices = ref<Device[]>([]);
    const selectedDevices = ref<Device[]>([]);

    async function loadDevices() {
        devices.value = await getDevices();

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

    function toggleIsOn(isOn: boolean) {

        const toggleable = selectedDevices.value.filter(canToggle);

        for (const device of toggleable) {

            device.isOn = isOn;
        }

        updateDevices(toggleable.map(device => ({ id: device.id, isOn })));
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
        toggleIsOn,
        setBrightness,
    };
}
