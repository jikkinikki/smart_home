<script setup lang="ts">
import button_device from '@/components/button_device.vue';
import LampAdjust from '@/components/LampAdjust.vue';
import { computed, onMounted, ref } from 'vue';
import { getTemperatureColor, toCssColor, type RGB } from '@/utils/lightColor';
import FilterDropdown from '@/components/FilterDropdown.vue';
import OnOffBtn from '@/components/OnOffBtn.vue';
import { useDevices } from '@/composables/useDevices';
import type { Vertical } from '@/types/DbDevice';

const props = defineProps<{

    roomId?: number  // leave out for all rooms
}>();

const { devices, selectedValues, modeOnLoad, isStateLoaded, loadDevices, getIsSelected, toggleSelectedDevice, isAllSelected, toggleSelectAll, selectByVertical,
    toggleIsOn, setPower, setBrightness, setBrightnessFor, setHue, setColor } = useDevices(props.roomId);

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

// The color the selected lamps are giving off, for the dot next to the power button.
// undefined = unknown, the dot keeps its default color.
const lightColor = computed(() => {

    const { mode, color, temperature } = selectedValues.value;

    let rgb: RGB | undefined;

    if (mode == "color" && color)
        rgb = color;
    else if (temperature !== undefined)
        rgb = getTemperatureColor(temperature);
    else
        rgb = color;

    return rgb ? toCssColor(rgb) : undefined;
});

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

            <!-- Built once the values are in, so each device starts showing the right on/off instead of off -->
            <div v-if="isStateLoaded" class="devices">

                <button_device :class="{ deviceSelected: getIsSelected(device.id) }" v-for="device in devices"
                    @click="onDeviceClick(device.id)" @power="(isOn) => setPower([device], isOn)"
                    @brightness="(value) => setBrightnessFor([device], value)" :device="device">
                </button_device>

            </div>
        </div>

        <div>

            <h2>Adjust</h2>
            <div>
                <!-- Built once the values are in, so the tab and sliders start in the right place without sliding there -->
                <LampAdjust v-if="isStateLoaded" :deviceBrightness="selectedValues.brightness" :deviceTemperature="selectedValues.temperature"
                    :deviceColor="selectedValues.color" :modeOnLoad="modeOnLoad" @brightness="setBrightness" @hue="setHue" @color="setColor">
                </LampAdjust>

            </div>

        </div>

        <div class="toggle-active-area">

            <div class="info">
                <div class="color-div" :style="lightColor ? { backgroundColor: lightColor } : {}"></div>

                <p>{{ selectedValues.isOn ? "On" : "Off" }} {{ selectedValues.brightness ?? "-" }}%</p>
            </div>

            <OnOffBtn :isOn="selectedValues.isOn" @isOn="toggleIsOn"></OnOffBtn>

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

        background-color: rgba(0, 0, 0, 0);

        width: 100px;
    }
}

.toggle-active-area {

    display: flex;
    justify-content: space-between;
    // --width: 100px;

    background-color: var(--surface);

    padding: 10px 10px;
    border-radius: 10px;
    box-sizing: border-box;

    box-shadow: 0px 0px 5px 5px rgba(0, 0, 0, 0.137);

    margin-bottom: 50px;

    .info {

        display: flex;
        align-items: center;
        gap: 10px;


        .color-div {

            width: 40px;
            border-radius: 1000px;
            aspect-ratio: 1;
            background-color: orange;
            box-shadow: 0px 0px 5px 5px rgba(205, 205, 28, 0.137);

        }

        p {
            display: inline;
        }
    }

    @media (min-width: $phone-limit) {

        margin-top: 200px;
    }

    @media (max-width: $phone-limit) {

        margin-top: 10px;

        // position: fixed;
        // bottom: 10px;
        // left: calc(50% - var(--width) / 2);
        // z-index: 100;
    }

}
</style>