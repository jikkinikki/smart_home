import { getDevices, getDevicesState, setDevicesValues, type DeviceUpdate } from '@/api/DeviceApi';
import { computed, ref } from 'vue';
import { canToggle, hasCapability, type Device, type LightMode } from '@/types/Device';
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

        try {
            await loadDevicesState();
        }
        finally {
            // Also when it fails, so the controls still show up
            isStateLoaded.value = true;
        }
    }

    // Becomes true once the devices' values have arrived, so the controls can be built with them
    const isStateLoaded = ref(false);

    // Fills in the devices' current values. After this the values are only changed here,
    // so a value set while the devices were being read is kept.
    async function loadDevicesState() {

        if (devices.value.length == 0)
            return;

        const states = await getDevicesState(devices.value.map(device => device.id));

        for (const state of states) {

            const device = devices.value.find(device => device.id == state.id);

            if (!device)
                continue;

            device.isOn ??= state.power ?? undefined;
            device.brightness ??= state.brightness ?? undefined;
            device.temperature ??= state.temperature ?? undefined;
            device.color ??= state.color ?? undefined;
            device.mode ??= state.mode ?? undefined;
        }

        modeOnLoad.value = getMajorityMode(devices.value);
    }

    // The mode most devices were in when they were loaded. Only set on load,
    // so picking devices afterwards doesn't switch the tab.
    const modeOnLoad = ref<LightMode | undefined>();

    // The selected devices' values put together, for the controls.
    // Brightness, temperature and color are averages of the lamps that aren't off;
    // undefined = none of them has that value (e.g. every selected lamp is off).
    const selectedValues = computed(() => {

        const selected = selectedDevices.value;
        const notOff = selected.filter(device => device.isOn !== false);
        const colors = notOff.map(device => device.color).filter(color => color !== undefined);

        return {
            isOn: selected.some(device => device.isOn),
            brightness: average(notOff.map(device => device.brightness)),
            temperature: average(notOff.map(device => device.temperature)),
            color: colors.length == 0
                ? undefined
                : [0, 1, 2].map(channel => Math.round(average(colors.map(color => color[channel]))!)) as [number, number, number],
            mode: getMajorityMode(selected)
        };
    });

    // The mode most of the devices are in. undefined on a tie or when none is known.
    function getMajorityMode(devices: Device[]): LightMode | undefined {

        const colorCount = devices.filter(device => device.mode == "color").length;
        const temperatureCount = devices.filter(device => device.mode == "temperature").length;

        if (colorCount > temperatureCount)
            return "color";

        if (temperatureCount > colorCount)
            return "temperature";

        return undefined;
    }

    function average(values: (number | undefined)[]): number | undefined {

        const known = values.filter(value => value !== undefined);

        if (known.length == 0)
            return undefined;

        return Math.round(known.reduce((sum, value) => sum + value, 0) / known.length);
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

        setPower(selectedDevices.value, isOn);
    }

    // Turns the given devices on or off (the ones that can be switched)
    function setPower(targets: Device[], isOn: boolean) {

        const toggleable = targets.filter(canToggle);

        for (const device of toggleable) {

            device.isOn = isOn;
        }

        updateDevices(toggleable.map(device => ({ id: device.id, isOn })));
    }

    function setHue(hue: number) {

        const hasHue = selectedDevices.value.filter(device => hasCapability(device, "temperature"));

        for (const device of hasHue) {

            device.temperature = hue;
            device.mode = "temperature";
        }

        updateDevices(hasHue.map(device => ({ id: device.id, temperature: hue })));
    }

    function setColor(color: [number, number, number]) {

        const hasColor = selectedDevices.value.filter(device => hasCapability(device, "color"));

        for (const device of hasColor) {

            device.color = color;
            device.mode = "color";
        }

        updateDevices(hasColor.map(device => ({ id: device.id, color })));
    }

    function setBrightness(brightness: number) {

        setBrightnessFor(selectedDevices.value, brightness);
    }

    // Sets the brightness of the given devices (the ones that can be dimmed)
    function setBrightnessFor(targets: Device[], brightness: number) {

        const dimmable = targets.filter(device => hasCapability(device, "brightness"));

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
        selectedValues,
        modeOnLoad,
        isStateLoaded,
        loadDevices,
        getIsSelected,
        toggleSelectedDevice,
        isAllSelected,
        toggleSelectAll,
        selectByVertical,
        toggleIsOn,
        setPower,
        setBrightness,
        setBrightnessFor,
        setHue,
        setColor
    };
}
