import axios from 'axios'
import type { Inspection, InspectionForm, InspectionResultFilter } from '@/types/inspection'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取巡检记录列表
 * @param result - 巡检结果筛选
 */
export async function fetchInspections(
  result: InspectionResultFilter = 'all',
): Promise<Inspection[]> {
  const { data } = await http.get<Inspection[]>('/inspections', {
    params: { result },
  })
  return data
}

/**
 * 新增巡检记录
 * @param payload - 表单数据
 */
export async function createInspection(payload: InspectionForm): Promise<Inspection> {
  const { data } = await http.post<Inspection>('/inspections', payload)
  return data
}
