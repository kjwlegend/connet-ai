/**
 * AI代理变更业务逻辑 Hook
 * 处理AI代理的创建、更新、删除等变更操作
 */

import { useCallback } from 'react'
import { AgentsService } from '@/services/api'
import { useAgents } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseAgentsMutationReturn {
  // State
  isCreating: boolean
  isUpdating: boolean
  isDeleting: boolean
  isDeploying: boolean
  error: string | null
  
  // Actions
  createAgent: (data: any) => Promise<any | null>
  updateAgent: (agentId: string, data: any) => Promise<any | null>
  deleteAgent: (agentId: string) => Promise<boolean>
  deployAgent: (agentId: string) => Promise<boolean>
  clearError: () => void
}

export const useAgentsMutation = (): UseAgentsMutationReturn => {
  const {
    ui,
    error,
    addAgent,
    updateAgentInList,
    setCurrentAgent,
    setLoading,
    setError,
    clearError: clearAgentsError,
  } = useAgents()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearAgentsError()
  }, [clearAgentsError])

  const createAgent = useCallback(async (data: any): Promise<any | null> => {
    try {
      // 输入验证
      if (!data?.name?.trim()) {
        toasts.error('错误', 'Agent名称不能为空')
        return null
      }

      if (!data?.description?.trim()) {
        toasts.error('错误', 'Agent描述不能为空')
        return null
      }

      // 直接调用AgentsService
      const agent = await AgentsService.createAgent({
        ...data,
        name: data.name.trim(),
        description: data.description.trim(),
      })

      // 更新本地状态
      if (agent) {
        addAgent(agent)
        toasts.success('成功', 'AI代理创建成功')
      }

      return agent
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '创建AI代理失败'
      
      toasts.error('创建失败', errorMessage)
      return null
    }
  }, [addAgent, toasts])

  const updateAgent = useCallback(async (
    agentId: string,
    data: any
  ): Promise<any | null> => {
    try {
      // 输入验证
      if (!agentId?.trim()) {
        toasts.error('错误', 'Agent ID不能为空')
        return null
      }

      if (data?.name !== undefined && !data.name?.trim()) {
        toasts.error('错误', 'Agent名称不能为空')
        return null
      }

      const cleanData = { ...data }
      if (cleanData.name) {
        cleanData.name = cleanData.name.trim()
      }
      if (cleanData.description) {
        cleanData.description = cleanData.description.trim()
      }

      // 直接调用AgentsService
      const agent = await AgentsService.updateAgent(agentId.trim(), cleanData)

      // 更新本地状态
      if (agent) {
        updateAgentInList(agent)
        setCurrentAgent(agent)
        toasts.success('成功', 'AI代理更新成功')
      }

      return agent
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '更新AI代理失败'
      
      toasts.error('更新失败', errorMessage)
      return null
    }
  }, [updateAgentInList, setCurrentAgent, toasts])

  const deleteAgent = useCallback(async (agentId: string): Promise<boolean> => {
    try {
      // 输入验证
      if (!agentId?.trim()) {
        toasts.error('错误', 'Agent ID不能为空')
        return false
      }

      // 确认删除
      const confirmed = window.confirm('确定要删除这个AI代理吗？此操作不可撤销。')
      if (!confirmed) {
        return false
      }

      // 直接调用AgentsService
      await AgentsService.deleteAgent(agentId.trim())
      
      // 更新本地状态 - 清除当前代理如果是被删除的
      setCurrentAgent(null)
      
      toasts.success('成功', 'AI代理删除成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '删除AI代理失败'
      
      toasts.error('删除失败', errorMessage)
      return false
    }
  }, [setCurrentAgent, toasts])

  const deployAgent = useCallback(async (agentId: string): Promise<boolean> => {
    try {
      // 输入验证
      if (!agentId?.trim()) {
        toasts.error('错误', 'Agent ID不能为空')
        return false
      }

      // 确认部署
      const confirmed = window.confirm('确定要部署这个AI代理吗？')
      if (!confirmed) {
        return false
      }

      // 直接调用AgentsService
      const result = await AgentsService.deployAgent(agentId.trim())
      
      // 如果有更新的代理信息，更新本地状态
      if (result && result.agent) {
        setCurrentAgent(result.agent)
      }
      
      toasts.success('成功', 'AI代理部署成功')
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '部署AI代理失败'
      
      toasts.error('部署失败', errorMessage)
      return false
    }
  }, [setCurrentAgent, toasts])

  return {
    // State
    isCreating: ui.isCreating,
    isUpdating: ui.isUpdating,
    isDeleting: ui.isDeleting,
    isDeploying: ui.isDeploying,
    error: error.current,
    
    // Actions
    createAgent,
    updateAgent,
    deleteAgent,
    deployAgent,
    clearError,
  }
}