<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { createTag, fetchTag, updateTag } from '@/api/tags'
import type { TagForm } from '@/types/tag'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const tagId = computed(() => {
  const raw = route.params.id
  if (typeof raw === 'string' && raw !== 'new') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
})

const isEdit = computed(() => tagId.value !== null)

const formModel = reactive<TagForm>({
  name: '',
  color: '#18a058',
})

const presetColors = [
  '#e53935', '#fb8c00', '#fdd835', '#43a047',
  '#00897b', '#1e88e5', '#8e24aa', '#d81b60',
  '#6d4c41', '#546e7a', '#18a058', '#263238',
]

const rules: FormRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  color: [{ required: true, message: '请选择或输入颜色', trigger: 'blur' }],
}

async function loadTag() {
  if (!isEdit.value || tagId.value === null) return
  loading.value = true
  try {
    const data = await fetchTag(tagId.value)
    Object.assign(formModel, {
      name: data.name,
      color: data.color,
    })
  } catch {
    message.error('加载失败')
    router.push('/tags')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && tagId.value !== null) {
      await updateTag(tagId.value, { ...formModel })
      message.success('已更新')
    } else {
      await createTag({ ...formModel })
      message.success('已新增')
    }
    router.push('/tags')
  } catch {
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadTag()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>{{ isEdit ? '编辑标签' : '新增标签' }}</h1>
        <p class="subtitle">填写标签名称与颜色标识</p>
      </div>
      <NButton quaternary @click="router.push('/tags')">返回列表</NButton>
    </header>

    <NSpin :show="loading">
      <NCard class="form-card">
        <NForm
          ref="formRef"
          :model="formModel"
          :rules="rules"
          label-placement="left"
          label-width="100"
          require-mark-placement="right-hanging"
        >
          <NFormItem label="标签名称" path="name">
            <NInput
              v-model:value="formModel.name"
              placeholder="例如 经典红色"
            />
          </NFormItem>

          <NFormItem label="颜色标识" path="color">
            <div class="color-field">
              <NColorPicker
                v-model:value="formModel.color"
                show-alpha
                :modes="['hex']"
                style="width: 100%"
              />
              <div class="preset-colors">
                <div
                  v-for="color in presetColors"
                  :key="color"
                  class="preset-color"
                  :class="{ active: formModel.color.toLowerCase() === color.toLowerCase() }"
                  :style="{ backgroundColor: color }"
                  @click="formModel.color = color"
                />
              </div>
            </div>
          </NFormItem>

          <NFormItem>
            <NSpace>
              <NButton
                type="primary"
                :loading="submitting"
                @click="handleSubmit"
              >
                保存
              </NButton>
              <NButton @click="router.push('/tags')">取消</NButton>
            </NSpace>
          </NFormItem>
        </NForm>
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

.form-card {
  background: #fffdf8;
  border: 1px solid #e8dcc8;
}

.color-field {
  width: 100%;
}

.preset-colors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.preset-color {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s ease;
}

.preset-color:hover {
  transform: scale(1.1);
}

.preset-color.active {
  border-color: #3d2f1f;
  box-shadow: 0 0 0 2px rgba(61, 47, 31, 0.15);
}
</style>
