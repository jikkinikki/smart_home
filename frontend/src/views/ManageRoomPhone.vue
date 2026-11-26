<script setup lang="ts">
import button_device from '@/components/button_device.vue';
import LampAdjust from '@/components/LampAdjust.vue';
import { onMounted } from 'vue';
import OnOffBtn from '@/components/OnOffBtn.vue';
import { useDevices } from '@/composables/useDevices';

const props = defineProps<{

    roomId?: number  // leave out for all rooms
}>();

const { devices, loadDevices, getIsSelected, toggleSelectedDevice, toggleIsOn, setBrightness, setHue } = useDevices(props.roomId);

onMounted(loadDevices);

</script>

<template>

    <div class="wrapper">

        <div class="container">

            <h2 @click="loadDevices">Devices</h2>
            <div class="devices">

                <button_device :class="{ deviceSelected: getIsSelected(device.id) }" v-for="device in devices"
                    @click="toggleSelectedDevice(device.id)" icon="placeholder" :lamp-name="device.name">
                </button_device>

            </div>
            <br>
        </div>

        <div class="container">

            <h2>Adjust</h2>
            <div>
                <LampAdjust @brightness="setBrightness" @hue="setHue"></LampAdjust>

            </div>

        </div>

        <div class="toggle-active-area container">

            <OnOffBtn @isOn="toggleIsOn"></OnOffBtn>

        </div>

    </div>


</template>

<style scoped lang="scss">
@media (min-width: 600px) {
    
    .wrapper{

        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .container {
        
        width: 600px;
        margin-left: -5%;
    }
}

h2 {

    text-transform: uppercase;
}

.devices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 5px;

    div {

        // background-color: black;
        // box-sizing: border-box;
        border: 2px solid var(--button-col);
        overflow: hidden;
    }

    .deviceSelected {

        // background-color: var(--button-col);
        border: 2px solid rgb(195, 195, 195);
    }
}

.toggle-active-area {

    display: flex;
    justify-content: space-evenly;

    margin-top: 200px;

}
</style>