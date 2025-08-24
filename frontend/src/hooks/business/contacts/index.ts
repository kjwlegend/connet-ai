/**
 * Contacts Business Hooks 入口文件
 * 统一导出所有联系人相关的业务逻辑 hooks
 */

export { useContactsQuery } from './useContactsQuery'
export { useContactsMutation } from './useContactsMutation'
export { useContactsSearch } from './useContactsSearch'
export { useContactsKnowledge } from './useContactsKnowledge'
export { useContactsTools } from './useContactsTools'

// 类型导出
export type { 
  ContactResponse,
  ContactCreateRequest,
  ContactUpdateRequest,
  ContactSearchResponse,
  ContactKnowledgeResponse,
  ContactToolResponse,
  ContactType 
} from '@/services/api'