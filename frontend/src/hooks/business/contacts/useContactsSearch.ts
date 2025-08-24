/**
 * 联系人搜索业务逻辑 Hook
 * 处理联系人搜索、推荐等相关业务逻辑
 */

import { useCallback, useState, useMemo } from 'react'
import { 
  ContactsService, 
  type ContactSearchParams, 
  type ContactSearchResponse 
} from '@/services/api'
import { useContacts } from '@/store/index'
import { useDebounce } from '@/hooks/ui/useDebounce'

interface UseContactsSearchReturn {
  // State
  searchResults: ContactSearchResponse[]
  isSearching: boolean
  searchQuery: string
  error: string | null
  hasSearched: boolean
  
  // Actions
  search: (params: ContactSearchParams) => Promise<void>
  searchByQuery: (query: string, type?: string) => Promise<void>
  clearSearchResults: () => void
  setSearchQuery: (query: string) => void
  clearError: () => void
  
  // Utils
  getSearchSuggestions: (query: string) => ContactSearchResponse[]
}

export const useContactsSearch = (): UseContactsSearchReturn => {
  const [searchQuery, setSearchQuery] = useState('')
  const [hasSearched, setHasSearched] = useState(false)
  
  const {
    searchResults,
    contactsUI,
    error,
    setSearchResults,
    clearSearchResults: clearSearchResultsAction,
    setSearching,
    setError,
    clearError: clearContactsError,
  } = useContacts()

  // 防抖搜索查询
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  const clearError = useCallback(() => {
    clearContactsError()
  }, [clearContactsError])

  const clearSearchResults = useCallback(() => {
    clearSearchResultsAction()
    setHasSearched(false)
    setSearchQuery('')
  }, [clearSearchResultsAction])

  const search = useCallback(async (
    params: ContactSearchParams
  ): Promise<void> => {
    try {
      setSearching(true)
      setError(null)
      setHasSearched(true)
      
      // 直接调用ContactsService
      const results = await ContactsService.searchContacts(params)
      
      // 更新本地状态
      setSearchResults(results)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '搜索失败'
      setError(errorMessage, 'search')
      console.error('Search failed:', error)
    } finally {
      setSearching(false)
    }
  }, [setSearching, setError, setSearchResults])

  const searchByQuery = useCallback(async (
    query: string,
    type?: string
  ): Promise<void> => {
    try {
      if (!query?.trim()) {
        clearSearchResults()
        return
      }

      const searchParams: ContactSearchParams = {
        query: query.trim(),
        limit: 20,
        ...(type && { contact_type: type as any }),
      }

      await search(searchParams)
    } catch (error) {
      console.error('Query search failed:', error)
    }
  }, [search, clearSearchResults])

  // 获取搜索建议
  const getSearchSuggestions = useCallback((query: string): ContactSearchResponse[] => {
    if (!query?.trim() || !searchResults.length) {
      return []
    }

    const normalizedQuery = query.toLowerCase().trim()
    
    return searchResults
      .filter(contact => 
        contact.name?.toLowerCase().includes(normalizedQuery) ||
        contact.description?.toLowerCase().includes(normalizedQuery) ||
        contact.tags?.some(tag => tag.toLowerCase().includes(normalizedQuery))
      )
      .slice(0, 5) // 限制建议数量
  }, [searchResults])

  // 自动搜索（防抖）
  const autoSearchResults = useMemo(() => {
    if (!debouncedSearchQuery.trim()) {
      return []
    }
    return getSearchSuggestions(debouncedSearchQuery)
  }, [debouncedSearchQuery, getSearchSuggestions])

  // 当防抖查询变化时自动搜索
  useState(() => {
    if (debouncedSearchQuery.trim() && debouncedSearchQuery !== searchQuery) {
      searchByQuery(debouncedSearchQuery)
    }
  })

  return {
    // State
    searchResults,
    isSearching: contactsUI.isSearching,
    searchQuery,
    error: error.current,
    hasSearched,
    
    // Actions
    search,
    searchByQuery,
    clearSearchResults,
    setSearchQuery,
    clearError,
    
    // Utils
    getSearchSuggestions,
  }
}