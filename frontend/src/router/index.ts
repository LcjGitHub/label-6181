import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/MachineListView.vue'),
    },
    {
      path: '/machines/:id/edit',
      name: 'machine-edit',
      component: () => import('@/views/MachineFormView.vue'),
    },
    {
      path: '/machines/new',
      name: 'machine-new',
      component: () => import('@/views/MachineFormView.vue'),
    },
  ],
})

export default router
