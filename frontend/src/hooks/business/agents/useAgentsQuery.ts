/**
 * AI代理查询业务逻辑 Hook
 * 处理AI代理列表获取、分页、筛选等查询相关业务逻辑
 */

import { useCallback, useEffect } from 'react'
import { AgentsService } from '@/services/api'
import { useAgents } from '@/store/index'

interface UseAgentsQueryReturn {
  // State
  agents: any[]
  currentAgent: any | null
  isLoading: boolean
  error: string | null
  pagination: {
    skip: number
    limit: number
    hasMore: boolean
    total: number
  }
  filters: any
  
  // Actions
  listAgents: (params?: any, append?: boolean) => Promise<void>
  getAgent: (agentId: string) => Promise<any | null>
  searchAgents: (query: string) => Promise<void>
  refreshAgents: () => Promise<void>
  loadMoreAgents: () => Promise<void>
  setFilters: (filters: any) => void
  clearFilters: () => void
  clearError: () => void
}

export const useAgentsQuery = (): UseAgentsQueryReturn => {
  const {
    agents,
    currentAgent,
    pagination,
    filters,
    ui,
    error,
    setAgents,
    setCurrentAgent,
    setLoading,
    setError,
    setAgentsFilters,
    clearError: clearAgentsError,
  } = useAgents()

  const clearError = useCallback(() => {
    clearAgentsError()
  }, [clearAgentsError])

  const listAgents = useCallback(async (
    params: any = {},
    append = false
  ): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      
      // 直接调用AgentsService
      const result = await AgentsService.listAgents(params)
      
      // 更新本地状态
      if (append && result.agents) {
        setAgents([...agents, ...result.agents])
      } else if (result.agents) {
        setAgents(result.agents)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '加载代理失败'
      setError(errorMessage, 'listAgents')
      console.error('Failed to load agents:', error)
    } finally {
      setLoading(false)
    }
  }, [agents, setAgents, setLoading, setError])

  const refreshAgents = useCallback(async (): Promise<void> => {
    try {
      await listAgents({ skip: 0 })
    } catch (error) {
      console.error('Failed to refresh agents:', error)
    }
  }, [listAgents])

  const loadMoreAgents = useCallback(async (): Promise<void> => {
    if (!pagination.hasMore || ui.isLoading) return
    
    try {
      await listAgents({ ...filters, skip: pagination.skip }, true)
    } catch (error) {
      console.error('Failed to load more agents:', error)
    }
  }, [listAgents, filters, pagination.hasMore, pagination.skip, ui.isLoading])

  const setFilters = useCallback((newFilters: any) => {
    setAgentsFilters(newFilters)
    // 应用新筛选条件后重新加载
    listAgents({ ...newFilters, skip: 0 })
  }, [setAgentsFilters, listAgents])

  const clearFilters = useCallback(() => {
    setAgentsFilters({})
    // 清除筛选条件后重新加载
    listAgents({ skip: 0 })
  }, [setAgentsFilters, listAgents])

  const getAgent = useCallback(async (agentId: string): Promise<any | null> => {
    try {
      setError(null)
      
      if (!agentId?.trim()) {
        return null
      }

      // 直接调用AgentsService
      const agent = await AgentsService.getAgent(agentId.trim())
      
      // 更新当前代理
      if (agent) {
        setCurrentAgent(agent)
      }
      
      return agent
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取代理失败'
      setError(errorMessage, 'getAgent')
      console.error('Failed to get agent:', error)
      return null
    }
  }, [setCurrentAgent, setError])

  const searchAgents = useCallback(async (query: string): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      
      // 直接调用AgentsService
      const result = await AgentsService.searchAgents(query)
      
      // 更新本地状态
      if (result) {
        setAgents(result)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '搜索代理失败'
      setError(errorMessage, 'searchAgents')
      console.error('Failed to search agents:', error)
    } finally {
      setLoading(false)
    }
  }, [setAgents, setLoading, setError])

  // 自动加载初始数据
  useEffect(() => {
    if (agents.length === 0 && !ui.isLoading) {
      listAgents()
    }
  }, []) // 只在组件挂载时执行

  return {
    // State
    agents,
    currentAgent,
    isLoading: ui.isLoading,
    error: error.current,
    pagination,
    filters,
    
    // Actions
    listAgents,
    getAgent,
    searchAgents,
    refreshAgents,
    loadMoreAgents,
    setFilters,
    clearFilters,
    clearError,
  }
}