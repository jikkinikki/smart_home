<script lang="ts" setup>

import ManageRoom from './ManageRoom.vue';
import RoomBtn from '@/components/RoomBtn.vue';
import { useRooms } from '@/composables/useRooms';
import { useDevices } from '@/composables/useDevices';
import { canToggle } from '@/types/Device';
import { onMounted } from 'vue';

const { rooms, loadRooms } = useRooms();
const { devices, loadDevices, setPower } = useDevices();

onMounted(() => {

    loadRooms();
    loadDevices();
});

// The room's devices that can be switched on/off. roomId = undefined is every room.
function getRoomLamps(roomId?: number) {

    return devices.value.filter(device => canToggle(device) && (roomId === undefined || device.room_id == roomId));
}

function setRoomPower(isOn: boolean, roomId?: number) {

    setPower(getRoomLamps(roomId), isOn);
}

// How many of the room's lamps are on, 0-100.
// A room with no lamps is 0, a lamp that didn't answer counts as off.
function getLampsOnPercent(roomId?: number) {

    const lamps = getRoomLamps(roomId);

    if (lamps.length == 0)
        return 0;

    return Math.round(lamps.filter(device => device.isOn === true).length / lamps.length * 100);
}

</script>

<template>

    <div class="dynamic-wrapper">

        <h1>Home</h1>

        <div class="rooms">

            <div class="room-all">

                <RoomBtn roomName="All Rooms" roomId="all" :lampsOnPercent="getLampsOnPercent()"
                    @power="(isOn) => setRoomPower(isOn)"></RoomBtn>
            </div>

            <div class="individual-rooms">

                <RoomBtn v-for="room in rooms" :key="room.id" :roomName="room.name" :roomId="String(room.id)"
                    :lampsOnPercent="getLampsOnPercent(room.id)" @power="(isOn) => setRoomPower(isOn, room.id)">
                </RoomBtn>

                <RoomBtn v-for="room in rooms" :key="room.id" :roomName="room.name" :roomId="String(room.id)"
                    :lampsOnPercent="getLampsOnPercent(room.id)" @power="(isOn) => setRoomPower(isOn, room.id)">
                </RoomBtn>
                <RoomBtn v-for="room in rooms" :key="room.id" :roomName="room.name" :roomId="String(room.id)"
                    :lampsOnPercent="getLampsOnPercent(room.id)" @power="(isOn) => setRoomPower(isOn, room.id)">
                </RoomBtn>


            </div>

        </div>

    </div>

    <!-- <ManageRoom></ManageRoom> -->


</template>

<style lang="scss">
.rooms {

    .room-all {

        margin: 10px 0px;
        margin-bottom: 25px;
    }

    .individual-rooms {

        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;

        margin-bottom: 50px;

    }
}
</style>