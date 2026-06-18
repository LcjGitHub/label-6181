<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { createMachine, fetchMachine, updateMachine } from '@/api/machines'
import type { MachineForm } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const machineId = computed(() => {
  const raw = route.params.id
  if (typeof raw === 'string' && raw !== 'new') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
})

const isEdit = computed(() => machineId.value !== null)

const formModel = reactive<MachineForm>({
  model_type: '',
  location: '',
  categories: '',
  is_operational: true,
  photo_description: '',
})

const rules: FormRules = {
  model_type: [{ required: true, message: '请输入机型', trigger: 'blur' }],
  location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
  categories: [{ required: true, message: '请输入售卖品类', trigger: 'blur' }],
}

/** 编辑模式加载数据 */
async function loadMachine() {
  if (!isEdit.value || machineId.value === null) return
  loading.value = true
  try {
    const data = await fetchMachine(machineId.value)
    Object.assign(formModel, {
      model_type: data.model_type,
      location: data.location,
      categories: data.categories,
      is_operational: data.is_operational,
      photo_description: data.photo_description,
    })
  } catch {
    message.error('加载失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

/** 提交表单 */
async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && machineId.value !== null) {
      await updateMachine(machineId.value, { ...formModel })
      message.success('已更新')
    } else {
      await createMachine({ ...formModel })
      message.success('已新增')
    }
    router.push('/')
  } catch {
    message.error('保存失败')
  } finally {
    submitting.value = false
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
        <h1>{{ isEdit ? '编辑售货机' : '新增售货机' }}</h1>
        <p class="subtitle">填写机型、地点、售卖品类、运作状态与照片描述</p>
      </div>
      <NButton quaternary @click="router.push('/')">返回列表</NButton>
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
          <NFormItem label="机型" path="model_type">
            <NInput
              v-model:value="formModel.model_type"
              placeholder="例如 National Vendo 44"
            />
          </NFormItem>

          <NFormItem label="地点" path="location">
            <NInput
              v-model:value="formModel.location"
              placeholder="例如 东京涩谷站东口"
            />
          </NFormItem>

          <NFormItem label="售卖品类" path="categories">
            <NInput
              v-model:value="formModel.categories"
              placeholder="例如 罐装饮料、咖啡"
            />
          </NFormItem>

          <NFormItem label="是否运作" path="is_operational">
            <NSwitch v-model:value="formModel.is_operational">
              <template #checked>运作中</template>
              <template #unchecked>已停运</template>
            </NSwitch>
          </NFormItem>

          <NFormItem label="照片描述" path="photo_description">
            <NInput
              v-model:value="formModel.photo_description"
              type="textarea"
              :rows="4"
              placeholder="描述机身外观、铭牌、玻璃门等细节"
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
              <NButton @click="router.push('/')">取消</NButton>
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
