/**
 * 联系人知识库业务逻辑 Hook
 * 处理联系人知识库管理相关业务逻辑
 */

import { useCallback } from 'react'
import { 
  ContactsService,
  type ContactKnowledgeResponse,
  type ContactType 
} from '@/services/api'
import { useContacts } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseContactsKnowledgeReturn {
  // State
  contactKnowledge: ContactKnowledgeResponse[]
  isLoading: boolean
  error: string | null
  
  // Actions
  loadContactKnowledgeBases: (contactId: string, contactType: ContactType) => Promise<void>
  addKnowledgeToContact: (contactId: string, contactType: ContactType, knowledgeBaseId: string, alias?: string) => Promise<boolean>
  removeKnowledgeFromContact: (contactId: string, contactType: ContactType, knowledgeBaseId: string) => Promise<boolean>
  clearError: () => void
}

export const useContactsKnowledge = (): UseContactsKnowledgeReturn => {
  const {
    contactKnowledge,
    contactsUI,
    error,
    setContactKnowledge,
    setLoading,
    setError,
    clearError: clearContactsError,
  } = useContacts()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearContactsError()
  }, [clearContactsError])

  const loadContactKnowledgeBases = useCallback(async (
    contactId: string,
    contactType: ContactType
  ): Promise<void> => {
    try {
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return
      }

      setLoading(true)
      setError(null)
      
      // 直接调用ContactsService
      const knowledge = await ContactsService.getContactKnowledgeBases(contactId.trim(), contactType)
      
      // 更新本地状态
      setContactKnowledge(knowledge)
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '加载知识库失败'
      
      setError(errorMessage, 'loadContactKnowledgeBases')
      console.error('Failed to load contact knowledge:', error)
      toasts.error('加载失败', errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError, setContactKnowledge, toasts])

  const addKnowledgeToContact = useCallback(async (
    contactId: string,
    contactType: ContactType,
    knowledgeBaseId: string,
    alias?: string
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      if (!knowledgeBaseId?.trim()) {
        toasts.error('错误', '知识库ID不能为空')
        return false
      }

      // 检查是否已经添加过
      const existingKnowledge = contactKnowledge.find(
        k => k.knowledge_base_id === knowledgeBaseId.trim()
      )
      
      if (existingKnowledge) {
        toasts.warning('提示', '该知识库已经添加过了')
        return false
      }

      // 直接调用ContactsService
      await ContactsService.addKnowledgeToContact(
        contactId.trim(), 
        contactType, 
        knowledgeBaseId.trim(),
        alias?.trim()
      )
      
      // 重新加载知识库列表
      await loadContactKnowledgeBases(contactId.trim(), contactType)
      
      toasts.success('成功', '知识库添加成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '添加知识库失败'
      
      toasts.error('添加失败', errorMessage)
      return false
    }
  }, [loadContactKnowledgeBases, contactKnowledge, toasts])

  const removeKnowledgeFromContact = useCallback(async (
    contactId: string,
    contactType: ContactType,
    knowledgeBaseId: string
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      if (!knowledgeBaseId?.trim()) {
        toasts.error('错误', '知识库ID不能为空')
        return false
      }

      // 确认删除
      const confirmed = window.confirm('确定要移除这个知识库吗？')
      if (!confirmed) {
        return false
      }

      // 直接调用ContactsService
      await ContactsService.removeKnowledgeFromContact(
        contactId.trim(), 
        contactType, 
        knowledgeBaseId.trim()
      )
      
      // 重新加载知识库列表
      await loadContactKnowledgeBases(contactId.trim(), contactType)
      
      toasts.success('成功', '知识库移除成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '移除知识库失败'
      
      toasts.error('移除失败', errorMessage)
      return false
    }
  }, [loadContactKnowledgeBases, toasts])

  return {
    // State
    contactKnowledge,
    isLoading: contactsUI.isLoading,
    error: error.current,
    
    // Actions
    loadContactKnowledgeBases,
    addKnowledgeToContact,
    removeKnowledgeFromContact,
    clearError,
  }
}