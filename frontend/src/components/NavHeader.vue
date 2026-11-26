<script setup lang="ts">
import { RouterLink } from 'vue-router'
import homeIcon from '@/assets/icons/room-home.svg'
</script>

<template>

    <header class="nav-header">

        <RouterLink to="/" class="home-btn" aria-label="Home">
            <img :src="homeIcon" alt="">

        </RouterLink>

        <nav class="nav-links">
            <RouterLink to="/manageDevices">Manage devices</RouterLink>
            <RouterLink to="/manageRooms">Manage rooms</RouterLink>
        </nav>

    </header>

</template>

<style lang="scss" scoped>

.nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background-color: var(--button-col);
}

a {
    color: rgb(217, 217, 217);
    text-decoration: none;
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

.nav-links {
    display: flex;
    gap: 16px;

    a.router-link-exact-active {
        color: rgb(255, 255, 255);
        font-weight: 600;
    }
}

</style>
