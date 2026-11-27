<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

export interface MenuLink {

    to: string,
    label: string
}

defineProps<{

    links: MenuLink[]
}>();

const isOpen = ref(false);
const root = ref<HTMLElement | null>(null);

// Close when clicking anywhere outside the menu
function onDocumentClick(event: MouseEvent) {

    if (root.value && !root.value.contains(event.target as Node)) {

        isOpen.value = false;
    }
}

onMounted(() => document.addEventListener("click", onDocumentClick));
onBeforeUnmount(() => document.removeEventListener("click", onDocumentClick));
</script>

<template>

    <div ref="root" class="hamburger-menu">

        <button class="menu-btn" :class="{ open: isOpen }" aria-label="Menu" :aria-expanded="isOpen"
            @click="isOpen = !isOpen">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <nav v-if="isOpen" class="menu-links">
            <RouterLink v-for="link in links" :key="link.to" :to="link.to" @click="isOpen = false">
                {{ link.label }}
            </RouterLink>
        </nav>

    </div>

</template>

<style lang="scss" scoped>

// Flex so the wrapper is exactly the button's size (no text line space under it),
// otherwise the header centers the taller wrapper and the button sits too high
.hamburger-menu {
    position: relative;
    display: flex;
    align-items: center;
}

.menu-btn {

    --line-gap: 8px;

    width: 32px;
    height: 32px;
    padding: 0;
    background-color: transparent;
    cursor: pointer;

    position: relative;

    // All lines sit on the center, top and bottom are pushed out from it
    span {
        position: absolute;
        left: 4px;
        right: 4px;
        top: calc(50% - 1px);
        height: 2px;
        border-radius: 2px;
        background-color: var(--icon);
        transition: transform .2s, opacity .2s;
    }

    span:nth-child(1) {
        transform: translateY(calc(var(--line-gap) * -1));
    }

    span:nth-child(3) {
        transform: translateY(var(--line-gap));
    }

    // The three lines turn into an X on the center while open
    &.open {

        span:nth-child(1) {
            transform: rotate(45deg);
        }

        span:nth-child(2) {
            opacity: 0;
        }

        span:nth-child(3) {
            transform: rotate(-45deg);
        }
    }
}

.menu-links {

    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    z-index: 10;

    min-width: 180px;
    padding: 4px;
    box-sizing: border-box;

    background-color: var(--surface);
    border: 1px solid var(--border-dark);
    border-radius: 10px;
    box-shadow: 0px 4px 12px var(--shadow);

    display: flex;
    flex-direction: column;
    gap: 2px;

    a {

        padding: 8px 10px;
        border-radius: 7px;
        color: var(--text-body);
        text-decoration: none;

        &:hover {
            background-color: var(--surface-light);
        }

        &.router-link-exact-active {
            color: var(--text-link-active);
            background-color: var(--surface-lighter);
            font-weight: 600;
        }
    }
}

</style>
