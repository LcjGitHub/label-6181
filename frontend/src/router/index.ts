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
      path: '/machines/:machineId/maintenances',
      name: 'machine-maintenance-list',
      component: () => import('@/views/MaintenanceListView.vue'),
    },
    {
      path: '/maintenances',
      name: 'maintenance-list',
      component: () => import('@/views/MaintenanceListView.vue'),
    },
    {
      path: '/maintenances/new',
      name: 'maintenance-new',
      component: () => import('@/views/MaintenanceFormView.vue'),
    },
    {
      path: '/maintenances/:id/edit',
      name: 'maintenance-edit',
      component: () => import('@/views/MaintenanceFormView.vue'),
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
    {
      path: '/inspections',
      name: 'inspection-list',
      component: () => import('@/views/InspectionListView.vue'),
    },
    {
      path: '/inspections/new',
      name: 'inspection-new',
      component: () => import('@/views/InspectionFormView.vue'),
    },
    {
      path: '/tags',
      name: 'tag-list',
      component: () => import('@/views/TagListView.vue'),
    },
    {
      path: '/tags/new',
      name: 'tag-new',
      component: () => import('@/views/TagFormView.vue'),
    },
    {
      path: '/tags/:id/edit',
      name: 'tag-edit',
      component: () => import('@/views/TagFormView.vue'),
    },
  ],
})

export default router
