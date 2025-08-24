/**
 * 联系人工具管理业务逻辑 Hook
 * 处理联系人工具配置相关业务逻辑
 */

import { useCallback } from 'react'
import { 
  ContactsService,
  type ContactToolResponse,
  type ContactType 
} from '@/services/api'
import { useContacts } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseContactsToolsReturn {
  // State
  contactTools: ContactToolResponse[]
  isLoading: boolean
  error: string | null
  
  // Actions
  loadContactTools: (contactId: string, contactType: ContactType) => Promise<void>
  addToolToContact: (contactId: string, contactType: ContactType, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<boolean>
  removeToolFromContact: (contactId: string, contactType: ContactType, toolId: string) => Promise<boolean>
  updateContactToolConfig: (contactId: string, contactType: ContactType, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<boolean>
  clearError: () => void
}

export const useContactsTools = (): UseContactsToolsReturn => {
  const {
    contactTools,
    contactsUI,
    error,
    setContactTools,
    setLoading,
    setError,
    clearError: clearContactsError,
  } = useContacts()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearContactsError()
  }, [clearContactsError])

  const loadContactTools = useCallback(async (
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
      const tools = await ContactsService.getContactTools(contactId.trim(), contactType)
      
      // 更新本地状态
      setContactTools(tools)
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '加载工具列表失败'
      
      setError(errorMessage, 'loadContactTools')
      console.error('Failed to load contact tools:', error)
      toasts.error('加载失败', errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError, setContactTools, toasts])

  const addToolToContact = useCallback(async (
    contactId: string,
    contactType: ContactType,
    toolId: string,
    enabled = true,
    toolConfig?: Record<string, any>
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      if (!toolId?.trim()) {
        toasts.error('错误', '工具ID不能为空')
        return false
      }

      // 检查是否已经添加过
      const existingTool = contactTools.find(
        t => t.tool_id === toolId.trim()
      )
      
      if (existingTool) {
        toasts.warning('提示', '该工具已经添加过了')
        return false
      }

      // 验证工具配置
      if (toolConfig && typeof toolConfig !== 'object') {
        toasts.error('错误', '工具配置格式不正确')
        return false
      }

      // 直接调用ContactsService
      await ContactsService.addToolToContact(
        contactId.trim(), 
        contactType, 
        toolId.trim(),
        enabled,
        toolConfig
      )
      
      // 重新加载工具列表
      await loadContactTools(contactId.trim(), contactType)
      
      toasts.success('成功', '工具添加成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '添加工具失败'
      
      toasts.error('添加失败', errorMessage)
      return false
    }
  }, [loadContactTools, contactTools, toasts])

  const removeToolFromContact = useCallback(async (
    contactId: string,
    contactType: ContactType,
    toolId: string
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      if (!toolId?.trim()) {
        toasts.error('错误', '工具ID不能为空')
        return false
      }

      // 确认删除
      const confirmed = window.confirm('确定要移除这个工具吗？')
      if (!confirmed) {
        return false
      }

      // 直接调用ContactsService
      await ContactsService.removeToolFromContact(
        contactId.trim(), 
        contactType, 
        toolId.trim()
      )
      
      // 重新加载工具列表
      await loadContactTools(contactId.trim(), contactType)
      
      toasts.success('成功', '工具移除成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '移除工具失败'
      
      toasts.error('移除失败', errorMessage)
      return false
    }
  }, [loadContactTools, toasts])

  const updateContactToolConfig = useCallback(async (
    contactId: string,
    contactType: ContactType,
    toolId: string,
    enabled?: boolean,
    toolConfig?: Record<string, any>
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      if (!toolId?.trim()) {
        toasts.error('错误', '工具ID不能为空')
        return false
      }

      // 验证工具配置
      if (toolConfig && typeof toolConfig !== 'object') {
        toasts.error('错误', '工具配置格式不正确')
        return false
      }

      // 直接调用ContactsService
      await ContactsService.updateContactToolConfig(
        contactId.trim(), 
        contactType, 
        toolId.trim(),
        enabled,
        toolConfig
      )
      
      // 重新加载工具列表
      await loadContactTools(contactId.trim(), contactType)
      
      toasts.success('成功', '工具配置更新成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '更新工具配置失败'
      
      toasts.error('更新失败', errorMessage)
      return false
    }
  }, [loadContactTools, toasts])

  return {
    // State
    contactTools,
    isLoading: contactsUI.isLoading,
    error: error.current,
    
    // Actions
    loadContactTools,
    addToolToContact,
    removeToolFromContact,
    updateContactToolConfig,
    clearError,
  }
}