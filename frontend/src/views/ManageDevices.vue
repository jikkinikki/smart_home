<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useDbDevices } from '@/composables/useDbDevices';
import { useRooms } from '@/composables/useRooms';
import DeviceEdit from '@/components/DeviceEdit.vue';
import DeviceRefetch from '@/components/DeviceRefetch.vue';
import type { DbDevice } from '@/types/DbDevice';

const { devices, error, loadDevices, updateDevice } = useDbDevices();
const { loadRooms, getRoomById } = useRooms();

function roomName(device: DbDevice) {

    return device.room_id == null ? undefined : getRoomById(device.room_id)?.name;
}

// Sorted by room name (devices without a room last), then by device name
const sortedDevices = computed(() => [...devices.value].sort((a, b) => {

    const roomA = roomName(a);
    const roomB = roomName(b);

    if (roomA != roomB) {
        if (roomA == undefined) return 1;
        if (roomB == undefined) return -1;
        return roomA.localeCompare(roomB);
    }

    return a.name.localeCompare(b.name);
}));

onMounted(() => {

    loadDevices();
    loadRooms();
});

</script>

<template>

    <div class="wrapper">

        <div class="container">

            <h2 @click="loadDevices">Manage devices</h2>

            <p v-if="error">Could not load devices: {{ error }}</p>

            <div class="devices">

                <DeviceEdit v-for="device in sortedDevices" :key="device.id" :device="device" @save="updateDevice"></DeviceEdit>

            </div>

        </div>

        <div class="container">

            <h2>Refetch devices</h2>

            <DeviceRefetch @applied="loadDevices"></DeviceRefetch>

        </div>

        <div class="add-device container">


        </div>

    </div>


</template>

<style lang="scss" scoped>

// Same max width layout as ManageRoomPhone
@media (min-width: 600px) {

    .wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .container {
        width: 600px;
        margin-left: -5%;
    }
}

h2 {
    text-transform: uppercase;
}

.devices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 5px;
}

</style>
