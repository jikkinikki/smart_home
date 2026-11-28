<script setup lang="ts">
import { ref, defineEmits } from 'vue';

import powerIcon from '@/assets/icons/control-power.svg'

const inRGBMode = ref(false);

// Like OnOffBtn, but also fills from the bottom to fillPercent (0-100), e.g. how many lamps are on.
// Clicking only asks for the change, the parent sets isOn.
defineProps<{

    isOn: boolean,
    fillPercent: number
}>();

const emits = defineEmits<{

    isOn: [value: boolean]
}>();


</script>

<template>

    <button @click="emits('isOn', !isOn)" :class="{ on: isOn }" :style="{ '--fill': `${fillPercent}%` }">

        <img :src="powerIcon" alt="">

        <!-- The "on" look (orange + dark icon) over the whole button, cut off from the top down to the fill -->
        <span class="fill"><img :src="powerIcon" alt=""></span>

    </button>

</template>


<style scoped lang="scss">

@use '@/assets/styles/variables' as *;

button {
    width: 80px;
    height: 80px;
    border-radius: 1000px;
    // aspect-ratio: 1;

    transition: .2s;

    background-color: var(--surface-light);

    box-shadow: 0px 0px 5px 5px var(--shadow);

    padding: 30px;

    position: relative;
    overflow: hidden;

    // Flex centers both icons the same way, so they line up exactly
    display: flex;
    align-items: center;
    justify-content: center;

    img {

        filter: brightness(0) invert(.7);

        height: 100%;
    }

    .fill {

        position: absolute;
        inset: 0;
        padding: inherit;
        box-sizing: border-box;

        display: flex;
        align-items: center;
        justify-content: center;

        background-color: var(--accent);

        // Hides the top part, so only the bottom fillPercent shows
        clip-path: inset(calc(100% - var(--fill)) 0 0 0);
        transition: clip-path .3s;

        img {

            filter: brightness(0);
        }
    }

    @media (max-width: $phone-limit) {

        width: 60px;
        height: 60px;
        padding: 15px;
    }
}
</style>