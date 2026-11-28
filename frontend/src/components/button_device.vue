<script setup lang="ts">

import placeholderIcon from "@/assets/icons/lights-all.svg";
import ceilingIcon from "@/assets/icons/lamp-ceiling.svg";
import deskIcon from "@/assets/icons/lamp-floor.svg";
import floorIcon from "@/assets/icons/lamp-desk.svg";
import lampDefault from "@/assets/icons/lamp-bulb.svg";

import { ref } from "vue";
import { canToggle, hasCapability, type Device } from "@/types/Device";
import type { Vertical } from "@/types/DbDevice";

const lampIcons: Record<Vertical, string> = {

    high: ceilingIcon,
    medium: deskIcon,
    low: floorIcon
}

const props = defineProps<{
    device: Device
}>();

// Asks for the change, the parent does it and updates device.isOn / device.brightness
const emit = defineEmits<{

    power: [isOn: boolean]
    brightness: [value: number]
}>();

const canDim = () => hasCapability(props.device, "brightness");

// Dragging sideways across the card changes the brightness, the full card width = 0-100.
// Smaller moves than this are still a tap (select / switch on-off).
const dragThreshold = 8;

const card = ref<HTMLElement | null>(null);

let pointerId: number | null = null;
let startX = 0;
let startY = 0;
let startBrightness = 0;
let isDragging = false;
let justDragged = false;

function onPointerDown(event: PointerEvent) {

    if (!canDim() || !props.device.isOn)
        return;

    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    startBrightness = props.device.brightness ?? 50;
    isDragging = false;
}

function onPointerMove(event: PointerEvent) {

    if (event.pointerId !== pointerId || !card.value)
        return;

    const dx = event.clientX - startX;
    const dy = event.clientY - startY;

    if (!isDragging) {

        // Mostly up/down = the page is being scrolled, leave it alone
        if (Math.abs(dy) > dragThreshold && Math.abs(dy) > Math.abs(dx)) {

            pointerId = null;
            return;
        }

        if (Math.abs(dx) < dragThreshold)
            return;

        isDragging = true;
        card.value.setPointerCapture(event.pointerId);
    }

    const brightness = Math.round(startBrightness + dx / card.value.offsetWidth * 100);
    const clamped = Math.min(100, Math.max(1, brightness));

    if (clamped != props.device.brightness)
        emit("brightness", clamped);
}

function onPointerEnd(event: PointerEvent) {

    if (event.pointerId !== pointerId)
        return;

    pointerId = null;

    if (isDragging) {

        isDragging = false;

        // The click that follows the drag shouldn't select the device or switch it
        justDragged = true;
        setTimeout(() => justDragged = false);
    }
}

// Capture runs before the card's and the icon's own click handlers, so they can be skipped
function onClickCapture(event: MouseEvent) {

    if (justDragged) {

        event.stopImmediatePropagation();
        event.preventDefault();
    }
}

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

    <div ref="card" class="button-wrapper" @click.capture="onClickCapture" @pointerdown="onPointerDown"
        @pointermove="onPointerMove" @pointerup="onPointerEnd" @pointercancel="onPointerEnd">

        <!-- .stop so switching it doesn't also select/deselect the device -->
        <button class="icon" :class="{ on: device.isOn }" :disabled="!canToggle(device)"
            @click.stop="emit('power', !device.isOn)">

            <img :src="getDeviceIcon()" alt="" draggable="false">

        </button>

        <p class="device-name">{{ device.name.replaceAll("_", " ") }}</p>

        <div v-if="canDim()" class="brightness-line" :class="{ on: device.isOn }"
            :style="{ width: `${device.brightness ?? 0}%` }"></div>

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

    position: relative;
    overflow: hidden;

    /* Sideways drags change brightness, up/down still scrolls the page */
    touch-action: pan-y;
    user-select: none;

    .brightness-line {

        position: absolute;
        left: 0;
        bottom: 0;
        height: 3px;

        background-color: var(--surface-light);
        transition: width .1s;

        &.on {

            background-color: var(--accent);
        }
    }

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