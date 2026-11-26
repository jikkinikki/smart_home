<script lang="ts" setup>

import { computed, onBeforeUnmount, onMounted, ref } from 'vue';

export interface FilterOption {

    value: string,
    label: string
}

const props = withDefaults(defineProps<{

    options: FilterOption[],
    modelValue?: string | null,  // the picked option's value, null = none picked
    placeholder?: string

}>(), {

    modelValue: null,
    placeholder: "Filter"
});

const emit = defineEmits<{

    "update:modelValue": [value: string],
    select: [value: string]  // also sent when the already picked option is picked again
}>();

const isOpen = ref(false);
const root = ref<HTMLElement | null>(null);

const shownLabel = computed(() =>
    props.options.find(option => option.value == props.modelValue)?.label ?? props.placeholder
);

function hover(option: FilterOption) {

    emit("update:modelValue", option.value);
    emit("select", option.value);
}

function pick(option: FilterOption) {

    hover(option);
    isOpen.value = false;
}

// Close when clicking anywhere outside the dropdown
function onDocumentClick(event: MouseEvent) {

    if (root.value && !root.value.contains(event.target as Node)) {

        isOpen.value = false;
    }
}

onMounted(() => document.addEventListener("click", onDocumentClick));
onBeforeUnmount(() => document.removeEventListener("click", onDocumentClick));

</script>


<template>

    <div ref="root" class="filter-dropdown" :class="{ open: isOpen }">

        <button class="current" :class="{ placeholder: modelValue == null }" @click="isOpen = !isOpen">
            <span>{{ shownLabel }}</span>
            <span class="arrow"></span>
        </button>

        <div v-if="isOpen" class="options">

            <button v-for="option in options" :key="option.value" class="option"
                :class="{ picked: option.value == modelValue }" @mouseenter="hover(option)" @click="pick(option)">
                {{ option.label }}
            </button>

        </div>

    </div>

</template>


<style scoped lang="scss">
.filter-dropdown {

    position: relative;
    display: inline-block;

    button {

        font-family: inherit;
        font-size: 14px;
        cursor: pointer;
    }

    .current {

        min-width: 120px;
        padding: 8px 12px;
        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;

        &.placeholder {

            color: rgb(150, 150, 150);
        }

        .arrow {

            width: 6px;
            height: 6px;

            border-right: 2px solid currentColor;
            border-bottom: 2px solid currentColor;

            transform: translateY(-2px) rotate(45deg);
            transition: transform 0.15s;
        }
    }

    &.open .current .arrow {

        transform: translateY(2px) rotate(-135deg);
    }

    .options {

        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        z-index: 10;

        min-width: 100%;
        padding: 4px;
        box-sizing: border-box;

        background-color: var(--button-col);
        border: 1px solid rgb(60, 60, 60);
        border-radius: 10px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.6);

        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .option {

        padding: 8px 10px;
        border-radius: 7px;

        background-color: transparent;
        text-align: left;

        &:hover {

            background-color: rgb(55, 55, 55);
        }

        &.picked {

            background-color: rgb(70, 70, 70);
        }
    }
}
</style>
