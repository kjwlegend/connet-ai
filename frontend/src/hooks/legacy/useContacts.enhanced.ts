/**
 * Enhanced useContacts hook - Integration with new store and API service architecture
 * 
 * This demonstrates the best practices for:
 * - API service integration
 * - Store state management
 * - Error handling and user feedback
 * - Optimistic updates
 * - Caching and performance
 */

'use client'

import { useCallback } from 'react'
import { contactService } from '@/services/api/contactService' // Will be created
import { 
  useContactsStore, // From store/hooks/useOptimizedSelectors.ts
  useToasts,       // From store/index.new.ts
} from '@/store'
import { AIAgent, ContactRequest, UseContactsReturn, AddContactSearchResult } from '@/types/contact'

export function useContacts(): UseContactsReturn {
  // Get state and actions from optimized store selectors
  const {
    contacts,
    pendingRequests,
    isLoading,
    error,
    // Store actions - pure state operations
    addContactToStore,
    removeContactFromStore,
    updateContactInStore,
    addPendingRequest,
    removePendingRequest,
    setLoading,
    setError,
    clearError,
  } = useContactsStore()

  // Get toast utilities for user feedback
  const toasts = useToasts()

  // Business logic methods with API integration
  const addContact = useCallback(async (contactId: string): Promise<AIAgent | null> => {
    try {
      setLoading(true)
      clearError()

      // Check if contact already exists
      const existingContact = contacts.find(c => c.id === contactId)
      if (existingContact) {
        toasts.warning('联系人已存在', '该联系人已在您的联系人列表中')
        return existingContact
      }

      // Optimistic update - immediately show loading state
      toasts.loading('正在添加联系人', '请稍候...')

      // API call
      const response = await contactService.addContact(contactId)
      
      if (response.success && response.data) {
        // Update store with real data
        addContactToStore(response.data)
        
        toasts.success('添加成功', `${response.data.name} 已添加到联系人`)
        return response.data
      } else {
        throw new Error(response.error || '添加联系人失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '添加联系人失败'
      setError(errorMessage)
      toasts.error('添加失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [
    contacts,
    addContactToStore,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  const removeContact = useCallback(async (contactId: string): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const contactToRemove = contacts.find(c => c.id === contactId)
      if (!contactToRemove) {
        toasts.warning('联系人不存在')
        return
      }

      // Optimistic update - remove from UI immediately
      removeContactFromStore(contactId)
      toasts.loading('正在删除联系人', '请稍候...')

      // API call
      const response = await contactService.removeContact(contactId)

      if (response.success) {
        toasts.success('删除成功', `${contactToRemove.name} 已从联系人列表中删除`)
      } else {
        // Rollback optimistic update on failure
        addContactToStore(contactToRemove)
        throw new Error(response.error || '删除联系人失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '删除联系人失败'
      setError(errorMessage)
      toasts.error('删除失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [
    contacts,
    addContactToStore,
    removeContactFromStore,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  const updateContact = useCallback(async (
    contactId: string, 
    updates: Partial<AIAgent>
  ): Promise<AIAgent | null> => {
    try {
      setLoading(true)
      clearError()

      const originalContact = contacts.find(c => c.id === contactId)
      if (!originalContact) {
        toasts.warning('联系人不存在')
        return null
      }

      // Optimistic update
      const optimisticUpdate = {
        ...originalContact,
        ...updates,
        updatedAt: new Date().toISOString()
      }
      updateContactInStore(contactId, optimisticUpdate)

      toasts.loading('正在更新联系人', '请稍候...')

      // API call
      const response = await contactService.updateContact(contactId, updates)

      if (response.success && response.data) {
        // Update with real data from server
        updateContactInStore(contactId, response.data)
        toasts.success('更新成功', '联系人信息已更新')
        return response.data
      } else {
        // Rollback optimistic update
        updateContactInStore(contactId, originalContact)
        throw new Error(response.error || '更新联系人失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '更新联系人失败'
      setError(errorMessage)
      toasts.error('更新失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [
    contacts,
    updateContactInStore,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  const searchContacts = useCallback(async (query: string): Promise<AddContactSearchResult[]> => {
    try {
      clearError()

      if (query.trim().length === 0) {
        return []
      }

      // Use debounced API call
      const response = await contactService.searchContacts({
        query: query.trim(),
        limit: 20,
        excludeExisting: true, // Don't return contacts user already has
      })

      if (response.success) {
        return response.data || []
      } else {
        throw new Error(response.error || '搜索失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '搜索联系人失败'
      setError(errorMessage)
      toasts.error('搜索失败', errorMessage)
      return []
    }
  }, [setError, clearError, toasts])

  const sendContactRequest = useCallback(async (contactId: string, message: string): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      toasts.loading('发送联系人请求', '请稍候...')

      // API call
      const response = await contactService.sendContactRequest({
        toContactId: contactId,
        message: message.trim(),
      })

      if (response.success) {
        toasts.success('请求已发送', '联系人请求已成功发送')
      } else {
        throw new Error(response.error || '发送联系人请求失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '发送联系人请求失败'
      setError(errorMessage)
      toasts.error('发送失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError, clearError, toasts])

  const approveContactRequest = useCallback(async (requestId: string): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const request = pendingRequests.find(r => r.id === requestId)
      if (!request) {
        toasts.warning('请求不存在')
        return
      }

      // Optimistic update - remove from pending list
      removePendingRequest(requestId)
      toasts.loading('正在批准请求', '请稍候...')

      // API call
      const response = await contactService.approveContactRequest(requestId)

      if (response.success && response.data) {
        // Add approved contact to contacts list
        addContactToStore(response.data.contact)
        toasts.success('已批准', `${response.data.contact.name} 已添加到联系人`)
      } else {
        // Rollback - add request back to pending list
        addPendingRequest(request)
        throw new Error(response.error || '批准联系人请求失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '批准联系人请求失败'
      setError(errorMessage)
      toasts.error('批准失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [
    pendingRequests,
    addContactToStore,
    removePendingRequest,
    addPendingRequest,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  const rejectContactRequest = useCallback(async (requestId: string): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      const request = pendingRequests.find(r => r.id === requestId)
      if (!request) {
        toasts.warning('请求不存在')
        return
      }

      // Optimistic update
      removePendingRequest(requestId)
      toasts.loading('正在拒绝请求', '请稍候...')

      // API call
      const response = await contactService.rejectContactRequest(requestId)

      if (response.success) {
        toasts.info('已拒绝', '联系人请求已拒绝')
      } else {
        // Rollback
        addPendingRequest(request)
        throw new Error(response.error || '拒绝联系人请求失败')
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '拒绝联系人请求失败'
      setError(errorMessage)
      toasts.error('拒绝失败', errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }, [
    pendingRequests,
    removePendingRequest,
    addPendingRequest,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  const getPendingRequestsCount = useCallback(() => {
    return pendingRequests.length
  }, [pendingRequests.length])

  // Load initial data when hook is first used
  const loadContacts = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      clearError()

      // Load both contacts and pending requests in parallel
      const [contactsResponse, requestsResponse] = await Promise.all([
        contactService.getContacts(),
        contactService.getPendingRequests(),
      ])

      if (contactsResponse.success) {
        // Update store with contacts data
        contactsResponse.data?.forEach(contact => addContactToStore(contact))
      }

      if (requestsResponse.success) {
        // Update store with pending requests
        requestsResponse.data?.forEach(request => addPendingRequest(request))
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '加载联系人数据失败'
      setError(errorMessage)
      toasts.error('加载失败', errorMessage)
    } finally {
      setLoading(false)
    }
  }, [
    addContactToStore,
    addPendingRequest,
    setLoading,
    setError,
    clearError,
    toasts
  ])

  return {
    // State
    contacts,
    pendingRequests,
    loading: isLoading,
    error,

    // Actions
    addContact,
    removeContact,
    updateContact,
    searchContacts,
    sendContactRequest,
    approveContactRequest,
    rejectContactRequest,
    getPendingRequestsCount,
    loadContacts,

    // Additional utilities
    refreshContacts: loadContacts,
    clearError,
  }
}