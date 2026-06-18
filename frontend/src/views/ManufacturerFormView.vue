<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { createManufacturer, fetchManufacturer, updateManufacturer } from '@/api/manufacturers'
import type { ManufacturerForm } from '@/types/manufacturer'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const manufacturerId = computed(() => {
  const raw = route.params.id
  if (typeof raw === 'string' && raw !== 'new') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
})

const isEdit = computed(() => manufacturerId.value !== null)

const formModel = reactive<ManufacturerForm>({
  brand_name: '',
  country: '',
  founded_year: 1950,
  description: '',
})

const rules: FormRules = {
  brand_name: [{ required: true, message: '请输入品牌名称', trigger: 'blur' }],
  country: [{ required: true, message: '请输入所属国家', trigger: 'blur' }],
  founded_year: [{ required: true, type: 'number', message: '请输入成立年份', trigger: 'blur' }],
}

async function loadManufacturer() {
  if (!isEdit.value || manufacturerId.value === null) return
  loading.value = true
  try {
    const data = await fetchManufacturer(manufacturerId.value)
    Object.assign(formModel, {
      brand_name: data.brand_name,
      country: data.country,
      founded_year: data.founded_year,
      description: data.description,
    })
  } catch {
    message.error('加载失败')
    router.push('/manufacturers')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && manufacturerId.value !== null) {
      await updateManufacturer(manufacturerId.value, { ...formModel })
      message.success('已更新')
    } else {
      await createManufacturer({ ...formModel })
      message.success('已新增')
    }
    router.push('/manufacturers')
  } catch {
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadManufacturer()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>{{ isEdit ? '编辑厂商' : '新增厂商' }}</h1>
        <p class="subtitle">填写品牌名称、所属国家、成立年份与简介</p>
      </div>
      <NButton quaternary @click="router.push('/manufacturers')">返回列表</NButton>
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
          <NFormItem label="品牌名称" path="brand_name">
            <NInput
              v-model:value="formModel.brand_name"
              placeholder="例如 National"
            />
          </NFormItem>

          <NFormItem label="所属国家" path="country">
            <NInput
              v-model:value="formModel.country"
              placeholder="例如 日本"
            />
          </NFormItem>

          <NFormItem label="成立年份" path="founded_year">
            <NInputNumber
              v-model:value="formModel.founded_year"
              :min="1800"
              :max="2100"
              placeholder="例如 1925"
              style="width: 100%"
            />
          </NFormItem>

          <NFormItem label="简介" path="description">
            <NInput
              v-model:value="formModel.description"
              type="textarea"
              :rows="4"
              placeholder="描述品牌历史、主营产品等"
            />
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
              <NButton @click="router.push('/manufacturers')">取消</NButton>
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
</style>
