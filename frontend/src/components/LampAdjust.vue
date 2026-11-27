<script setup lang="ts">
import { computed, ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';

const inRGBMode = ref(false);

const emits = defineEmits<{

    brightness: [value: number]
    hue: [value: number]
    color: [value: [number, number, number]]
}>();

type RGB = [number, number, number];

// The light's color at a temperature. 0 = warmest (~2200K, amber), 100 = coolest (~6500K, daylight).
// Also used for the temperature slider's track, keep them the same.
const temperatureStops: [number, RGB][] = [
    [0, [255, 147, 44]],
    [12, [255, 169, 87]],
    [30, [255, 196, 137]],
    [53, [255, 219, 186]],
    [77, [255, 236, 224]],
    [100, [235, 242, 255]]
];

// The color wheel unrolled: full-saturation hues, red -> yellow -> green -> cyan -> blue -> magenta -> red.
// Also used for the color slider's track, so the track shows exactly the color we send.
const colorStops: [number, RGB][] = [
    [0, [255, 0, 0]],
    [100 / 6, [255, 255, 0]],
    [200 / 6, [0, 255, 0]],
    [300 / 6, [0, 255, 255]],
    [400 / 6, [0, 0, 255]],
    [500 / 6, [255, 0, 255]],
    [100, [255, 0, 0]]
];

// How bright the light looks at a brightness. Our eyes see dim light as brighter
// than it is, so it rises fast at the start and slower at the end.
const brightnessStops: [number, number][] = [
    [0, 0.1],
    [10, 0.35],
    [25, 0.54],
    [50, 0.735],
    [100, 1]
];

// Starts at 0, same as the slider
const temperature = ref(0);
const hue = ref(0);

// The color at a position (0-100) between the stops
function getStopColor(stops: [number, RGB][], position: number): RGB {

    for (let i = 1; i < stops.length; i++) {

        const [pos, color] = stops[i]!;
        const [prevPos, prevColor] = stops[i - 1]!;

        if (position <= pos) {

            const t = (position - prevPos) / (pos - prevPos);
            return prevColor.map((value, c) => value + (color[c]! - value) * t) as RGB;
        }
    }

    return stops[stops.length - 1]![1];
}

function getTemperatureColor(temperature: number): RGB {

    return getStopColor(temperatureStops, temperature);
}

function toCss(gradient: string[]) {

    return `linear-gradient(90deg, ${gradient.join(", ")})`;
}

// The temperature's color, from dim to full brightness
const brightnessGradient = computed(() => {

    const color = getTemperatureColor(temperature.value);

    return toCss(brightnessStops.map(([pos, amount]) => {

        const [r, g, b] = color.map(value => Math.round(value * amount));
        return `rgb(${r}, ${g}, ${b}) ${pos}%`;
    }));
});

const temperatureGradient = toCss(temperatureStops.map(([pos, [r, g, b]]) => `rgb(${r}, ${g}, ${b}) ${pos}%`));
const colorGradient = toCss(colorStops.map(([pos, [r, g, b]]) => `rgb(${r}, ${g}, ${b}) ${pos}%`));

function onHueChange(value: number) {

    hue.value = value;
    emits('color', getStopColor(colorStops, value).map(Math.round) as RGB);
}

function onTemperatureChange(value: number) {

    temperature.value = value;
    emits('hue', value);
}

// Quick picks above the sliders. Each dot is colored with the same
// value it sends, so it looks like the slider at that spot. Starts at 1, the slider's min.
function makePresets(stops: [number, RGB][], values: number[]) {

    return values.map(value => {

        const [r, g, b] = getStopColor(stops, value).map(Math.round);
        return { value, color: `rgb(${r}, ${g}, ${b})` };
    });
}

const temperaturePresets = makePresets(temperatureStops, [1, 25, 50, 75, 100]);

// Red, yellow, green, cyan, blue: the main points of colorStops (rounded, the slider only does whole numbers).
// The last dot is a color picker instead (see pickedColor).
const colorPresets = makePresets(colorStops, [1, 17, 33, 50, 67]);

// The color from the picker as "#rrggbb", null when the slider/presets are in use
const pickedColor = ref<string | null>(null);

function onColorPicked(hex: string) {

    pickedColor.value = hex;
    const value = parseInt(hex.slice(1), 16);
    emits('color', [(value >> 16) & 255, (value >> 8) & 255, value & 255]);
}

function onColorSliderChange(value: number) {

    pickedColor.value = null;
    onHueChange(value);
}


</script>

<template>

    <div class="back-panel">

        <LabeledSlider @change="(brightness) => emits('brightness', brightness)" class="brightness-slider"
            :style="{ '--track-gradient': brightnessGradient }" label="Brightness"></LabeledSlider>
    </div>

    <div class="back-panel">

        <div class="mode-buttons">

            <button :class="{ selectedMode: inRGBMode }" @click="inRGBMode = true">Color</button>
            <button :class="{ selectedMode: !inRGBMode }" @click="inRGBMode = false">Temperature</button>

            <div class="mode-marker" :class="{ modeRight: !inRGBMode }"></div>

        </div>

        <LabeledSlider v-if="inRGBMode" v-model="hue" @change="onColorSliderChange" class="color-slider"
            :style="{ '--track-gradient': colorGradient }" label="Color">

            <div class="presets">

                <button v-for="preset in colorPresets" :key="preset.value" class="preset"
                    :class="{ presetSelected: !pickedColor && hue === preset.value }"
                    :style="{ backgroundColor: preset.color }" :title="`${preset.value}%`"
                    @click="onColorSliderChange(preset.value)"></button>

                <!-- Rainbow until a color is picked, then shows that color. The invisible input on top opens the picker. -->
                <label class="preset color-picker" :class="{ presetSelected: pickedColor }"
                    :style="pickedColor ? { background: pickedColor } : {}" title="Pick a color">

                    <input type="color" :value="pickedColor ?? '#ffffff'"
                        @input="onColorPicked(($event.target as HTMLInputElement).value)">
                </label>

            </div>

        </LabeledSlider>

        <LabeledSlider v-else v-model="temperature" @change="onTemperatureChange" class="temperature-slider"
            :style="{ '--track-gradient': temperatureGradient }" label="temperature">

            <div class="presets">

                <button v-for="preset in temperaturePresets" :key="preset.value" class="preset"
                    :class="{ presetSelected: temperature === preset.value }"
                    :style="{ backgroundColor: preset.color }" :title="`${preset.value}%`"
                    @click="onTemperatureChange(preset.value)"></button>

            </div>

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

            // Set from the script (brightnessGradient), it follows the temperature.
            // The Color slider also has this class but no gradient yet, so it uses the fallback.
            background: var(--track-gradient, linear-gradient(90deg, rgb(49, 48, 48), yellow));
        }

    }
}

.presets {

    display: flex;
    justify-content: space-evenly;
    margin: 6px 0 10px;

    .preset {

        width: 32px;
        aspect-ratio: 1;
        padding: 0;
        border-radius: 1000px;
        border: 1px solid var(--border-medium);
        transition: .2s;
    }

    .presetSelected {

        border-color: var(--border-bright);
        transform: scale(1.15);
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
}

.temperature-slider,
.color-slider {

    :deep(input) {

        &::-webkit-slider-runnable-track {

            // Set from the script (temperatureGradient / colorGradient)
            background: var(--track-gradient);
        }

    }
}


</style>