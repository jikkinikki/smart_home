import { createRoom, getRooms } from '@/api/RoomApi';
import { ref } from 'vue';
import type { Room } from '@/types/Room';

export function useRooms() {

    const rooms = ref<Room[]>([]);
    const error = ref<string | null>(null);

    async function loadRooms() {

        try {
            rooms.value = await getRooms();
            error.value = null;
        }
        catch (e) {
            error.value = e instanceof Error ? e.message : String(e);
        }
    }

    function getRoomById(roomId: number) {

        return rooms.value.find(room => room.id == roomId);
    }

    // Returns the new room, or null if it couldn't be created (e.g. the name is taken)
    async function addRoom(name: string) {

        try {
            const room = await createRoom(name);
            rooms.value = [...rooms.value, room].sort((a, b) => a.name.localeCompare(b.name));
            error.value = null;
            return room;
        }
        catch (e) {
            error.value = e instanceof Error ? e.message : String(e);
            return null;
        }
    }

    return {
        rooms,
        error,
        loadRooms,
        getRoomById,
        addRoom
    };
}
