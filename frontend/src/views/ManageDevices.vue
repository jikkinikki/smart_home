<script setup lang="ts">
import { onMounted } from 'vue';
import { useDbDevices } from '@/composables/useDbDevices';
import DeviceEdit from '@/components/DeviceEdit.vue';
import DeviceRefetch from '@/components/DeviceRefetch.vue';

const { devices, error, loadDevices, updateDevice } = useDbDevices();

onMounted(loadDevices);

</script>

<template>

    <div class="wrapper">

        <div class="container">

            <h2 @click="loadDevices">Manage devices</h2>

            <p v-if="error">Could not load devices: {{ error }}</p>

            <div class="devices">

                <DeviceEdit v-for="device in devices" :key="device.id" :device="device" @save="updateDevice"></DeviceEdit>

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
