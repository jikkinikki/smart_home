<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';
import { watch } from 'vue';

import powerIcon from '@/assets/icons/control-power.svg'

const inRGBMode = ref(false);

const isOn = ref(false);

const emits = defineEmits<{

    isOn: [value: boolean]
}>();

watch(isOn, () => {

    emits("isOn", isOn.value);
})


</script>

<template>

    <button @click="isOn = !isOn" :class="{ on: isOn }"><img :src="powerIcon" alt=""></button>

</template>


<style scoped lang="scss">

@use '@/assets/styles/variables' as *;

button {
    width: 100px;
    height: 100px;
    border-radius: 1000px;
    // aspect-ratio: 1;

    transition: .2s;

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