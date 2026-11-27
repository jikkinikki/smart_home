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
button {
    width: 100px;
    height: 100px;
    border-radius: 1000px;

    transition: .2s;

    box-shadow: 0px 0px 5px 5px var(--shadow);

    padding: 30px;

    img {

        filter: brightness(0) invert(.7);

        height: 100%;
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