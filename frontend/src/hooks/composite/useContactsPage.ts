/**
 * 联系人页面组合 Hook
 * 整合联系人页面所需的所有业务逻辑
 */

import { 
  useContactsQuery, 
  useContactsMutation, 
  useContactsSearch,
  useContactsKnowledge,
  useContactsTools 
} from '@/hooks/business/contacts'

interface UseContactsPageReturn {
  // Query state and actions
  query: {
    contacts: any[]
    isLoading: boolean
    error: string | null
    pagination: any
    filters: any
    loadContacts: (params?: any, append?: boolean) => Promise<void>
    refreshContacts: () => Promise<void>
    loadMoreContacts: () => Promise<void>
    setFilters: (filters: any) => void
    clearFilters: () => void
    clearError: () => void
  }
  
  // Mutation state and actions
  mutation: {
    isCreating: boolean
    isUpdating: boolean
    isDeleting: boolean
    error: string | null
    createContact: (data: any) => Promise<any>
    updateContact: (contactId: string, contactType: any, data: any) => Promise<any>
    deleteContact: (contactId: string, contactType: any) => Promise<boolean>
    toggleFavorite: (contactId: string, contactType: any) => Promise<boolean>
    clearError: () => void
  }
  
  // Search state and actions
  search: {
    searchResults: any[]
    isSearching: boolean
    searchQuery: string
    error: string | null
    hasSearched: boolean
    search: (params: any) => Promise<void>
    searchByQuery: (query: string, type?: string) => Promise<void>
    clearSearchResults: () => void
    setSearchQuery: (query: string) => void
    clearError: () => void
  }
  
  // Knowledge state and actions
  knowledge: {
    contactKnowledge: any[]
    isLoading: boolean
    error: string | null
    loadContactKnowledge: (contactId: string, contactType: any) => Promise<void>
    addKnowledgeToContact: (contactId: string, contactType: any, knowledgeBaseId: string, alias?: string) => Promise<boolean>
    removeKnowledgeFromContact: (contactId: string, contactType: any, knowledgeBaseId: string) => Promise<boolean>
    clearError: () => void
  }
  
  // Tools state and actions
  tools: {
    contactTools: any[]
    isLoading: boolean
    error: string | null
    loadContactTools: (contactId: string, contactType: any) => Promise<void>
    addToolToContact: (contactId: string, contactType: any, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<boolean>
    removeToolFromContact: (contactId: string, contactType: any, toolId: string) => Promise<boolean>
    updateContactToolConfig: (contactId: string, contactType: any, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<boolean>
    clearError: () => void
  }
  
  // Unified actions
  clearAllErrors: () => void
  refreshAll: () => Promise<void>
}

export const useContactsPage = (): UseContactsPageReturn => {
  // 使用各个业务 hooks
  const queryHook = useContactsQuery()
  const mutationHook = useContactsMutation()
  const searchHook = useContactsSearch()
  const knowledgeHook = useContactsKnowledge()
  const toolsHook = useContactsTools()

  // 统一清除所有错误
  const clearAllErrors = () => {
    queryHook.clearError()
    mutationHook.clearError()
    searchHook.clearError()
    knowledgeHook.clearError()
    toolsHook.clearError()
  }

  // 刷新所有数据
  const refreshAll = async () => {
    await Promise.all([
      queryHook.refreshContacts(),
      // 可以根据需要添加其他数据的刷新
    ])
  }

  return {
    // Query
    query: {
      contacts: queryHook.contacts,
      isLoading: queryHook.isLoading,
      error: queryHook.error,
      pagination: queryHook.pagination,
      filters: queryHook.filters,
      loadContacts: queryHook.loadContacts,
      refreshContacts: queryHook.refreshContacts,
      loadMoreContacts: queryHook.loadMoreContacts,
      setFilters: queryHook.setFilters,
      clearFilters: queryHook.clearFilters,
      clearError: queryHook.clearError,
    },
    
    // Mutation
    mutation: {
      isCreating: mutationHook.isCreating,
      isUpdating: mutationHook.isUpdating,
      isDeleting: mutationHook.isDeleting,
      error: mutationHook.error,
      createContact: mutationHook.createContact,
      updateContact: mutationHook.updateContact,
      deleteContact: mutationHook.deleteContact,
      toggleFavorite: mutationHook.toggleFavorite,
      clearError: mutationHook.clearError,
    },
    
    // Search
    search: {
      searchResults: searchHook.searchResults,
      isSearching: searchHook.isSearching,
      searchQuery: searchHook.searchQuery,
      error: searchHook.error,
      hasSearched: searchHook.hasSearched,
      search: searchHook.search,
      searchByQuery: searchHook.searchByQuery,
      clearSearchResults: searchHook.clearSearchResults,
      setSearchQuery: searchHook.setSearchQuery,
      clearError: searchHook.clearError,
    },
    
    // Knowledge
    knowledge: {
      contactKnowledge: knowledgeHook.contactKnowledge,
      isLoading: knowledgeHook.isLoading,
      error: knowledgeHook.error,
      loadContactKnowledge: knowledgeHook.loadContactKnowledge,
      addKnowledgeToContact: knowledgeHook.addKnowledgeToContact,
      removeKnowledgeFromContact: knowledgeHook.removeKnowledgeFromContact,
      clearError: knowledgeHook.clearError,
    },
    
    // Tools
    tools: {
      contactTools: toolsHook.contactTools,
      isLoading: toolsHook.isLoading,
      error: toolsHook.error,
      loadContactTools: toolsHook.loadContactTools,
      addToolToContact: toolsHook.addToolToContact,
      removeToolFromContact: toolsHook.removeToolFromContact,
      updateContactToolConfig: toolsHook.updateContactToolConfig,
      clearError: toolsHook.clearError,
    },
    
    // Unified actions
    clearAllErrors,
    refreshAll,
  }
}