<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';

const inRGBMode = ref(false);

const emits = defineEmits<{

    brightness: [value: number]
}>();


</script>

<template>

    <div class="back-panel">

        <LabeledSlider @change="(brightness) => emits('brightness', brightness)" class="brightness-slider" label="Brightness"></LabeledSlider>
    </div>

    <div class="back-panel">

        <div class="mode-buttons">

            <button :class="{ selectedMode: inRGBMode }" @click="inRGBMode = true">Color</button>
            <button :class="{ selectedMode: !inRGBMode }" @click="inRGBMode = false">Temperature</button>

            <div class="mode-marker" :class="{ modeRight: !inRGBMode }"></div>

        </div>

        <LabeledSlider v-if="inRGBMode" class="brightness-slider" label="Color"></LabeledSlider>
        <LabeledSlider v-else class="brightness-slider" label="temperature"></LabeledSlider>

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

            background: linear-gradient(90deg, rgb(49, 48, 48), yellow);
        }

    }
}


</style>