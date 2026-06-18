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
    {
      path: '/manufacturers',
      name: 'manufacturer-list',
      component: () => import('@/views/ManufacturerListView.vue'),
    },
    {
      path: '/manufacturers/new',
      name: 'manufacturer-new',
      component: () => import('@/views/ManufacturerFormView.vue'),
    },
    {
      path: '/manufacturers/:id/edit',
      name: 'manufacturer-edit',
      component: () => import('@/views/ManufacturerFormView.vue'),
    },
  ],
})

export default router
