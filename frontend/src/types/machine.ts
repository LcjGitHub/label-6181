import type { Tag } from '@/types/tag'

/** 运作状态筛选 */
export type OperationalFilter = 'all' | 'true' | 'false'

/** 售货机实体 */
export interface Machine {
  id: number
  model_type: string
  location: string
  categories: string
  is_operational: boolean
  photo_description: string
  tags: Tag[]
}

/** 创建/更新表单 */
export interface MachineForm {
  model_type: string
  location: string
  categories: string
  is_operational: boolean
  photo_description: string
  tag_ids: number[]
}

/** 地点分布统计 */
export interface LocationStats {
  location: string
  count: number
}

/** 售卖品类统计 */
export interface CategoryStats {
  category: string
  count: number
}

/** 分页响应 */
export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/** 统计看板数据 */
export interface StatisticsData {
  total_machines: number
  operational_count: number
  out_of_service_count: number
  location_distribution: LocationStats[]
  category_rankings: CategoryStats[]
}
