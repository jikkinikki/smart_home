<script setup lang="ts">
import button_device from '@/components/button_device.vue';
import LampAdjust from '@/components/LampAdjust.vue';
import { getDevices, setDevicesValues, type DeviceUpdate } from '@/api/DeviceApi';
import { onMounted, ref } from 'vue';
import { canToggle, hasCapability, type Device } from '@/types/Device';
import OnOffBtn from '@/components/OnOffBtn.vue';

const devices = ref<Device[]>([]);
const selectedDevices = ref<Device[]>([]);

async function loadDevices() {
    devices.value = await getDevices();

    selectedDevices.value.length = 0;

    for (const device of devices.value) {

        selectedDevices.value.push(device);
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

onMounted(loadDevices);

</script>

<template>

    <div>

        <h2 @click="loadDevices">Devices</h2>
        <div class="devices">

            <button_device v-for="device in devices" icon="placeholder" :lamp-name="device.name"></button_device>

        </div>
        <br>
    </div>

    <div>

        <h2>Adjust</h2>
        <div>
            <LampAdjust @brightness="setBrightness"></LampAdjust>

        </div>

    </div>

    <div class="toggle-active-area">

        <OnOffBtn @isOn="toggleIsOn"></OnOffBtn>

    </div>

</template>

<style scoped lang="scss">
div {

    margin-left: 10%;

    max-width: 600px;
}

h2 {

    text-transform: uppercase;
}

.devices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 5px;
}

.toggle-active-area {

    display: flex;
    justify-content: space-evenly;

    margin-top: 200px;

}
</style>