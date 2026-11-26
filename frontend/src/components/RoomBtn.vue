<script lang="ts" setup>

import icon from '@/assets/icons/room-home.svg'
import onoff from '@/assets/icons/control-power.svg'
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const isOn = ref(false);

const props = withDefaults(defineProps<{

    roomName?: string,
    roomId: string

}>(), {

    roomName: "room name"

});

function onclick(){

    router.push({ name: "roomId", params: { id: props.roomId } });
}


</script>


<template>

    <div @click="onclick" class="card">

        <div class="icon"><img :src="icon" alt=""></div>
        <div class="info">
            <p>{{ roomName }}</p>
        </div>
        <div @click.stop="isOn = !isOn" class="toggle-on" :class="{ isOn: isOn, isOff: !isOn }"><img :src="onoff" alt=""></div>


    </div>

    <!-- <ManageRoom></ManageRoom> -->


</template>


<style lang="scss">

.card {

    box-shadow: 0px 0px 5px 5px rgba(0, 0, 0, 0.493);
    padding: 10px;
    border-radius: 15px;

    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 10px;
    align-items: center;

    .icon {

        background-color: orange;

        width: 40px;
        aspect-ratio: 1;

        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: center;

        img {

            filter: brightness(0);
        }
    }

    .toggle-on {

        background-color: rgb(236, 232, 225);

        width: 40px;
        aspect-ratio: 1;

        border-radius: 1000px;

        display: flex;
        align-items: center;
        justify-content: center;

        img {

            filter: brightness(0);
        }
    }

    .isOn {

        background-color: rgb(236, 232, 225);

        img {

            filter: brightness(0);
        }
    }

    .isOff {

        background-color: rgb(63, 63, 63);

        img {

            filter: brightness(0) invert(0.9);
        }
    }
}
</style>