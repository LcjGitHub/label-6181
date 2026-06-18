<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules, SelectOption } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { createMaintenance, fetchMaintenance, updateMaintenance } from '@/api/maintenances'
import { fetchMachines } from '@/api/machines'
import type { MaintenanceForm } from '@/types/maintenance'
import type { Machine } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const maintenanceId = computed(() => {
  const raw = route.params.id
  if (typeof raw === 'string' && raw !== 'new') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
})

const isEdit = computed(() => maintenanceId.value !== null)

const queryMachineId = computed(() => {
  const raw = route.query.machine_id
  if (typeof raw === 'string') {
    const parsed = Number(raw)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
})

const { state: machines, isLoading: machinesLoading } = useAsyncState(
  () => fetchMachines('all'),
  [] as Machine[],
  { immediate: true },
)

const machineOptions = computed<SelectOption[]>(() =>
  machines.value.map((m) => ({
    label: `#${m.id} · ${m.model_type} (${m.location})`,
    value: m.id,
  })),
)

const maintenanceTypeOptions: SelectOption[] = [
  { label: '日常巡检', value: '日常巡检' },
  { label: '清洁保养', value: '清洁保养' },
  { label: '零部件更换', value: '零部件更换' },
  { label: '故障维修', value: '故障维修' },
  { label: '系统升级', value: '系统升级' },
  { label: '其他', value: '其他' },
]

const formModel = reactive<MaintenanceForm>({
  machine_id: queryMachineId.value ?? 1,
  maintenance_date: new Date().toISOString().slice(0, 10),
  maintenance_type: '日常巡检',
  handler: '',
  description: '',
})

const rules: FormRules = {
  machine_id: [{ required: true, message: '请选择售货机', trigger: 'change' }],
  maintenance_date: [{ required: true, message: '请选择维保日期', trigger: 'change' }],
  maintenance_type: [{ required: true, message: '请选择维保类型', trigger: 'change' }],
  handler: [{ required: true, message: '请输入经办人', trigger: 'blur' }],
}

function backToList() {
  if (formModel.machine_id) {
    router.push(`/machines/${formModel.machine_id}/maintenances`)
  } else {
    router.push('/maintenances')
  }
}

async function loadMaintenance() {
  if (!isEdit.value || maintenanceId.value === null) return
  loading.value = true
  try {
    const data = await fetchMaintenance(maintenanceId.value)
    Object.assign(formModel, {
      machine_id: data.machine_id,
      maintenance_date: data.maintenance_date,
      maintenance_type: data.maintenance_type,
      handler: data.handler,
      description: data.description,
    })
  } catch {
    message.error('加载失败')
    router.push('/maintenances')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && maintenanceId.value !== null) {
      await updateMaintenance(maintenanceId.value, { ...formModel })
      message.success('已更新')
    } else {
      await createMaintenance({ ...formModel })
      message.success('已新增')
    }
    backToList()
  } catch {
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMaintenance()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>{{ isEdit ? '编辑维保记录' : '新增维保记录' }}</h1>
        <p class="subtitle">填写售货机、维保日期、类型、经办人与说明</p>
      </div>
      <NButton quaternary @click="backToList">返回列表</NButton>
    </header>

    <NSpin :show="loading || machinesLoading">
      <NCard class="form-card">
        <NForm
          ref="formRef"
          :model="formModel"
          :rules="rules"
          label-placement="left"
          label-width="100"
          require-mark-placement="right-hanging"
        >
          <NFormItem label="售货机" path="machine_id">
            <NSelect
              v-model:value="formModel.machine_id"
              :options="machineOptions"
              :loading="machinesLoading"
              placeholder="请选择售货机"
              clearable
              filterable
            />
          </NFormItem>

          <NFormItem label="维保日期" path="maintenance_date">
            <NDatePicker
              v-model:value="formModel.maintenance_date"
              type="date"
              value-format="yyyy-MM-dd"
              placeholder="请选择维保日期"
              style="width: 100%"
            />
          </NFormItem>

          <NFormItem label="维保类型" path="maintenance_type">
            <NSelect
              v-model:value="formModel.maintenance_type"
              :options="maintenanceTypeOptions"
              placeholder="请选择维保类型"
              allow-create
              clearable
            />
          </NFormItem>

          <NFormItem label="经办人" path="handler">
            <NInput
              v-model:value="formModel.handler"
              placeholder="例如 张工 / 李师傅"
            />
          </NFormItem>

          <NFormItem label="维保说明" path="description">
            <NInput
              v-model:value="formModel.description"
              type="textarea"
              :rows="4"
              placeholder="详细描述维保内容、更换的部件、发现的问题等"
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
              <NButton @click="backToList">取消</NButton>
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
