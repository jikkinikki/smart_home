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

        <slot></slot>

        <input @input="updateSlider" v-model.number="amount" type="range" name="" id="" min="1" max="100">

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

        width: 100%;
        appearance: none;
        border-radius: 1000px;

        margin-top: 0.5em;

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
            background-color: var(--white);
            border: 3px solid var(--border-medium);
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