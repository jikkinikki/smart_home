<script setup lang="ts">

import placeholderIcon from "@/assets/icons/lights-all.svg";
import ceilingIcon from "@/assets/icons/lamp-ceiling.svg";
import deskIcon from "@/assets/icons/lamp-floor.svg";
import floorIcon from "@/assets/icons/lamp-desk.svg";
import lampDefault from "@/assets/icons/lamp-bulb.svg";

import type { Device } from "@/types/Device";
import type { Vertical } from "@/types/DbDevice";

const lampIcons: Record<Vertical, string> = {

    high: ceilingIcon,
    medium: deskIcon,
    low: floorIcon
}

const props = defineProps<{
    device: Device
}>();

function getDeviceIcon() {

    const { type, vertical } = props.device;

    // Not a lamp, e.g. an outlet
    if (type != "lamp") {

        return placeholderIcon;
    }

    // A lamp with no height set
    if (!vertical) {

        return lampDefault;
    }

    return lampIcons[vertical];
}

</script>

<template>

    <div class="button-wrapper">

        <div class="icon">

            <img :src="getDeviceIcon()" alt="">

        </div>

        <p class="device-name">{{ device.name }}</p>

    </div>

</template>

<style scoped>
.button-wrapper {

    min-width: 100px;

    padding: 10px;
    box-sizing: border-box;

    background-color: var(--surface);

    border-radius: 15px;

    display: flex;
    align-items: center;
    gap: 6px;

    .icon {

        height: 100%;
        aspect-ratio: 1;
        background-color: var(--accent);
        border-radius: 10000px;

        img {

            --width: 60%;

            margin: calc((100% - var(--width)) / 2);
            width: var(--width);

        }
    }

    .device-name {

        margin: 10px 0px;
        display: inline;
    }
}
</style>