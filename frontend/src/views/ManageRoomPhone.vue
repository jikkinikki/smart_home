<script setup lang="ts">
import button_device from '@/components/button_device.vue';
import LampAdjust from '@/components/LampAdjust.vue';
import { onMounted, ref } from 'vue';
import FilterDropdown from '@/components/FilterDropdown.vue';
import OnOffBtn from '@/components/OnOffBtn.vue';
import { useDevices } from '@/composables/useDevices';
import type { Vertical } from '@/types/DbDevice';

const props = defineProps<{

    roomId?: number  // leave out for all rooms
}>();

const { devices, loadDevices, getIsSelected, toggleSelectedDevice, isAllSelected, toggleSelectAll, selectByVertical,
    toggleIsOn, setBrightness, setHue } = useDevices(props.roomId);

const verticalFilters: { value: Vertical, label: string }[] = [
    { value: "high", label: "High" },
    { value: "medium", label: "Medium" },
    { value: "low", label: "Low" }
];

// The filter shown in the dropdown. Cleared when the selection is changed by hand.
const activeFilter = ref<string | null>(null);

function onFilterSelect(value: string) {

    selectByVertical(value as Vertical);
}

function onToggleSelectAll() {

    toggleSelectAll();
    activeFilter.value = null;
}

function onDeviceClick(deviceId: string) {

    toggleSelectedDevice(deviceId);
    activeFilter.value = null;
}

onMounted(loadDevices);

</script>

<template>

    <div class="wrapper">

        <div class="container">

            <h2 @click="loadDevices">Devices</h2>

            <div class="select-options">

                
                <FilterDropdown v-model="activeFilter" :options="verticalFilters" @select="onFilterSelect">
                </FilterDropdown>

                <button class="select-btn" @click="onToggleSelectAll">{{ isAllSelected ? "Deselect all" : "Select all" }}</button>

            </div>

            <div class="devices">

                <button_device :class="{ deviceSelected: getIsSelected(device.id) }" v-for="device in devices"
                    @click="onDeviceClick(device.id)" :device="device">
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

.select-options {

    display: flex;
    gap: 5px;
    margin-bottom: 5px;

    flex-direction: row-reverse;

    .select-btn{

        // border-radius: 5px;
        background-color: rgba(0, 0, 0, 0);

        width: 100px;
    }
}

.toggle-active-area {

    display: flex;
    justify-content: space-evenly;

    margin-top: 200px;

}
</style>