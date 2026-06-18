<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NSpace, NPopconfirm, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { deleteManufacturer, fetchManufacturers } from '@/api/manufacturers'
import type { Manufacturer } from '@/types/manufacturer'

const router = useRouter()
const message = useMessage()

const countryFilter = ref('')
const allCountries = ref<string[]>([])

const {
  state: manufacturers,
  isLoading,
  execute: reload,
} = useAsyncState(
  () => fetchManufacturers(countryFilter.value),
  [],
  { immediate: false, resetOnExecute: false },
)

const countryOptions = computed(() => {
  return [
    { label: '全部', value: '' },
    ...allCountries.value
      .sort()
      .map((c) => ({ label: c, value: c })),
  ]
})

async function loadCountries() {
  const all = await fetchManufacturers()
  const set = new Set<string>()
  for (const m of all) {
    set.add(m.country)
  }
  allCountries.value = Array.from(set)
}

function onFilterChange(value: string) {
  countryFilter.value = value
  reload()
}

async function handleDelete(id: number) {
  try {
    await deleteManufacturer(id)
    message.success('已删除')
    await loadCountries()
    await reload()
  } catch {
    message.error('删除失败')
  }
}

const columns = computed<DataTableColumns<Manufacturer>>(() => [
  { title: 'ID', key: 'id', width: 60 },
  { title: '品牌名称', key: 'brand_name', ellipsis: { tooltip: true } },
  {
    title: '所属国家',
    key: 'country',
    width: 120,
    render(row) {
      return h(NTag, { size: 'small', type: 'info' }, { default: () => row.country })
    },
  },
  { title: '成立年份', key: 'founded_year', width: 100 },
  { title: '简介', key: 'description', ellipsis: { tooltip: true } },
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
            onClick: () => router.push(`/manufacturers/${row.id}/edit`),
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
            default: () => '确定删除该厂商？',
          },
        ),
      ])
    },
  },
])

onMounted(async () => {
  await loadCountries()
  reload()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>厂商品牌</h1>
        <p class="subtitle">收录经典售货机厂商 · 品牌名称 · 所属国家与简介</p>
      </div>
      <NSpace>
        <NButton @click="router.push('/')">机型图鉴</NButton>
        <NButton type="primary" @click="router.push('/manufacturers/new')">
          新增厂商
        </NButton>
      </NSpace>
    </header>

    <NCard class="list-card" title="厂商列表">
      <div class="toolbar">
        <span class="toolbar-label">按国家筛选</span>
        <NRadioGroup
          :value="countryFilter"
          @update:value="onFilterChange"
        >
          <NRadioButton
            v-for="opt in countryOptions"
            :key="opt.value"
            :value="opt.value"
            :label="opt.label"
          />
        </NRadioGroup>
      </div>

      <NDataTable
        :columns="columns"
        :data="manufacturers"
        :loading="isLoading"
        :bordered="false"
        striped
        :row-key="(row: Manufacturer) => row.id"
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
