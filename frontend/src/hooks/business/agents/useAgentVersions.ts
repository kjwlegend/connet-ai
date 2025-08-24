/**
 * Agent版本管理业务逻辑 Hook
 * 处理AI代理版本相关的业务逻辑
 */

import { useCallback } from 'react'
import { useAgents } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseAgentVersionsReturn {
  // State
  agentVersions: any[]
  isLoading: boolean
  error: string | null
  
  // Actions
  getAgentVersions: (agentId: string) => Promise<any[] | null>
  rollbackAgent: (agentId: string, version: string) => Promise<boolean>
  clearError: () => void
}

export const useAgentVersions = (): UseAgentVersionsReturn => {
  const {
    agentVersions,
    ui,
    error,
    getAgentVersions: getAgentVersionsAction,
    rollbackAgent: rollbackAgentAction,
    clearError: clearAgentsError,
  } = useAgents()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearAgentsError()
  }, [clearAgentsError])

  const getAgentVersions = useCallback(async (
    agentId: string
  ): Promise<any[] | null> => {
    try {
      // 输入验证
      if (!agentId?.trim()) {
        toasts.error('错误', 'Agent ID不能为空')
        return null
      }

      const versions = await getAgentVersionsAction(agentId.trim())
      return versions
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '获取版本列表失败'
      
      toasts.error('获取失败', errorMessage)
      return null
    }
  }, [getAgentVersionsAction, toasts])

  const rollbackAgent = useCallback(async (
    agentId: string,
    version: string
  ): Promise<boolean> => {
    try {
      // 输入验证
      if (!agentId?.trim()) {
        toasts.error('错误', 'Agent ID不能为空')
        return false
      }

      if (!version?.trim()) {
        toasts.error('错误', '版本号不能为空')
        return false
      }

      // 确认回滚
      const confirmed = window.confirm(
        `确定要将AI代理回滚到版本 ${version} 吗？此操作将覆盖当前版本。`
      )
      if (!confirmed) {
        return false
      }

      await rollbackAgentAction(agentId.trim(), version.trim())
      toasts.success('成功', `AI代理已回滚到版本 ${version}`)
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '版本回滚失败'
      
      toasts.error('回滚失败', errorMessage)
      return false
    }
  }, [rollbackAgentAction, toasts])

  return {
    // State
    agentVersions,
    isLoading: ui.isLoading,
    error: error.current,
    
    // Actions
    getAgentVersions,
    rollbackAgent,
    clearError,
  }
}