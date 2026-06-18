<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, NButton, NTag, NSpace, NPopconfirm, NSelect } from 'naive-ui'
import type { DataTableColumns, SelectOption } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { deleteMaintenance, batchDeleteMaintenances, fetchMaintenances } from '@/api/maintenances'
import { fetchMachine, fetchAllMachines } from '@/api/machines'
import type { Maintenance } from '@/types/maintenance'
import type { Machine } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const machine = ref<Machine | null>(null)

const machineIdFromRoute = computed(() => {
  const raw = route.params.machineId
  if (typeof raw === 'string') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : undefined
  }
  return undefined
})

const hasMachineScope = computed(() => machineIdFromRoute.value !== undefined)

const filterMachineId = ref<number | null>(null)
const checkedRowKeys = ref<number[]>([])

const { state: allMachines, isLoading: machinesLoading } = useAsyncState(
  () => fetchAllMachines(),
  [] as Machine[],
  { immediate: true },
)

const machineFilterOptions = computed<SelectOption[]>(() => [
  { label: '全部售货机', value: null as unknown as number },
  ...allMachines.value.map((m) => ({
    label: `#${m.id} · ${m.model_type}`,
    value: m.id,
  })),
])

const effectiveMachineId = computed(() => {
  if (hasMachineScope.value) return machineIdFromRoute.value
  return filterMachineId.value ?? undefined
})

const {
  state: maintenances,
  isLoading,
  execute: reload,
} = useAsyncState(
  () => fetchMaintenances(effectiveMachineId.value),
  [],
  { immediate: false, resetOnExecute: false },
)

async function loadMachineInfo() {
  if (machineIdFromRoute.value === undefined) return
  try {
    machine.value = await fetchMachine(machineIdFromRoute.value)
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

async function handleBatchDelete() {
  try {
    await batchDeleteMaintenances(checkedRowKeys.value)
    message.success(`已删除 ${checkedRowKeys.value.length} 条记录`)
    checkedRowKeys.value = []
    await reload()
  } catch {
    message.error('批量删除失败')
  }
}

function goCreate() {
  const mid = effectiveMachineId.value
  if (mid !== undefined) {
    router.push({
      path: '/maintenances/new',
      query: { machine_id: String(mid) },
    })
  } else {
    router.push('/maintenances/new')
  }
}

function goBack() {
  router.push('/')
}

function onFilterChange(value: number | null) {
  filterMachineId.value = value
  reload()
}

const columns = computed<DataTableColumns<Maintenance>>(() => {
  const cols: DataTableColumns<Maintenance> = [
    { type: 'selection' },
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
          {{ hasMachineScope ? `${machine?.model_type ?? `售货机 #${machineIdFromRoute}`} 的维保记录` : '维保记录管理' }}
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

    <NCard class="list-card" :title="hasMachineScope ? `售货机 #${machineIdFromRoute} 维保历史` : '维保记录列表'">
      <div class="toolbar" v-if="!hasMachineScope || checkedRowKeys.length > 0">
        <NPopconfirm
          v-if="checkedRowKeys.length > 0"
          @positive-click="handleBatchDelete"
        >
          <template #trigger>
            <NButton type="error">
              批量删除 ({{ checkedRowKeys.length }})
            </NButton>
          </template>
          确定删除选中的 {{ checkedRowKeys.length }} 条维保记录？
        </NPopconfirm>
        <template v-if="!hasMachineScope">
          <span class="toolbar-label">按售货机筛选</span>
          <NSelect
            :value="filterMachineId"
            :options="machineFilterOptions"
            :loading="machinesLoading"
            placeholder="全部售货机"
            clearable
            style="width: 240px"
            @update:value="onFilterChange"
          />
        </template>
      </div>

      <NDataTable
        :columns="columns"
        :data="maintenances"
        :loading="isLoading"
        :bordered="false"
        striped
        :row-key="(row: Maintenance) => row.id"
        :checked-row-keys="checkedRowKeys"
        @update:checked-row-keys="(keys: number[]) => checkedRowKeys = keys"
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

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.toolbar-label {
  font-size: 0.9rem;
  color: #6b5c48;
}
</style>
