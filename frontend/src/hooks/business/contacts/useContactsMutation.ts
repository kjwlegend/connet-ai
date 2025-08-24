/**
 * 联系人变更业务逻辑 Hook
 * 处理联系人的创建、更新、删除等变更操作
 */

import { useCallback } from 'react'
import { 
  ContactsService, 
  type ContactCreateRequest, 
  type ContactUpdateRequest, 
  type ContactResponse,
  type ContactType 
} from '@/services/api'
import { useContacts } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseContactsMutationReturn {
  // State
  isCreating: boolean
  isUpdating: boolean
  isDeleting: boolean
  error: string | null
  
  // Actions
  createContact: (data: ContactCreateRequest) => Promise<ContactResponse | null>
  updateContact: (contactId: string, contactType: ContactType, data: ContactUpdateRequest) => Promise<ContactResponse | null>
  deleteContact: (contactId: string, contactType: ContactType) => Promise<boolean>
  toggleFavorite: (contactId: string, contactType: ContactType) => Promise<boolean>
  clearError: () => void
}

export const useContactsMutation = (): UseContactsMutationReturn => {
  const {
    contactsUI,
    error,
    addContact,
    updateContactInList,
    removeContactFromList,
    setCurrentContact,
    setLoading,
    setError,
    clearError: clearContactsError,
  } = useContacts()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearContactsError()
  }, [clearContactsError])

  const createContact = useCallback(async (
    data: ContactCreateRequest
  ): Promise<ContactResponse | null> => {
    try {
      // 输入验证
      if (!data.following_id?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return null
      }

      if (!data.following_type) {
        toasts.error('错误', '联系人类型不能为空')
        return null
      }

      // 直接调用ContactsService
      const contact = await ContactsService.createContact({
        ...data,
        following_id: data.following_id.trim(),
      })

      // 更新本地状态
      if (contact) {
        addContact(contact)
        toasts.success('成功', '联系人添加成功')
      }

      return contact
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '添加联系人失败'
      
      toasts.error('添加失败', errorMessage)
      return null
    }
  }, [addContact, toasts])

  const updateContact = useCallback(async (
    contactId: string,
    contactType: ContactType,
    data: ContactUpdateRequest
  ): Promise<ContactResponse | null> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return null
      }

      // 直接调用ContactsService  
      const contact = await ContactsService.updateContact(contactId.trim(), contactType, data)

      // 更新本地状态
      if (contact) {
        updateContactInList(contact)
        toasts.success('成功', '联系人更新成功')
      }

      return contact
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '更新联系人失败'
      
      toasts.error('更新失败', errorMessage)
      return null
    }
  }, [updateContactInList, toasts])

  const deleteContact = useCallback(async (
    contactId: string,
    contactType: ContactType
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      // 确认删除
      const confirmed = window.confirm('确定要删除这个联系人吗？此操作不可撤销。')
      if (!confirmed) {
        return false
      }

      // 直接调用ContactsService
      await ContactsService.deleteContact(contactId.trim(), contactType)
      
      // 更新本地状态
      removeContactFromList(contactId.trim(), contactType)
      
      toasts.success('成功', '联系人删除成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '删除联系人失败'
      
      toasts.error('删除失败', errorMessage)
      return false
    }
  }, [removeContactFromList, toasts])

  const toggleFavorite = useCallback(async (
    contactId: string,
    contactType: ContactType
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!contactId?.trim()) {
        toasts.error('错误', '联系人ID不能为空')
        return false
      }

      // 直接调用ContactsService
      const isFavorite = await ContactsService.toggleFavorite(contactId.trim(), contactType)
      
      // 更新本地状态 - 重新获取联系人信息
      try {
        const updatedContact = await ContactsService.getContact(contactId.trim(), contactType)
        if (updatedContact) {
          updateContactInList(updatedContact)
        }
      } catch {
        // 如果获取失败，忽略错误，只更新收藏状态
      }
      
      const message = isFavorite ? '已添加到收藏' : '已从收藏中移除'
      toasts.success('成功', message)
      
      return isFavorite
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '操作失败'
      
      toasts.error('操作失败', errorMessage)
      return false
    }
  }, [updateContactInList, toasts])

  return {
    // State
    isCreating: contactsUI.isCreating,
    isUpdating: contactsUI.isUpdating,
    isDeleting: contactsUI.isDeleting,
    error: error.current,
    
    // Actions
    createContact,
    updateContact,
    deleteContact,
    toggleFavorite,
    clearError,
  }
}