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
    toggleIsOn, setBrightness, setHue, setColor } = useDevices(props.roomId);

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

    <div class="dynamic-wrapper">

        <div>

            <h2 @click="loadDevices">Devices</h2>

            <div class="select-options">


                <FilterDropdown v-model="activeFilter" :options="verticalFilters" @select="onFilterSelect">
                </FilterDropdown>

                <button class="select-btn" @click="onToggleSelectAll">{{ isAllSelected ? "Deselect all" : "Select all"
                    }}</button>

            </div>

            <div class="devices">

                <button_device :class="{ deviceSelected: getIsSelected(device.id) }" v-for="device in devices"
                    @click="onDeviceClick(device.id)" :device="device">
                </button_device>

            </div>
        </div>

        <div>

            <h2>Adjust</h2>
            <div>
                <LampAdjust @brightness="setBrightness" @hue="setHue" @color="setColor"></LampAdjust>

            </div>

        </div>

        <div class="toggle-active-area">

            <OnOffBtn @isOn="toggleIsOn"></OnOffBtn>

        </div>

    </div>


</template>

<style scoped lang="scss">

@use '@/assets/styles/variables' as *;

h2 {

    text-transform: uppercase;
    font-weight: 300;
    color: var(--text-body);
    font-size: 20px;

    margin: 10px 0px;
}

.devices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 5px;

    margin-bottom: 20px;

    div {

        // background-color: black;
        // box-sizing: border-box;
        border: 2px solid color-mix(in srgb, var(--surface), white 2%);
        box-shadow: 0px 0px 5px 5px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }

    .deviceSelected {

        // background-color: var(--surface);
        border: 2px solid var(--border-bright);
    }
}

.select-options {

    display: flex;
    gap: 5px;
    margin-bottom: 5px;

    flex-direction: row-reverse;

    .select-btn {

        // border-radius: 5px;
        background-color: rgba(0, 0, 0, 0);

        width: 100px;
    }
}

.toggle-active-area {

    display: flex;
    justify-content: space-evenly;
    --width: 100px;


    @media (min-width: $phone-limit) {

        margin-top: 200px;
    }

    @media (max-width: $phone-limit) {

        margin-top: 20px;

        // position: fixed;
        // bottom: 10px;
        // left: calc(50% - var(--width) / 2);
        // z-index: 100;
    }

}
</style>