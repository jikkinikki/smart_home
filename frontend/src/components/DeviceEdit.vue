<script setup lang="ts">
import type { DbDevice } from '@/types/DbDevice';
import { ref } from 'vue';

let isOpen = ref(false);

defineProps<{
    device: DbDevice
}>();

</script>

<template>

    <div class="device" :class="{ disabled: device.disabled }">

        <div @click="isOpen = true" v-if="!isOpen">
            <h3>{{ device.name || "(no name)" }}</h3>
            <p>{{ device.type }} · {{ device.source }}</p>
            <p>{{ device.address }}</p>
            <p class="id">{{ device.id }}</p>
            <p v-if="device.disabled">disabled</p>
        </div>

        <div v-else>

            <input :value="device.name">
            <p>{{ device.type }} · {{ device.source }}</p>
            <p>{{ device.address }}</p>
            <p class="id">{{ device.id }}</p>
            <p v-if="device.disabled">disabled</p>

            <div>
                <button>Save</button>
                <button @click="isOpen = false">Cancel</button>
            </div>
        </div>

    </div>

</template>

<style lang="scss" scoped>
.device {

    border: 2px solid var(--button-col);
    padding: 8px;
    overflow: hidden;

    h3,
    p {
        margin: 0;
    }

    .id {
        font-size: 0.8em;
        opacity: 0.6;
        word-break: break-all;
    }
}
</style>
