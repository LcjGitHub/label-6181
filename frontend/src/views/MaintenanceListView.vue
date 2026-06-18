<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, NButton, NTag, NSpace, NPopconfirm } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { deleteMaintenance, fetchMaintenances } from '@/api/maintenances'
import { fetchMachine } from '@/api/machines'
import type { Maintenance } from '@/types/maintenance'
import type { Machine } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const machine = ref<Machine | null>(null)

const machineId = computed(() => {
  const raw = route.params.machineId
  if (typeof raw === 'string') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : undefined
  }
  return undefined
})

const hasMachineScope = computed(() => machineId.value !== undefined)

const {
  state: maintenances,
  isLoading,
  execute: reload,
} = useAsyncState(
  () => fetchMaintenances(machineId.value),
  [],
  { immediate: false, resetOnExecute: false },
)

async function loadMachineInfo() {
  if (machineId.value === undefined) return
  try {
    machine.value = await fetchMachine(machineId.value)
  } catch {
    message.error('加载售货机信息失败')
  }
}

async function handleDelete(id: number) {
  try {
    await deleteMaintenance(id)
    message.success('已删除')
    await reload()
  } catch {
    message.error('删除失败')
  }
}

function goCreate() {
  if (machineId.value !== undefined) {
    router.push({
      path: '/maintenances/new',
      query: { machine_id: String(machineId.value) },
    })
  } else {
    router.push('/maintenances/new')
  }
}

function goBack() {
  router.push('/')
}

const columns = computed<DataTableColumns<Maintenance>>(() => {
  const cols: DataTableColumns<Maintenance> = [
    { title: 'ID', key: 'id', width: 60 },
  ]
  if (!hasMachineScope.value) {
    cols.push({
      title: '售货机编号',
      key: 'machine_id',
      width: 110,
      render(row) {
        return h(
          NButton,
          {
            size: 'small',
            text: true,
            type: 'primary',
            onClick: () => router.push(`/machines/${row.machine_id}/maintenances`),
          },
          { default: () => `#${row.machine_id}` },
        )
      },
    })
  }
  cols.push(
    { title: '维保日期', key: 'maintenance_date', width: 120 },
    {
      title: '维保类型',
      key: 'maintenance_type',
      width: 140,
      render(row) {
        return h(
          NTag,
          { type: 'info', size: 'small' },
          { default: () => row.maintenance_type },
        )
      },
    },
    { title: '经办人', key: 'handler', width: 120 },
    {
      title: '维保说明',
      key: 'description',
      ellipsis: { tooltip: true },
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      render(row) {
        return h(NSpace, { size: 'small' }, () => [
          h(
            NButton,
            {
              size: 'small',
              tertiary: true,
              type: 'primary',
              onClick: () => router.push(`/maintenances/${row.id}/edit`),
            },
            { default: () => '编辑' },
          ),
          h(
            NPopconfirm,
            { onPositiveClick: () => handleDelete(row.id) },
            {
              trigger: () =>
                h(
                  NButton,
                  { size: 'small', tertiary: true, type: 'error' },
                  { default: () => '删除' },
                ),
              default: () => '确定删除该维保记录？',
            },
          ),
        ])
      },
    },
  )
  return cols
})

onMounted(async () => {
  await loadMachineInfo()
  reload()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>
          {{ hasMachineScope ? `${machine?.model_type ?? `售货机 #${machineId}`} 的维保记录` : '维保记录管理' }}
        </h1>
        <p class="subtitle" v-if="hasMachineScope">
          {{ machine?.location ?? '—' }} · 记录日常巡检、维修与保养
        </p>
        <p class="subtitle" v-else>
          查看所有售货机的维保记录，支持按售货机编号筛选
        </p>
      </div>
      <NSpace>
        <NButton v-if="hasMachineScope" quaternary @click="goBack">
          返回售货机列表
        </NButton>
        <NButton type="primary" @click="goCreate">
          新增维保记录
        </NButton>
      </NSpace>
    </header>

    <NCard class="list-card" :title="hasMachineScope ? `售货机 #${machineId} 维保历史` : '维保记录列表'">
      <NDataTable
        :columns="columns"
        :data="maintenances"
        :loading="isLoading"
        :bordered="false"
        striped
        :row-key="(row: Maintenance) => row.id"
      />
    </NCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 1.75rem;
  color: #3d2f1f;
}

.subtitle {
  margin: 0;
  color: #7a6a55;
  font-size: 0.95rem;
}

.list-card {
  background: #fffdf8;
  border: 1px solid #e8dcc8;
}
</style>
