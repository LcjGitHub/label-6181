<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, NPopconfirm } from 'naive-ui'
import { deleteMachine, fetchMachine } from '@/api/machines'
import type { Machine } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const machineId = computed(() => {
  const raw = route.params.id
  if (typeof raw === 'string') {
    const parsed = Number(raw)
    if (Number.isFinite(parsed)) return parsed
  }
  return null
})

const machine = ref<Machine | null>(null)
const loading = ref(false)

async function loadMachine() {
  if (machineId.value === null) {
    message.error('无效的售货机编号')
    router.push('/')
    return
  }
  loading.value = true
  try {
    machine.value = await fetchMachine(machineId.value)
  } catch {
    message.error('加载售货机数据失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (machineId.value === null) return
  try {
    await deleteMachine(machineId.value)
    message.success('已删除')
    router.push('/')
  } catch {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadMachine()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>售货机详情</h1>
        <p class="subtitle">查看机型、地点、售卖品类、运作状态、照片描述与标签</p>
      </div>
      <NSpace>
        <NButton quaternary @click="router.push('/')">返回列表</NButton>
      </NSpace>
    </header>

    <NSpin :show="loading">
      <NCard v-if="machine" class="detail-card">
        <NDescriptions
          bordered
          label-placement="left"
          :column="1"
          label-style="width: 120px; font-weight: 500;"
        >
          <NDescriptionsItem label="ID">{{ machine.id }}</NDescriptionsItem>
          <NDescriptionsItem label="机型">{{ machine.model_type }}</NDescriptionsItem>
          <NDescriptionsItem label="地点">{{ machine.location }}</NDescriptionsItem>
          <NDescriptionsItem label="售卖品类">{{ machine.categories }}</NDescriptionsItem>
          <NDescriptionsItem label="制造年份">{{ machine.manufacturing_year || '未填写' }}</NDescriptionsItem>
          <NDescriptionsItem label="是否运作">
            <NTag
              :type="machine.is_operational ? 'success' : 'default'"
              size="small"
            >
              {{ machine.is_operational ? '运作中' : '已停运' }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="标签">
            <NSpace v-if="machine.tags && machine.tags.length > 0" size="small">
              <NTag
                v-for="tag in machine.tags"
                :key="tag.id"
                size="small"
                :style="{
                  backgroundColor: tag.color,
                  borderColor: tag.color,
                  color: '#fff',
                }"
              >
                {{ tag.name }}
              </NTag>
            </NSpace>
            <span v-else style="color: #999">无</span>
          </NDescriptionsItem>
          <NDescriptionsItem label="照片描述">
            {{ machine.photo_description || '无' }}
          </NDescriptionsItem>
        </NDescriptions>

        <NSpace style="margin-top: 24px">
          <NButton type="primary" @click="router.push(`/machines/${machine.id}/edit`)">
            编辑
          </NButton>
          <NPopconfirm @positive-click="handleDelete">
            <template #trigger>
              <NButton type="error">删除</NButton>
            </template>
            确定删除这台售货机？
          </NPopconfirm>
          <NButton @click="router.push('/')">返回列表</NButton>
        </NSpace>
      </NCard>
    </NSpin>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
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
  font-size: 1.5rem;
  color: #3d2f1f;
}

.subtitle {
  margin: 0;
  color: #7a6a55;
  font-size: 0.95rem;
}

.detail-card {
  background: #fffdf8;
  border: 1px solid #e8dcc8;
}
</style>
