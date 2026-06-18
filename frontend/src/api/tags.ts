import axios from 'axios'
import type { Tag, TagForm } from '@/types/tag'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

/**
 * 获取标签列表
 */
export async function fetchTags(): Promise<Tag[]> {
  const { data } = await http.get<Tag[]>('/tags')
  return data
}

/**
 * 获取单个标签
 * @param id - 标签 ID
 */
export async function fetchTag(id: number): Promise<Tag> {
  const { data } = await http.get<Tag>(`/tags/${id}`)
  return data
}

/**
 * 新增标签
 * @param payload - 表单数据
 */
export async function createTag(payload: TagForm): Promise<Tag> {
  const { data } = await http.post<Tag>('/tags', payload)
  return data
}

/**
 * 更新标签
 * @param id - 标签 ID
 * @param payload - 表单数据
 */
export async function updateTag(id: number, payload: TagForm): Promise<Tag> {
  const { data } = await http.put<Tag>(`/tags/${id}`, payload)
  return data
}

/**
 * 删除标签
 * @param id - 标签 ID
 */
export async function deleteTag(id: number): Promise<void> {
  await http.delete(`/tags/${id}`)
}
