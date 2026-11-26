<script setup lang="ts">
import { computed, ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';

const inRGBMode = ref(false);

const emits = defineEmits<{

    brightness: [value: number]
    hue: [value: number]
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

function getTemperatureColor(temperature: number): RGB {

    for (let i = 1; i < temperatureStops.length; i++) {

        const [pos, color] = temperatureStops[i]!;
        const [prevPos, prevColor] = temperatureStops[i - 1]!;

        if (temperature <= pos) {

            const t = (temperature - prevPos) / (pos - prevPos);
            return prevColor.map((value, c) => value + (color[c]! - value) * t) as RGB;
        }
    }

    return temperatureStops[temperatureStops.length - 1]![1];
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

function onTemperatureChange(value: number) {

    temperature.value = value;
    emits('hue', value);
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

        <LabeledSlider v-if="inRGBMode" class="brightness-slider" label="Color"></LabeledSlider>
        <LabeledSlider v-else @change="onTemperatureChange" class="temperature-slider"
            :style="{ '--track-gradient': temperatureGradient }" label="temperature"></LabeledSlider>

    </div>

</template>


<style scoped lang="scss">
.mode-buttons {

    display: grid;
    grid-template-columns: repeat(2, 1fr);

    height: 40px;
    background-color: black;
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
        background-color: rgba(255, 255, 255, 0.281);
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


    .selectedMode {

        // background-color: gray !important;
    }
}

.back-panel {

    background-color: rgb(40, 39, 39);
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 10px;
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

.temperature-slider {

    :deep(input) {

        &::-webkit-slider-runnable-track {

            // Set from the script (temperatureGradient)
            background: var(--track-gradient);
        }

    }
}


</style>