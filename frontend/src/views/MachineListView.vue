<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NTag, NSpace, NPopconfirm } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { deleteMachine, fetchMachines } from '@/api/machines'
import { fetchTags } from '@/api/tags'
import type { Machine, OperationalFilter } from '@/types/machine'
import type { Tag } from '@/types/tag'

const router = useRouter()
const message = useMessage()

const operationalFilter = ref<OperationalFilter>('all')
const tagFilter = ref<number | null>(null)
const allTags = ref<Tag[]>([])

const filterOptions = [
  { label: '全部', value: 'all' as const },
  { label: '运作中', value: 'true' as const },
  { label: '已停运', value: 'false' as const },
]

const tagFilterOptions = computed(() => [
  { label: '全部标签', value: null },
  ...allTags.value.map((t) => ({ label: t.name, value: t.id })),
])

const {
  state: machines,
  isLoading,
  execute: reload,
} = useAsyncState(
  async () => {
    try {
      return await fetchMachines(operationalFilter.value, tagFilter.value)
    } catch {
      message.error('加载售货机列表失败')
      return []
    }
  },
  [],
  { immediate: false, resetOnExecute: false },
)

async function loadTags() {
  try {
    allTags.value = await fetchTags()
  } catch {
    message.error('加载标签列表失败，标签筛选将不可用')
  }
}

/** 筛选变化时重新加载 */
function onFilterChange() {
  reload()
}

/** 删除售货机 */
async function handleDelete(id: number) {
  try {
    await deleteMachine(id)
    message.success('已删除')
    await reload()
  } catch {
    message.error('删除失败')
  }
}

const columns = computed<DataTableColumns<Machine>>(() => [
  { title: 'ID', key: 'id', width: 60 },
  { title: '机型', key: 'model_type', ellipsis: { tooltip: true } },
  { title: '地点', key: 'location', ellipsis: { tooltip: true } },
  { title: '售卖品类', key: 'categories', ellipsis: { tooltip: true } },
  {
    title: '是否运作',
    key: 'is_operational',
    width: 100,
    render(row) {
      return h(
        NTag,
        { type: row.is_operational ? 'success' : 'default', size: 'small' },
        { default: () => (row.is_operational ? '运作中' : '已停运') },
      )
    },
  },
  {
    title: '标签',
    key: 'tags',
    width: 220,
    render(row) {
      if (!row.tags || row.tags.length === 0) {
        return h('span', { style: { color: '#999' } }, '无')
      }
      return h(
        NSpace,
        { size: 4, wrapItem: true, wrap: true },
        () =>
          row.tags.map((tag) =>
            h(
              NTag,
              {
                size: 'small',
                key: tag.id,
                style: {
                  backgroundColor: tag.color,
                  borderColor: tag.color,
                  color: '#fff',
                },
              },
              { default: () => tag.name },
            ),
          ),
      )
    },
  },
  {
    title: '照片描述',
    key: 'photo_description',
    ellipsis: { tooltip: true },
  },
  {
    title: '操作',
    key: 'actions',
    width: 300,
    render(row) {
      return h(NSpace, { size: 'small' }, () => [
        h(
          NButton,
          {
            size: 'small',
            tertiary: true,
            type: 'warning',
            onClick: () => router.push({
              path: '/inspections/new',
              query: { machine_id: String(row.id) },
            }),
          },
          { default: () => '巡检' },
        ),
        h(
          NButton,
          {
            size: 'small',
            tertiary: true,
            type: 'info',
            onClick: () => router.push(`/machines/${row.id}/maintenances`),
          },
          { default: () => '维保' },
        ),
        h(
          NButton,
          {
            size: 'small',
            tertiary: true,
            type: 'primary',
            onClick: () => router.push(`/machines/${row.id}/edit`),
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
            default: () => '确定删除这台售货机？',
          },
        ),
      ])
    },
  },
])

onMounted(() => {
  Promise.all([loadTags(), reload()])
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>老式自动售货机机型图鉴</h1>
        <p class="subtitle">收录经典机型 · 地点 · 售卖品类与运作状态</p>
      </div>
      <NSpace>
        <NButton type="success" @click="router.push('/statistics')">
          数据统计
        </NButton>
        <NButton @click="router.push('/maintenances')">维保记录</NButton>
        <NButton @click="router.push('/inspections')">巡检打卡</NButton>
        <NButton @click="router.push('/manufacturers')">厂商品牌</NButton>
        <NButton @click="router.push('/tags')">标签管理</NButton>
        <NButton type="primary" @click="router.push('/machines/new')">
          新增机型
        </NButton>
      </NSpace>
    </header>

    <NCard class="list-card" title="机器列表">
      <div class="toolbar">
        <span class="toolbar-label">运作状态筛选</span>
        <NRadioGroup
          :value="operationalFilter"
          @update:value="(v: OperationalFilter) => { operationalFilter = v; onFilterChange() }"
        >
          <NRadioButton
            v-for="opt in filterOptions"
            :key="opt.value"
            :value="opt.value"
            :label="opt.label"
          />
        </NRadioGroup>
        <span class="toolbar-sep" />
        <span class="toolbar-label">按标签筛选</span>
        <NSelect
          :options="tagFilterOptions"
          :value="tagFilter"
          @update:value="(v: number | null) => { tagFilter = v; onFilterChange() }"
          style="width: 180px"
          placeholder="选择标签"
        />
      </div>

      <NDataTable
        :columns="columns"
        :data="machines"
        :loading="isLoading"
        :bordered="false"
        striped
        :row-key="(row: Machine) => row.id"
      />
    </NCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1300px;
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

.toolbar-sep {
  width: 1px;
  height: 20px;
  background: #e0d5c2;
  margin: 0 4px;
}
</style>
