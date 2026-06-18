/** 标签实体 */
export interface Tag {
  id: number
  name: string
  color: string
}

/** 创建/更新标签表单 */
export interface TagForm {
  name: string
  color: string
}
