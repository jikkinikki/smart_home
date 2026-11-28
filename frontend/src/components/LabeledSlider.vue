<script setup lang="ts">
import { computed } from 'vue';

// Optional v-model, so a parent can move the slider (e.g. the temperature presets)
const amount = defineModel<number>({ default: 0 });

const min = 1;
const max = 100;

// How far along the track the thumb is, 0-1. Lets a track be filled up to the thumb (--thumb-center).
const thumbProgress = computed(() => (amount.value - min) / (max - min));

const emit = defineEmits<{

    change: [value: number]
}>();

const props = defineProps<{

    label: string
}>();

function updateSlider() {

    emit("change", amount.value);
}

</script>

<template>

    <div class="container">

        <div class="slider-info">
            <p>{{ label }}</p>
            <p>{{ amount }}%</p>
        </div>

        <slot></slot>

        <input @input="updateSlider" v-model.number="amount" type="range" name="" id="" :min="min" :max="max"
            :style="{ '--thumb-progress': thumbProgress }">

    </div>

</template>


<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.container {

    .slider-info {

        display: flex;
        justify-content: space-between
    }

    p {

        margin-top: 0;
        margin-bottom: 0.5em;
        text-transform: capitalize;
    }

    input {

        --thumb-size: 25px;

        // Where the middle of the thumb is on the track. The thumb stays inside the track,
        // so it moves across the track's width minus its own.
        --thumb-center: calc(var(--thumb-size) / 2 + var(--thumb-progress) * (100% - var(--thumb-size)));

        width: 100%;
        appearance: none;
        border-radius: 1000px;

        margin-top: 0.5em;

        &::-webkit-slider-runnable-track {

            height: var(--thumb-size);
            border-radius: 1000px;

        }

        &::-webkit-slider-thumb {
            appearance: none;
            height: var(--thumb-size);
            // transform: translateY(-5px);
            aspect-ratio: 1;

            border-radius: 1000px;
            background-color: var(--white);
            border: 2px solid var(--border-medium);
        }

        // @media (max-width: $phone-limit) {

        //     &::-webkit-slider-runnable-track {

        //         height: 15px;

        //     }

        //     &::-webkit-slider-thumb {

        //         height: 25px;
        //         transform: translateY(-5px);

        //     }
        // }
    }
}
</style>