import axios from 'axios'
import type { Maintenance, MaintenanceForm } from '@/types/maintenance'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取维保记录列表
 * @param machineId - 可选，按售货机编号筛选
 */
export async function fetchMaintenances(
  machineId?: number,
): Promise<Maintenance[]> {
  const { data } = await http.get<Maintenance[]>('/maintenances', {
    params: machineId !== undefined ? { machine_id: machineId } : {},
  })
  return data
}

/**
 * 获取单条维保记录
 * @param id - 维保记录 ID
 */
export async function fetchMaintenance(id: number): Promise<Maintenance> {
  const { data } = await http.get<Maintenance>(`/maintenances/${id}`)
  return data
}

/**
 * 新增维保记录
 * @param payload - 表单数据
 */
export async function createMaintenance(payload: MaintenanceForm): Promise<Maintenance> {
  const { data } = await http.post<Maintenance>('/maintenances', payload)
  return data
}

/**
 * 更新维保记录
 * @param id - 维保记录 ID
 * @param payload - 表单数据
 */
export async function updateMaintenance(
  id: number,
  payload: MaintenanceForm,
): Promise<Maintenance> {
  const { data } = await http.put<Maintenance>(`/maintenances/${id}`, payload)
  return data
}

/**
 * 删除维保记录
 * @param id - 维保记录 ID
 */
export async function deleteMaintenance(id: number): Promise<void> {
  await http.delete(`/maintenances/${id}`)
}

export async function batchDeleteMaintenances(ids: number[]): Promise<void> {
  await http.post('/maintenances/batch-delete', { ids })
}
