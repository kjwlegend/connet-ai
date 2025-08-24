/**
 * 联系人查询业务逻辑 Hook
 * 处理联系人列表获取、分页、筛选等查询相关业务逻辑
 */

import { useCallback, useEffect } from 'react'
import { ContactsService, type ContactListParams, type ContactResponse } from '@/services/api'
import { useContacts } from '@/store/index'

interface UseContactsQueryReturn {
  // State
  contacts: ContactResponse[]
  isLoading: boolean
  error: string | null
  pagination: {
    skip: number
    limit: number
    hasMore: boolean
    total: number
  }
  filters: {
    contactType?: string
    status?: string
    tags?: string[]
    favoritesOnly?: boolean
    search?: string
  }
  
  // Actions
  loadContacts: (params?: ContactListParams, append?: boolean) => Promise<void>
  getContact: (contactId: string, contactType: any) => Promise<ContactResponse | null>
  refreshContacts: () => Promise<void>
  loadMoreContacts: () => Promise<void>
  setFilters: (filters: any) => void
  clearFilters: () => void
  clearError: () => void
}

export const useContactsQuery = (): UseContactsQueryReturn => {
  const {
    contacts,
    pagination,
    contactsFilters: filters,
    contactsUI,
    error,
    setContacts,
    setLoading,
    setError,
    setFilters: setContactsFilters,
    clearError: clearContactsError,
    setPagination,
    resetPagination,
  } = useContacts()

  const clearError = useCallback(() => {
    clearContactsError()
  }, [clearContactsError])

  const loadContacts = useCallback(async (
    params: ContactListParams = {},
    append = false
  ): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      
      // 直接调用ContactsService
      const result = await ContactsService.getUserContacts(params)
      
      // 更新本地状态
      if (append) {
        setContacts([...contacts, ...result.contacts])
      } else {
        setContacts(result.contacts)
      }
      
      // 更新分页信息
      setPagination({
        skip: (params.skip || 0) + result.contacts.length,
        limit: params.limit || 20,
        hasMore: result.contacts.length === (params.limit || 20),
        total: result.total || result.contacts.length
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '加载联系人失败'
      setError(errorMessage, 'loadContacts')
      console.error('Failed to load contacts:', error)
    } finally {
      setLoading(false)
    }
  }, [contacts, setContacts, setLoading, setError, setPagination])

  const refreshContacts = useCallback(async (): Promise<void> => {
    try {
      resetPagination()
      await loadContacts({ skip: 0 })
    } catch (error) {
      console.error('Failed to refresh contacts:', error)
    }
  }, [loadContacts, resetPagination])

  const loadMoreContacts = useCallback(async (): Promise<void> => {
    if (!pagination.hasMore || contactsUI.isLoading) return
    
    try {
      await loadContacts({ ...filters, skip: pagination.skip }, true)
    } catch (error) {
      console.error('Failed to load more contacts:', error)
    }
  }, [loadContacts, filters, pagination.hasMore, pagination.skip, contactsUI.isLoading])

  const setFilters = useCallback((newFilters: any) => {
    setContactsFilters(newFilters)
    resetPagination()
    // 应用新筛选条件后重新加载
    loadContacts({ ...newFilters, skip: 0 })
  }, [setContactsFilters, loadContacts, resetPagination])

  const clearFilters = useCallback(() => {
    setContactsFilters({})
    resetPagination()
    // 清除筛选条件后重新加载
    loadContacts({ skip: 0 })
  }, [setContactsFilters, loadContacts, resetPagination])

  const getContact = useCallback(async (
    contactId: string, 
    contactType: any
  ): Promise<ContactResponse | null> => {
    try {
      setError(null)
      const contact = await ContactsService.getContact(contactId, contactType)
      return contact
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取联系人失败'
      setError(errorMessage, 'getContact')
      return null
    }
  }, [setError])

  // 自动加载初始数据
  useEffect(() => {
    if (contacts.length === 0 && !contactsUI.isLoading) {
      loadContacts()
    }
  }, []) // 只在组件挂载时执行

  return {
    // State
    contacts,
    isLoading: contactsUI.isLoading,
    error: error.current,
    pagination,
    filters,
    
    // Actions
    loadContacts,
    getContact,
    refreshContacts,
    loadMoreContacts,
    setFilters,
    clearFilters,
    clearError,
  }
}