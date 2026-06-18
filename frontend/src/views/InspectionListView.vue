<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTag, NSpace } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { fetchInspections } from '@/api/inspections'
import type { Inspection, InspectionResultFilter } from '@/types/inspection'
import type { Machine } from '@/types/machine'
import { fetchMachines } from '@/api/machines'

const router = useRouter()

const resultFilter = ref<InspectionResultFilter>('all')

const filterOptions = [
  { label: '全部', value: 'all' as const },
  { label: '正常', value: '正常' as const },
  { label: '异常', value: '异常' as const },
]

const { state: machines, isLoading: machinesLoading } = useAsyncState(
  () => fetchMachines('all'),
  [] as Machine[],
  { immediate: true },
)

const machineMap = computed(() => {
  const map: Record<number, Machine> = {}
  machines.value.forEach((m) => {
    map[m.id] = m
  })
  return map
})

const {
  state: inspections,
  isLoading,
  execute: reload,
} = useAsyncState(
  () => fetchInspections(resultFilter.value),
  [],
  { immediate: false, resetOnExecute: false },
)

function onFilterChange(value: InspectionResultFilter) {
  resultFilter.value = value
  reload()
}

function goCreate() {
  router.push('/inspections/new')
}

const columns = computed<DataTableColumns<Inspection>>(() => [
  { title: 'ID', key: 'id', width: 60 },
  {
    title: '售货机编号',
    key: 'machine_id',
    width: 140,
    render(row) {
      const m = machineMap.value[row.machine_id]
      if (m) {
        return `#${m.id} · ${m.model_type}`
      }
      return `#${row.machine_id}`
    },
  },
  {
    title: '售货机地点',
    key: 'location',
    width: 180,
    render(row) {
      const m = machineMap.value[row.machine_id]
      return m?.location ?? '—'
    },
  },
  { title: '巡检时间', key: 'inspection_time', width: 160 },
  {
    title: '巡检结果',
    key: 'result',
    width: 100,
    render(row) {
      return h(
        NTag,
        { type: row.result === '正常' ? 'success' : 'error', size: 'small' },
        { default: () => row.result },
      )
    },
  },
  {
    title: '异常说明',
    key: 'remark',
    ellipsis: { tooltip: true },
    render(row) {
      return row.remark || h('span', { style: { color: '#aaa' } }, '—')
    },
  },
])

onMounted(() => {
  reload()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>巡检打卡管理</h1>
        <p class="subtitle">查看所有巡检记录，支持按巡检结果筛选</p>
      </div>
      <NSpace>
        <NButton @click="router.push('/')">售货机列表</NButton>
        <NButton type="primary" @click="goCreate">
          新增巡检打卡
        </NButton>
      </NSpace>
    </header>

    <NCard class="list-card" title="巡检历史记录">
      <div class="toolbar">
        <span class="toolbar-label">巡检结果筛选</span>
        <NRadioGroup
          :value="resultFilter"
          @update:value="onFilterChange"
        >
          <NRadioButton
            v-for="opt in filterOptions"
            :key="opt.value"
            :value="opt.value"
            :label="opt.label"
          />
        </NRadioGroup>
      </div>

      <NDataTable
        :columns="columns"
        :data="inspections"
        :loading="isLoading || machinesLoading"
        :bordered="false"
        striped
        :row-key="(row: Inspection) => row.id"
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
