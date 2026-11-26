import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    {
      path: '/',
      component: () => import('@/views/Rooms.vue'),
    },
    {
      path: '/room/:id',
      name: "roomId",
      component: () => import('@/views/ManageRoom.vue'),
    },
    {
      path: '/manageDevices',
      component: () => import('@/views/ManageDevices.vue'),
    },
    {
      path: '/manageRooms',
      component: () => import('@/views/ManageRooms.vue'),
    }
  ],
})

export default router
