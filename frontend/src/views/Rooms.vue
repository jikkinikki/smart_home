<script lang="ts" setup>

import ManageRoom from './ManageRoom.vue';
import RoomBtn from '@/components/RoomBtn.vue';
import { useRooms } from '@/composables/useRooms';
import { onMounted } from 'vue';

const { rooms, loadRooms } = useRooms();

onMounted(() => {

    loadRooms();
});

</script>

<template>

    <div>

        <h1>Home</h1>

        <div class="rooms">

            <div class="room-all">

                <RoomBtn roomName="All Rooms" roomId="all"></RoomBtn>
            </div>

            <div class="individual-rooms">

                <RoomBtn v-for="room in rooms" :key="room.id" :roomName="room.name" :roomId="String(room.id)"></RoomBtn>

            </div>

        </div>

    </div>

    <!-- <ManageRoom></ManageRoom> -->


</template>

<style lang="scss">
.rooms {

    padding: 20px;

    .room-all {

        margin: 10px 0px;
    }

    .individual-rooms {

        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
    }
}
</style>