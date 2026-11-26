<script setup lang="ts">
import type { DbDevice, Vertical } from '@/types/DbDevice';
import type { DbDeviceUpdate } from '@/api/DbDeviceApi';
import { ref } from 'vue';

const props = defineProps<{
    device: DbDevice
}>();

// The page does the saving, so the component doesn't talk to the API itself
const emit = defineEmits<{
    save: [deviceId: string, changes: DbDeviceUpdate]
}>();

const isOpen = ref(false);

const newName = ref(props.device.name);
const newHidden = ref(props.device.hidden);
const newVertical = ref<Vertical | null>(props.device.vertical);

function save() {

    emit("save", props.device.id, { name: newName.value, hidden: newHidden.value, vertical: newVertical.value });
    isOpen.value = false;
}

function cancel() {

    newName.value = props.device.name;
    newHidden.value = props.device.hidden;
    newVertical.value = props.device.vertical;
    isOpen.value = false;
}

</script>

<template>

    <div class="device" :class="{ disabled: device.disabled }">

        <div v-if="!isOpen">
            <h3>{{ device.name || "(no name)" }}</h3>
            <p>{{ device.type }} · {{ device.source }}</p>
            <p>{{ device.address }}</p>
            <p class="id">{{ device.id }}</p>
            <p v-if="device.disabled">disabled</p>
            <p>hidden: {{ device.hidden }}</p>
            <p>vertical: {{ device.vertical ?? "not set" }}</p>

            <div class="buttons">
                <button @click="isOpen = true">Edit</button>
            </div>

        </div>

        <div v-else>

            <input class="name-inp" v-model="newName">
            <p>{{ device.type }} · {{ device.source }}</p>
            <p>{{ device.address }}</p>
            <p class="id">{{ device.id }}</p>
            <p v-if="device.disabled">disabled</p>

            <label>
                <input type="checkbox" v-model="newHidden">
                hidden
            </label>

            <label>
                vertical
                <select v-model="newVertical">
                    <option :value="null">not set</option>
                    <option value="low">low</option>
                    <option value="medium">medium</option>
                    <option value="high">high</option>
                </select>
            </label>

            <div class="buttons">
                <button @click="save">Save</button>
                <button @click="cancel">Cancel</button>
            </div>
        </div>

    </div>

</template>

<style lang="scss" scoped>
.device {

    border: 2px solid var(--button-col);
    padding: 8px;
    overflow: hidden;

    h3, .name-inp{

        height: 30px;
        box-sizing: border-box;
    }

    h3,
    p {
        margin: 0;
    }

    label {
        display: block;
    }

    .id {
        font-size: 0.8em;
        opacity: 0.6;
        word-break: break-all;
    }

    .buttons {

        display: flex;
        gap: 4px;

        button {

            flex: 1;
        }

    }
}
</style>
