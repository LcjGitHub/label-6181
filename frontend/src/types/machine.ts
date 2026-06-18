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
}

/** 创建/更新表单 */
export interface MachineForm {
  model_type: string
  location: string
  categories: string
  is_operational: boolean
  photo_description: string
}
