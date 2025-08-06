// 插件配置字段类型系统 - 参考 dify, n8n 等成熟工具的配置模式

/**
 * 基础字段类型
 */
export type FieldType = 
  | 'text'         // 文本输入
  | 'password'     // 密码输入
  | 'number'       // 数字输入
  | 'email'        // 邮箱输入
  | 'url'          // URL 输入
  | 'textarea'     // 多行文本
  | 'select'       // 下拉选择
  | 'multiselect' // 多选下拉
  | 'checkbox'     // 复选框
  | 'radio'        // 单选按钮
  | 'toggle'       // 开关按钮
  | 'slider'       // 滑块
  | 'date'         // 日期选择
  | 'datetime'     // 日期时间选择
  | 'time'         // 时间选择
  | 'file'         // 文件上传
  | 'color'        // 颜色选择
  | 'json'         // JSON 编辑器
  | 'code'         // 代码编辑器
  | 'keyvalue'     // 键值对
  | 'array'        // 数组
  | 'object'       // 对象
  | 'dynamic'      // 动态字段
  | 'condition'    // 条件字段
  | 'group'        // 字段组

/**
 * 字段验证规则
 */
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: string
  custom?: (value: any) => boolean | string
}

/**
 * 字段选项
 */
export interface FieldOption {
  label: string
  value: any
  description?: string
  disabled?: boolean
  icon?: string
}

/**
 * 条件显示规则
 */
export interface ConditionalDisplay {
  field: string
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'exists' | 'not_exists'
  value: any
}

/**
 * 基础配置字段接口
 */
export interface BaseConfigField {
  key: string
  label: string
  description?: string
  placeholder?: string
  defaultValue?: any
  required?: boolean
  disabled?: boolean
  readonly?: boolean
  hidden?: boolean
  tooltip?: string
  validation?: ValidationRule
  conditionalDisplay?: ConditionalDisplay[]
  group?: string
  order?: number
}

/**
 * 文本类型字段
 */
export interface TextConfigField extends BaseConfigField {
  type: 'text' | 'password' | 'email' | 'url'
  multiline?: boolean
  maxLength?: number
  minLength?: number
  pattern?: string
}

/**
 * 数字类型字段
 */
export interface NumberConfigField extends BaseConfigField {
  type: 'number' | 'slider'
  min?: number
  max?: number
  step?: number
  unit?: string
}

/**
 * 选择类型字段
 */
export interface SelectConfigField extends BaseConfigField {
  type: 'select' | 'multiselect' | 'radio'
  options: FieldOption[]
  allowCustomValue?: boolean
  multiple?: boolean
  searchable?: boolean
}

/**
 * 布尔类型字段
 */
export interface BooleanConfigField extends BaseConfigField {
  type: 'checkbox' | 'toggle'
  checkedLabel?: string
  uncheckedLabel?: string
}

/**
 * 日期时间类型字段
 */
export interface DateTimeConfigField extends BaseConfigField {
  type: 'date' | 'datetime' | 'time'
  format?: string
  timezone?: string
}

/**
 * 文件类型字段
 */
export interface FileConfigField extends BaseConfigField {
  type: 'file'
  accept?: string
  multiple?: boolean
  maxSize?: number
  maxFiles?: number
}

/**
 * 代码编辑器字段
 */
export interface CodeConfigField extends BaseConfigField {
  type: 'code'
  language?: string
  theme?: 'light' | 'dark'
  lineNumbers?: boolean
  wordWrap?: boolean
}

/**
 * JSON 编辑器字段
 */
export interface JsonConfigField extends BaseConfigField {
  type: 'json'
  schema?: object
  prettify?: boolean
}

/**
 * 数组类型字段
 */
export interface ArrayConfigField extends BaseConfigField {
  type: 'array'
  itemType: FieldType
  itemConfig?: Partial<ConfigField>
  minItems?: number
  maxItems?: number
  addButtonLabel?: string
  removeButtonLabel?: string
}

