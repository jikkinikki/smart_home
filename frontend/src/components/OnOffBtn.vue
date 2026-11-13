<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import LabeledSlider from './LabeledSlider.vue';
import { watch } from 'vue';

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

    <button @click="isOn = !isOn" :class="{ on: isOn }">O</button>

</template>


<style scoped lang="scss">
button {
    width: 100px;
    height: 100px;
    border-radius: 1000px;


    transition: .2s;
}

.on {

    background-color: orange;
    color: black;
}
</style>