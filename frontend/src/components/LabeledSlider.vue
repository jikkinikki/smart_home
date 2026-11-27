<script setup lang="ts">
// Optional v-model, so a parent can move the slider (e.g. the temperature presets)
const amount = defineModel<number>({ default: 0 });

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

        <!-- Optional extras between the label and the slider (e.g. preset buttons) -->
        <slot></slot>

        <input @input="updateSlider" v-model.number="amount" type="range" name="" id="" min="1" max="100">

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