<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useDbDevices } from '@/composables/useDbDevices';
import { useRooms } from '@/composables/useRooms';
import DeviceEdit from '@/components/DeviceEdit.vue';
import DeviceRefetch from '@/components/DeviceRefetch.vue';
import OnOffBtn from '@/components/OnOffBtn.vue';
import { useDevices } from '@/composables/useDevices';
import { canToggle } from '@/types/Device';
import type { DbDevice } from '@/types/DbDevice';

const { devices, error, loadDevices, updateDevice, deleteDevice } = useDbDevices();
const { loadRooms, getRoomById } = useRooms();

// The same devices with their live state (on/off), for the on/off buttons
const { devices: liveDevices, isStateLoaded, loadDevices: loadLiveDevices, setPower } = useDevices();

// undefined = the device can't be switched (or isn't reachable), so it gets no button
function getSwitchableDevice(deviceId: string) {

    const device = liveDevices.value.find(device => device.id == deviceId);

    return device && canToggle(device) ? device : undefined;
}

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
    loadLiveDevices();
});

</script>

<template>

    <div class="dynamic-wrapper">

        <div>

            <h2 @click="loadDevices">Manage devices</h2>

            <p v-if="error">Could not load devices: {{ error }}</p>

            <div class="devices">

                <DeviceEdit v-for="device in sortedDevices" :key="device.id" :device="device" @save="updateDevice"
                    @delete="deleteDevice">

                    <template v-if="isStateLoaded && getSwitchableDevice(device.id)">
                        <OnOffBtn class="power-toggle" :isOn="getSwitchableDevice(device.id)!.isOn === true"
                            @isOn="(isOn) => setPower([getSwitchableDevice(device.id)!], isOn)"></OnOffBtn>
                    </template>

                </DeviceEdit>

            </div>

        </div>

        <div>

            <h2>Refetch devices</h2>

            <DeviceRefetch @applied="loadDevices"></DeviceRefetch>

        </div>

        <div class="add-device">


        </div>

    </div>


</template>

<style lang="scss" scoped>

h2 {
    text-transform: uppercase;
}

// Same height as the device name, the OnOffBtn is bigger by default
.power-toggle {

    flex-shrink: 0;
    width: 30px;
    height: 30px;
    padding: 7px;
    box-shadow: none;
}

.devices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 5px;
}

</style>
