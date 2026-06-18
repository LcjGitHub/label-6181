import axios from 'axios'
import type { Machine, MachineForm, OperationalFilter } from '@/types/machine'
import type { Tag } from '@/types/tag'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取售货机列表
 * @param operational - 运作状态筛选
 * @param tagId - 标签 ID 筛选，null 表示全部
 */
export async function fetchMachines(
  operational: OperationalFilter = 'all',
  tagId: number | null = null,
): Promise<Machine[]> {
  const params: Record<string, unknown> = { operational }
  if (tagId !== null) {
    params.tag_id = tagId
  }
  const { data } = await http.get<Machine[]>('/machines', { params })
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

/**
 * 为售货机设置标签（专用接口）
 * @param machineId - 售货机 ID
 * @param tagIds - 标签 ID 列表，空数组表示清除所有标签
 */
export async function setMachineTags(
  machineId: number,
  tagIds: number[],
): Promise<Tag[]> {
  const { data } = await http.put<Tag[]>(`/machines/${machineId}/tags`, {
    tag_ids: tagIds,
  })
  return data
}
