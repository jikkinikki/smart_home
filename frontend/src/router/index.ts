import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    {
      path: '/playground',
      component: () => import('@/views/ComponentPlayground.vue'),
    },
    {
      path: '/',
      component: () => import('@/views/ManageRoom.vue'),
    },
    {
      path: '/manageDevices',
      component: () => import('@/views/ManageDevices.vue'),
    }
  ],
})

export default router
