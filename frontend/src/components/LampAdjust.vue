<script setup lang="ts">
import { ref, watch, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';
import ColorPresets from './ColorPresets.vue';
import type { LightMode } from '@/types/Device';
import { colorGradient, colorStops, getHueColor, getHuePosition, hexToRgb, temperatureGradient,
    temperatureStops, type RGB } from '@/utils/lightColor';

const inRGBMode = ref(false);

const emits = defineEmits<{

    brightness: [value: number]
    hue: [value: number]
    color: [value: [number, number, number]]
}>();

// The values the selected devices have, shown on the sliders. undefined = unknown, the slider stays where it is.
const props = defineProps<{

    deviceBrightness?: number
    deviceTemperature?: number
    deviceColor?: RGB
    deviceMode?: LightMode  // opens that tab
}>();

watch(() => props.deviceMode, mode => {

    if (mode !== undefined)
        inRGBMode.value = mode == "color";
}, { immediate: true });

// Starts at 0, same as the slider
const brightness = ref(0);
const temperature = ref(0);
const hue = ref(0);

watch(() => props.deviceBrightness, value => {

    if (value !== undefined)
        brightness.value = value;
}, { immediate: true });

watch(() => props.deviceTemperature, value => {

    if (value !== undefined)
        temperature.value = value;
}, { immediate: true });

watch(() => props.deviceColor, value => {

    if (value !== undefined)
        hue.value = getHuePosition(value);
}, { immediate: true });

function onHueChange(value: number) {

    hue.value = value;
    emits('color', getHueColor(value));
}

function onTemperatureChange(value: number) {

    temperature.value = value;
    emits('hue', value);
}

// Where the quick picks above the sliders are. Starts at 1, the slider's min.
const temperaturePresetValues = [1, 25, 50, 75, 100];

// Red, yellow, green, cyan, blue: the main points of colorStops (rounded, the slider only does whole numbers).
// The last dot is a color picker instead (see pickedColor).
const colorPresetValues = [1, 17, 33, 50, 67];

// The color from the picker as "#rrggbb", null when the slider/presets are in use
const pickedColor = ref<string | null>(null);

function onColorPicked(hex: string) {

    pickedColor.value = hex;
    emits('color', hexToRgb(hex));
}

function onColorSliderChange(value: number) {

    pickedColor.value = null;
    onHueChange(value);
}


</script>

<template>

    <div class="back-panel">

        <LabeledSlider v-model="brightness" @change="(value) => emits('brightness', value)" class="brightness-slider"
            label="Brightness"></LabeledSlider>
    </div>

    <div class="back-panel">

        <div class="mode-buttons">

            <button :class="{ selectedMode: inRGBMode }" @click="inRGBMode = true">Color</button>
            <button :class="{ selectedMode: !inRGBMode }" @click="inRGBMode = false">Temperature</button>

            <div class="mode-marker" :class="{ modeRight: !inRGBMode }"></div>

        </div>

        <LabeledSlider v-if="inRGBMode" v-model="hue" @change="onColorSliderChange" class="color-slider"
            :style="{ '--track-gradient': colorGradient }" label="Color">

            <ColorPresets :stops="colorStops" :values="colorPresetValues" :selectedValue="pickedColor ? null : hue"
                @select="onColorSliderChange">

                <!-- Rainbow until a color is picked, then shows that color. The invisible input on top opens the picker. -->
                <label class="preset color-picker" :class="{ presetSelected: pickedColor }"
                    :style="pickedColor ? { background: pickedColor } : {}" title="Pick a color">

                    <input type="color" :value="pickedColor ?? '#ffffff'"
                        @input="onColorPicked(($event.target as HTMLInputElement).value)">
                </label>

            </ColorPresets>

        </LabeledSlider>

        <LabeledSlider v-else v-model="temperature" @change="onTemperatureChange" class="temperature-slider"
            :style="{ '--track-gradient': temperatureGradient }" label="temperature">

            <ColorPresets :stops="temperatureStops" :values="temperaturePresetValues" :selectedValue="temperature"
                @select="onTemperatureChange">
            </ColorPresets>

        </LabeledSlider>

    </div>

</template>


<style scoped lang="scss">
.mode-buttons {

    display: grid;
    grid-template-columns: repeat(2, 1fr);

    height: 40px;
    background-color: var(--black);
    border-radius: 10px;
    margin-bottom: .5em;

    position: relative;
    top: 0px;

    button {

        background-color: rgba(0, 0, 0, 0);

        position: relative;
        top: 0px;
        z-index: 3;
    }

    .mode-marker {

        --inset: 4px;
        background-color: var(--surface-light);
        width: calc(50% - var(--inset) * 2);
        height: calc(100% - var(--inset) * 2);

        margin-left: var(--inset);
        margin-top: var(--inset);

        border-radius: 7px;

        transition: .2s;

        z-index: 2;

        position: absolute;
        top: 0px;
        left: 0%;
    }

    .modeRight {

        left: 50%;
    }
}

.back-panel {

    background-color: var(--surface);
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 10px;

    box-shadow: 0px 0px 5px 5px var(--shadow);

}

.brightness-slider {

    :deep(input) {

        &::-webkit-slider-runnable-track {

            // Filled up to the current value, empty after it
            background: linear-gradient(90deg, var(--slider-fill) var(--fill-end), var(--surface-light) var(--fill-end));
        }

        &::-webkit-slider-thumb {

            background-color: rgba(0, 0, 0, 0);
            border: none;
        }

    }
}

.color-picker {

    position: relative;
    overflow: hidden;
    cursor: pointer;
    background: conic-gradient(red, yellow, lime, cyan, blue, magenta, red);

    input {

        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
    }
}

.temperature-slider, .color-slider {

    :deep(input) {

        &::-webkit-slider-runnable-track {

            // Set from the script (temperatureGradient / colorGradient)
            background: var(--track-gradient);
        }
    }
}

</style>