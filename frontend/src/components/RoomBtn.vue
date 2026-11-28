<script lang="ts" setup>

import icon from '@/assets/icons/room-home.svg'
import onoff from '@/assets/icons/control-power.svg'
import { useRouter } from 'vue-router';
import OnOffFillBtn from './OnOffFillBtn.vue';

const router = useRouter();

const props = withDefaults(defineProps<{

    roomName?: string,
    roomId: string,
    lampsOnPercent?: number

}>(), {

    roomName: "room name",
    lampsOnPercent: 0

});

// Asks to turn all the room's lamps on or off, the parent does it and updates lampsOnPercent
const emit = defineEmits<{

    power: [isOn: boolean]
}>();

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
        <OnOffFillBtn class="room-toggle" @click.stop :isOn="lampsOnPercent == 100" :fillPercent="lampsOnPercent"
            @isOn="(isOn) => emit('power', isOn)"></OnOffFillBtn>

    </div>

    <!-- <ManageRoom></ManageRoom> -->


</template>


<style lang="scss">

.card {

    box-shadow: 0px 0px 5px 5px var(--shadow);
    padding: 10px;
    border-radius: 10px;

    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 10px;
    align-items: center;

    .icon {

        background-color: var(--accent);

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

    // Same size as the old toggle, the OnOffFillBtn is bigger by default
    .room-toggle {

        width: 40px;
        height: 40px;
        padding: 8px;
    }

    .toggle-on {

        background-color: var(--white);

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

        background-color: var(--white);

        img {

            filter: brightness(0);
        }
    }

    .isOff {

        background-color: var(--surface-light);

        img {

            filter: brightness(0) invert(0.9);
        }
    }
}
</style>