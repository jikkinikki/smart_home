<script setup lang="ts">

import ManageRoomPhone from './ManageRoomPhone.vue';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// "all" = devices from all rooms, otherwise the room's id
const roomId = computed(() => {

    const id = route.params.id;
    return id == "all" ? undefined : Number(id);
});

</script>

<template>

    <!-- key: remake the view when going to another room, so its devices are loaded -->
    <ManageRoomPhone :key="String(route.params.id)" :roomId="roomId"></ManageRoomPhone>

</template>

<style lang="sass" scoped>

</style>
