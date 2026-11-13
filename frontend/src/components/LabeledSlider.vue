<script setup lang="ts">
import { ref } from 'vue';

const amount = ref(0);

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

        <input @input="updateSlider" v-model.number="amount" type="range" name="" id="" min="0" max="100">

    </div>

</template>


<style scoped lang="scss">
.container {

    .slider-info {

        display: flex;
        justify-content: space-between
    }

    input {

        width: 100%;
        appearance: none;
        border-radius: 1000px;
        
        &::-webkit-slider-runnable-track {
            
            height: 20px;
            border-radius: 1000px;
            
        }
        
        &::-webkit-slider-thumb {
            appearance: none;
            height: 30px;
            transform: translateY(-5px);
            aspect-ratio: 1;
            
            border-radius: 1000px;
            background-color: white;
            border: 3px solid gray;
        }
    }
}
</style>