/**
 * 对象类型字段
 */
export interface ObjectConfigField extends BaseConfigField {
  type: 'object'
  fields: ConfigField[]
  collapsible?: boolean
  defaultCollapsed?: boolean
}

/**
 * 键值对类型字段
 */
export interface KeyValueConfigField extends BaseConfigField {
  type: 'keyvalue'
  keyLabel?: string
  valueLabel?: string
  keyType?: FieldType
  valueType?: FieldType
  minItems?: number
  maxItems?: number
}

/**
 * 字段组类型
 */
export interface GroupConfigField extends BaseConfigField {
  type: 'group'
  fields: ConfigField[]
  collapsible?: boolean
  defaultCollapsed?: boolean
  layout?: 'vertical' | 'horizontal' | 'grid'
}

/**
 * 条件字段类型
 */
export interface ConditionConfigField extends BaseConfigField {
  type: 'condition'
  conditions: Array<{
    when: ConditionalDisplay
    fields: ConfigField[]
  }>
  defaultFields?: ConfigField[]
}

/**
 * 动态字段类型
 */
export interface DynamicConfigField extends BaseConfigField {
  type: 'dynamic'
  sourceEndpoint?: string
  dependsOn?: string[]
  transform?: (value: any, context: any) => ConfigField[]
}

/**
 * 联合类型 - 所有配置字段类型
 */
export type ConfigField = 
  | TextConfigField
  | NumberConfigField
  | SelectConfigField
  | BooleanConfigField
  | DateTimeConfigField
  | FileConfigField
  | CodeConfigField
  | JsonConfigField
  | ArrayConfigField
  | ObjectConfigField
  | KeyValueConfigField
  | GroupConfigField
  | ConditionConfigField
  | DynamicConfigField

/**
 * 插件配置模板
 */
export interface PluginConfigTemplate {
  version: string
  sections: Array<{
    id: string
    title: string
    description?: string
    fields: ConfigField[]
    collapsible?: boolean
    defaultCollapsed?: boolean
  }>
  validation?: {
    rules?: ValidationRule[]
    async?: boolean
    endpoint?: string
  }
  preview?: {
    enabled: boolean
    endpoint?: string
    realtime?: boolean
  }
}

/**
 * 插件基本信息接口
 */
export interface Plugin {
  id: string
  name: string
  displayName: string
  version: string
  description: string
  longDescription?: string
  icon: string
  author: {
    name: string
    email?: string
    url?: string
  }
  category: string
  tags: string[]
  rating: number
  downloadCount: number
  configured: boolean
  enabled: boolean
  featured?: boolean
  verified?: boolean
  
  // 配置相关
  configTemplate: PluginConfigTemplate
  currentConfig?: Record<string, any>
  
  // 功能特性
  features: string[]
  requirements?: string[]
  permissions?: string[]
  
  // 元数据
  createdAt: string
  updatedAt: string
  supportUrl?: string
  documentationUrl?: string
  githubUrl?: string
  
  // 兼容性
  minVersion?: string
  maxVersion?: string
  dependencies?: Array<{
    id: string
    version: string
    optional?: boolean
  }>
}

/**
 * 插件分类
 */
export interface PluginCategory {
  id: string
  name: string
  description?: string
  icon: string
  plugins: Plugin[]
  featured?: boolean
  order?: number
}

/**
 * 插件配置保存请求
 */
export interface SavePluginConfigRequest {
  pluginId: string
  config: Record<string, any>
  validate?: boolean
  test?: boolean
}

/**
 * 插件配置验证响应
 */
export interface ValidateConfigResponse {
  valid: boolean
  errors?: Array<{
    field: string
    message: string
    code?: string
  }>
  warnings?: Array<{
    field: string
    message: string
  }>
}

/**
 * 插件操作响应
 */
export interface PluginActionResponse {
  success: boolean
  message?: string
  data?: any
  errors?: Array<{
    field?: string
    message: string
    code?: string
  }>
}