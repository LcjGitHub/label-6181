/** 维保记录实体 */
export interface Maintenance {
  id: number
  machine_id: number
  maintenance_date: string
  maintenance_type: string
  handler: string
  description: string
}

/** 创建/更新表单 */
export interface MaintenanceForm {
  machine_id: number
  maintenance_date: string
  maintenance_type: string
  handler: string
  description: string
}
