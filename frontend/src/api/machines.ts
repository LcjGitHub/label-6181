import axios from 'axios'
import type { Machine, MachineForm, OperationalFilter, PageData, StatisticsData } from '@/types/machine'
import type { Tag } from '@/types/tag'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取售货机列表（分页）
 * @param operational - 运作状态筛选
 * @param tagId - 标签 ID 筛选，null 表示全部
 * @param keyword - 关键词搜索，按机型、地点、售卖品类、照片描述模糊匹配，空字符串表示不搜索；可与运作状态、标签筛选组合使用
 * @param page - 页码，从 1 开始
 * @param pageSize - 每页条数
 */
export async function fetchMachines(
  operational: OperationalFilter = 'all',
  tagId: number | null = null,
  keyword: string = '',
  page: number = 1,
  pageSize: number = 10,
): Promise<PageData<Machine>> {
  const params: Record<string, unknown> = { operational, page, page_size: pageSize }
  if (tagId !== null) {
    params.tag_id = tagId
  }
  if (keyword.trim()) {
    params.keyword = keyword.trim()
  }
  const { data } = await http.get<PageData<Machine>>('/machines', { params })
  return data
}

/**
 * 循环分页拉取全部售货机（用于下拉选项等场景）
 * 每次按最大允许 pageSize=100 拉取，直到取完为止
 */
export async function fetchAllMachines(): Promise<Machine[]> {
  const all: Machine[] = []
  let currentPage = 1
  const pageSize = 100
  while (true) {
    const result = await fetchMachines('all', null, '', currentPage, pageSize)
    all.push(...result.items)
    if (all.length >= result.total || result.items.length < pageSize) {
      break
    }
    currentPage += 1
  }
  return all
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

/**
 * 获取统计看板数据
 */
export async function fetchStatistics(): Promise<StatisticsData> {
  const { data } = await http.get<StatisticsData>('/statistics')
  return data
}
