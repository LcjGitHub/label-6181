/** 巡检结果筛选 */
export type InspectionResultFilter = 'all' | '正常' | '异常'

/** 巡检记录实体 */
export interface Inspection {
  id: number
  machine_id: number
  inspection_time: string
  result: '正常' | '异常'
  remark: string
}

/** 创建表单 */
export interface InspectionForm {
  machine_id: number
  inspection_time: string
  result: '正常' | '异常'
  remark: string
}
