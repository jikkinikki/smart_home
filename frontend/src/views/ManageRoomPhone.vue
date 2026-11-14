<script setup lang="ts">
import button_device from '@/components/button_device.vue';
import LampAdjust from '@/components/LampAdjust.vue';
import { onMounted } from 'vue';
import OnOffBtn from '@/components/OnOffBtn.vue';
import { useDevices } from '@/composables/useDevices';

const { devices, loadDevices, getIsSelected, toggleSelectedDevice, toggleIsOn, setBrightness } = useDevices();

onMounted(loadDevices);

</script>

<template>

    <div>

        <h2 @click="loadDevices">Devices</h2>
        <div class="devices">

            <button_device :class="{ deviceSelected: getIsSelected(device.id)}" v-for="device in devices" @click="toggleSelectedDevice(device.id)"
                icon="placeholder" :lamp-name="device.name"></button_device>

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

.deviceSelected{

    border: 1px solid white;
}

</style>