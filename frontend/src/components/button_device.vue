<script setup lang="ts">

import placeholderIcon from "@/assets/icons/lights-all.svg";
import ceilingIcon from "@/assets/icons/lamp-ceiling.svg";
import deskIcon from "@/assets/icons/lamp-floor.svg";
import floorIcon from "@/assets/icons/lamp-desk.svg";
import lampDefault from "@/assets/icons/lamp-bulb.svg";

import { canToggle, type Device } from "@/types/Device";
import type { Vertical } from "@/types/DbDevice";

const lampIcons: Record<Vertical, string> = {

    high: ceilingIcon,
    medium: deskIcon,
    low: floorIcon
}

const props = defineProps<{
    device: Device
}>();

// Asks to turn this device on or off, the parent does it and updates device.isOn
const emit = defineEmits<{

    power: [isOn: boolean]
}>();

function getDeviceIcon() {

    const { type, vertical } = props.device;

    if (type != "lamp") {

        return placeholderIcon;
    }

    if (!vertical) {

        return lampDefault;
    }

    return lampIcons[vertical];
}

</script>

<template>

    <div class="button-wrapper">

        <!-- .stop so switching it doesn't also select/deselect the device -->
        <button class="icon" :class="{ on: device.isOn }" :disabled="!canToggle(device)"
            @click.stop="emit('power', !device.isOn)">

            <img :src="getDeviceIcon()" alt="">

        </button>

        <p class="device-name">{{ device.name.replaceAll("_", " ") }}</p>

    </div>

</template>

<style scoped>

.button-wrapper {

    min-width: 100px;

    padding: 10px;
    box-sizing: border-box;

    background-color: var(--surface);

    border-radius: 10px;

    display: flex;
    align-items: center;
    gap: 6px;

    /* Same on/off look as OnOffBtn */
    .icon {

        height: 100%;
        aspect-ratio: 1;
        padding: 0;
        background-color: var(--surface-light);
        border-radius: 1000px;
        cursor: pointer;
        transition: .2s;

        img {

            --width: 60%;

            margin: calc((100% - var(--width)) / 2);
            width: var(--width);

            filter: brightness(0) invert(.7);
        }

        &.on {

            background-color: var(--accent);

            img {

                filter: brightness(0);
            }
        }

        &:disabled {

            cursor: default;
        }
    }

    .device-name {

        margin: 7px 0px;
        display: inline;

        text-transform: capitalize;
    }
}
</style>