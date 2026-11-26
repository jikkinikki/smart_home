<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useDbDevices } from '@/composables/useDbDevices';
import { useRooms } from '@/composables/useRooms';
import type { DbDevice } from '@/types/DbDevice';

const { devices, error: devicesError, loadDevices, updateDevice } = useDbDevices();
const { rooms, error: roomsError, loadRooms, addRoom, getRoomById } = useRooms();

const newRoomName = ref("");

// Clicking a device moves it to this room
const selectedRoomId = ref<number | null>(null);
const selectedRoom = computed(() => selectedRoomId.value == null ? undefined : getRoomById(selectedRoomId.value));

// The devices split into: in the selected room, in no room, in another room. Empty ones are left out.
const deviceSections = computed(() => {

    const hasRoom = (device: DbDevice) => device.room_id != null && getRoomById(device.room_id) != undefined;
    const inSelected = (device: DbDevice) => selectedRoomId.value != null && device.room_id == selectedRoomId.value;

    return [
        {
            key: "selected",
            title: selectedRoom.value ? `In ${selectedRoom.value.name}` : "",
            devices: devices.value.filter(inSelected)
        },
        {
            key: "none",
            title: "No room",
            devices: devices.value.filter(device => !hasRoom(device))
        },
        {
            key: "other",
            title: selectedRoom.value ? "In other rooms" : "In a room",
            devices: devices.value.filter(device => hasRoom(device) && !inSelected(device))
        }
    ].filter(section => section.devices.length > 0);
});

function deviceCount(roomId: number) {

    return devices.value.filter(device => device.room_id == roomId).length;
}

function roomName(device: DbDevice) {

    const room = device.room_id == null ? undefined : getRoomById(device.room_id);
    return room ? room.name : "No room";
}

async function add() {

    const name = newRoomName.value.trim();
    if (!name) return;

    const room = await addRoom(name);

    if (room) {
        newRoomName.value = "";
        selectedRoomId.value = room.id;  // so you can start adding devices right away
    }
}

function selectRoom(roomId: number) {

    selectedRoomId.value = selectedRoomId.value == roomId ? null : roomId;
}

// Moves the device to the selected room. Clicking a device that's already in it takes it out again.
function clickDevice(device: DbDevice) {

    if (selectedRoomId.value == null) return;

    const roomId = device.room_id == selectedRoomId.value ? null : selectedRoomId.value;
    updateDevice(device.id, { room_id: roomId });
}

onMounted(() => {

    loadRooms();
    loadDevices();
});

</script>

<template>

    <div class="wrapper">

        <div class="container">

            <h2>Rooms</h2>

            <p v-if="roomsError" class="error">Rooms: {{ roomsError }}</p>

            <form class="add-room" @submit.prevent="add">
                <input v-model="newRoomName" placeholder="New room name">
                <button type="submit" :disabled="!newRoomName.trim()">Add room</button>
            </form>

            <p v-if="rooms.length == 0" class="hint">No rooms yet. Add one above.</p>

            <div class="rooms">

                <button v-for="room in rooms" :key="room.id" class="room"
                    :class="{ selected: room.id == selectedRoomId }" @click="selectRoom(room.id)">
                    {{ room.name }}
                    <span class="count">{{ deviceCount(room.id) }}</span>
                </button>

            </div>

        </div>

        <div class="container">

            <h2>Devices</h2>

            <p v-if="devicesError" class="error">Devices: {{ devicesError }}</p>

            <p class="hint">
                <template v-if="selectedRoom">
                    Click devices to move them to <b>{{ selectedRoom.name }}</b>. Click again to take them out.
                </template>
                <template v-else>Select a room above, then click devices to move them to it.</template>
            </p>

            <div v-for="section in deviceSections" :key="section.key" class="device-section">

                <h3>{{ section.title }} <span class="count">{{ section.devices.length }}</span></h3>

                <div class="devices" :class="{ 'no-selection': !selectedRoom }">

                    <div v-for="device in section.devices" :key="device.id" class="device"
                        :class="{ 'in-selected': section.key == 'selected' }"
                        @click="clickDevice(device)">

                        <p class="device-name">{{ device.name || "(no name)" }}</p>
                        <p class="device-room">{{ roomName(device) }}</p>

                    </div>

                </div>

            </div>

        </div>

    </div>

</template>

<style lang="scss" scoped>

// Same max width layout as ManageDevices
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

p {
    margin: 0;
}

.hint {
    opacity: 0.6;
    margin-bottom: 8px;
}

.error {
    color: rgb(240, 110, 110);
}

.add-room {

    display: flex;
    gap: 4px;
    margin-bottom: 10px;

    input {
        flex: 1;
    }

    button {
        padding: 6px 12px;
    }

    button:disabled {
        opacity: 0.6;
    }
}

.rooms {

    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.room {

    padding: 10px 14px;
    border: 2px solid var(--button-col);
    border-radius: 10px;
    cursor: pointer;
    font-size: 1em;

    .count {
        margin-left: 6px;
        opacity: 0.6;
    }

    &.selected {
        background-color: orange;
        border-color: orange;
        color: rgb(15, 15, 15);
        font-weight: 600;

        .count {
            opacity: 0.8;
        }
    }
}

.device-section {

    margin-bottom: 12px;

    h3 {
        margin: 0 0 6px 0;
    }

    .count {
        opacity: 0.6;
        font-weight: normal;
    }
}

.devices {

    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 5px;

    // Nothing happens when clicking devices before a room is selected
    &.no-selection .device {
        cursor: default;
        opacity: 0.6;
    }
}

.device {

    border: 2px solid var(--button-col);
    border-radius: 10px;
    padding: 8px;
    cursor: pointer;
    overflow: hidden;
    user-select: none;

    .device-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .device-room {
        font-size: 0.8em;
        opacity: 0.6;
    }

    // The device is in the selected room
    &.in-selected {
        border-color: orange;
        background-color: rgba(255, 165, 0, 0.15);

        .device-room {
            color: orange;
            opacity: 1;
        }
    }
}

</style>
