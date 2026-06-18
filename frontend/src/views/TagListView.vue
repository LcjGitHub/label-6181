<script setup lang="ts">
import { computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NSpace, NPopconfirm, NTag, NCard } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { deleteTag, fetchTags } from '@/api/tags'
import type { Tag } from '@/types/tag'

const router = useRouter()
const message = useMessage()

const {
  state: tags,
  isLoading,
  execute: reload,
} = useAsyncState(() => fetchTags(), [], { immediate: false, resetOnExecute: false })

async function handleDelete(id: number) {
  try {
    await deleteTag(id)
    message.success('已删除')
    await reload()
  } catch {
    message.error('删除失败')
  }
}

const columns = computed<DataTableColumns<Tag>>(() => [
  { title: 'ID', key: 'id', width: 60 },
  {
    title: '标签名称',
    key: 'name',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        NTag,
        { size: 'small', style: { backgroundColor: row.color, borderColor: row.color, color: '#fff' } },
        { default: () => row.name },
      )
    },
  },
  {
    title: '颜色标识',
    key: 'color',
    width: 180,
    render(row) {
      return h(
        NSpace,
        { size: 8, align: 'center' },
        () => [
          h('div', {
            style: {
              width: '24px',
              height: '24px',
              borderRadius: '4px',
              backgroundColor: row.color,
              border: '1px solid rgba(0,0,0,0.1)',
            },
          }),
          row.color.toUpperCase(),
        ],
      )
    },
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
            onClick: () => router.push(`/tags/${row.id}/edit`),
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
            default: () => '确定删除该标签？',
          },
        ),
      ])
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
        <h1>标签管理</h1>
        <p class="subtitle">管理售货机机型标签 · 名称 · 颜色标识</p>
      </div>
      <NSpace>
        <NButton @click="router.push('/')">机型图鉴</NButton>
        <NButton type="primary" @click="router.push('/tags/new')">
          新增标签
        </NButton>
      </NSpace>
    </header>

    <NCard class="list-card" title="标签列表">
      <NDataTable
        :columns="columns"
        :data="tags"
        :loading="isLoading"
        :bordered="false"
        striped
        :row-key="(row: Tag) => row.id"
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
