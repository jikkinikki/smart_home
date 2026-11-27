<script setup lang="ts">
import { computed } from 'vue';
import { getStopColor, toCssColor, type RGB } from '@/utils/lightColor';

// Quick picks for a slider. Each dot is colored with the stops' color at its value,
// so it looks like the slider at that spot.
const props = defineProps<{

    stops: [number, RGB][]   // the same stops as the slider's track
    values: number[]         // where on the slider (0-100) each dot is
    selectedValue: number | null  // the dot shown as selected, null = none
}>();

const emits = defineEmits<{

    select: [value: number]
}>();

const presets = computed(() => props.values.map(value => ({ value, color: toCssColor(getStopColor(props.stops, value)) })));

</script>

<template>

    <div class="presets">

        <button v-for="preset in presets" :key="preset.value" class="preset"
            :class="{ presetSelected: selectedValue === preset.value }" :style="{ backgroundColor: preset.color }"
            :title="`${preset.value}%`" @click="emits('select', preset.value)"></button>

        <slot></slot>

    </div>

</template>


<style scoped lang="scss">
.presets {

    display: flex;
    justify-content: space-evenly;
    margin: 6px 0 10px;
}

.preset,
:slotted(.preset) {

    width: 32px;
    aspect-ratio: 1;
    padding: 0;
    border-radius: 1000px;
    border: 1px solid var(--border-medium);
    transition: .2s;
}

.presetSelected,
:slotted(.presetSelected) {

    border-color: var(--border-bright);
    transform: scale(1.15);
}
</style>
