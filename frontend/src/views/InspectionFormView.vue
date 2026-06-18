<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules, SelectOption } from 'naive-ui'
import { useAsyncState } from '@vueuse/core'
import { createInspection } from '@/api/inspections'
import { fetchMachines } from '@/api/machines'
import type { InspectionForm } from '@/types/inspection'
import type { Machine } from '@/types/machine'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)

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

const resultOptions: SelectOption[] = [
  { label: '正常', value: '正常' },
  { label: '异常', value: '异常' },
]

function getCurrentTime() {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const hh = String(now.getHours()).padStart(2, '0')
  const mm = String(now.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}`
}

const formModel = reactive<{
  machine_id: number | null
  inspection_time: string | null
  result: '正常' | '异常'
  remark: string
}>({
  machine_id: null,
  inspection_time: getCurrentTime(),
  result: '正常',
  remark: '',
})

watch(machineOptions, (opts) => {
  if (formModel.machine_id !== null) return
  if (queryMachineId.value !== null && opts.some((o) => o.value === queryMachineId.value)) {
    formModel.machine_id = queryMachineId.value
  } else if (opts.length > 0) {
    formModel.machine_id = opts[0].value as number
  }
}, { immediate: true })

const rules: FormRules = {
  machine_id: [
    {
      required: true,
      validator(_rule, value) {
        if (value === null || value === undefined) {
          return new Error('请选择售货机')
        }
        return true
      },
      trigger: 'change',
    },
  ],
  inspection_time: [
    {
      required: true,
      validator(_rule, value) {
        if (!value) {
          return new Error('请选择巡检时间')
        }
        return true
      },
      trigger: 'change',
    },
  ],
  result: [{ required: true, message: '请选择巡检结果', trigger: 'change' }],
  remark: [
    {
      validator(_rule, value) {
        if (formModel.result === '异常' && (!value || !value.trim())) {
          return new Error('巡检异常时请填写异常说明')
        }
        return true
      },
      trigger: 'blur',
    },
  ],
}

function backToList() {
  router.push('/inspections')
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (formModel.machine_id === null || !formModel.inspection_time) return
  submitting.value = true
  try {
    const payload: InspectionForm = {
      machine_id: formModel.machine_id,
      inspection_time: formModel.inspection_time,
      result: formModel.result,
      remark: formModel.remark,
    }
    await createInspection(payload)
    message.success('巡检打卡成功')
    backToList()
  } catch {
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>巡检打卡</h1>
        <p class="subtitle">选择售货机、巡检时间和结果，填写异常说明</p>
      </div>
      <NButton quaternary @click="backToList">返回巡检历史</NButton>
    </header>

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

        <NFormItem label="巡检时间" path="inspection_time">
          <NDatePicker
            v-model:formatted-value="formModel.inspection_time"
            type="datetime"
            value-format="yyyy-MM-dd HH:mm"
            format="yyyy-MM-dd HH:mm"
            placeholder="请选择巡检时间"
            style="width: 100%"
          />
        </NFormItem>

        <NFormItem label="巡检结果" path="result">
          <NSelect
            v-model:value="formModel.result"
            :options="resultOptions"
            placeholder="请选择巡检结果"
          />
        </NFormItem>

        <NFormItem label="异常说明" path="remark">
          <NInput
            v-model:value="formModel.remark"
            type="textarea"
            :rows="4"
            placeholder="巡检异常时请详细描述问题（正常时可留空）"
          />
        </NFormItem>

        <NFormItem>
          <NSpace>
            <NButton
              type="primary"
              :loading="submitting"
              @click="handleSubmit"
            >
              提交打卡
            </NButton>
            <NButton @click="backToList">取消</NButton>
          </NSpace>
        </NFormItem>
      </NForm>
    </NCard>
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
