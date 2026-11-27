<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';

import powerIcon from '@/assets/icons/control-power.svg'

const inRGBMode = ref(false);

// Shown on the button. Clicking only asks for the change, the parent sets isOn.
defineProps<{

    isOn: boolean
}>();

const emits = defineEmits<{

    isOn: [value: boolean]
}>();


</script>

<template>

    <button @click="emits('isOn', !isOn)" :class="{ on: isOn }"><img :src="powerIcon" alt=""></button>

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

    img {

        filter: brightness(0) invert(.7);

        height: 100%;
    }

    @media (max-width: $phone-limit) {

        width: 60px;
        height: 60px;
        padding: 15px;
    }
}

.on {

    background-color: var(--accent);
    color: var(--text-on-accent);

    img {

        filter: brightness(0);
    }
}
</style>