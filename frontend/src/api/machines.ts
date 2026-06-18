import axios from 'axios'
import type { Machine, MachineForm, OperationalFilter } from '@/types/machine'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取售货机列表
 * @param operational - 运作状态筛选
 */
export async function fetchMachines(
  operational: OperationalFilter = 'all',
): Promise<Machine[]> {
  const { data } = await http.get<Machine[]>('/machines', {
    params: { operational },
  })
  return data
}

/**
 * 获取单台售货机
 * @param id - 售货机 ID
 */
export async function fetchMachine(id: number): Promise<Machine> {
  const { data } = await http.get<Machine>(`/machines/${id}`)
  return data
}

/**
 * 新增售货机
 * @param payload - 表单数据
 */
export async function createMachine(payload: MachineForm): Promise<Machine> {
  const { data } = await http.post<Machine>('/machines', payload)
  return data
}

/**
 * 更新售货机
 * @param id - 售货机 ID
 * @param payload - 表单数据
 */
export async function updateMachine(
  id: number,
  payload: MachineForm,
): Promise<Machine> {
  const { data } = await http.put<Machine>(`/machines/${id}`, payload)
  return data
}

/**
 * 删除售货机
 * @param id - 售货机 ID
 */
export async function deleteMachine(id: number): Promise<void> {
  await http.delete(`/machines/${id}`)
}
