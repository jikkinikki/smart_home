<script setup lang="ts">
import { RouterLink } from 'vue-router'
import homeIcon from '@/assets/icons/room-home.svg'
import HamburgerMenu, { type MenuLink } from './HamburgerMenu.vue'

const menuLinks: MenuLink[] = [
    { to: "/manageDevices", label: "Manage devices" },
    { to: "/manageRooms", label: "Manage rooms" }
];
</script>

<template>

    <header class="nav-header">

        <RouterLink to="/" class="home-btn" aria-label="Home">
            <img :src="homeIcon" alt="">

        </RouterLink>

        <HamburgerMenu :links="menuLinks"></HamburgerMenu>

    </header>

</template>

<style lang="scss" scoped>

.nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background-color: var(--surface);
}

.home-btn {
    display: flex;
    align-items: center;

    img {
        width: 24px;
        height: 24px;
        // SVG strokes render black inside <img>; invert to light grey on the dark header
        filter: invert(85%);
    }
}

</style>
