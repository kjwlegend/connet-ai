/**
 * 聊天对话业务逻辑 Hook
 * 处理聊天对话管理相关的业务逻辑
 */

import { useCallback } from 'react'
import { useConversations } from '@/store/index'
import { useToasts } from '@/store/index'

interface UseChatConversationsReturn {
  // State
  conversations: any[]
  activeConversationId: string | null
  isLoading: boolean
  error: string | null
  
  // Actions
  loadConversations: () => Promise<void>
  createConversation: (title?: string) => Promise<any | null>
  setActiveConversation: (conversationId: string) => void
  pinConversation: (conversationId: string) => Promise<boolean>
  archiveConversation: (conversationId: string) => Promise<boolean>
  exportConversation: (conversationId: string) => Promise<boolean>
  clearError: () => void
}

export const useChatConversations = (): UseChatConversationsReturn => {
  const {
    conversations,
    activeConversationId,
    isLoading,
    conversationError,
    loadConversations: loadConversationsAction,
    createConversation: createConversationAction,
    setActiveConversation: setActiveConversationAction,
    pinConversation: pinConversationAction,
    archiveConversation: archiveConversationAction,
    exportConversation: exportConversationAction,
    clearConversationError,
  } = useConversations()
  
  const toasts = useToasts()

  const clearError = useCallback(() => {
    clearConversationError()
  }, [clearConversationError])

  const loadConversations = useCallback(async (): Promise<void> => {
    try {
      await loadConversationsAction()
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '加载对话列表失败'
      
      toasts.error('加载失败', errorMessage)
    }
  }, [loadConversationsAction, toasts])

  const createConversation = useCallback(async (
    title?: string
  ): Promise<any | null> => {
    try {
      const conversation = await createConversationAction(title?.trim())
      
      if (conversation) {
        toasts.success('成功', '新对话创建成功')
        // 自动设置为活跃对话
        setActiveConversationAction(conversation.id)
      }

      return conversation
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '创建对话失败'
      
      toasts.error('创建失败', errorMessage)
      return null
    }
  }, [createConversationAction, setActiveConversationAction, toasts])

  const setActiveConversation = useCallback((conversationId: string) => {
    if (!conversationId?.trim()) {
      console.warn('Conversation ID cannot be empty')
      return
    }

    setActiveConversationAction(conversationId.trim())
  }, [setActiveConversationAction])

  const pinConversation = useCallback(async (
    conversationId: string
  ): Promise<boolean> => {
    try {
      if (!conversationId?.trim()) {
        toasts.error('错误', '对话ID不能为空')
        return false
      }

      const success = await pinConversationAction(conversationId.trim())
      
      if (success) {
        toasts.success('成功', '对话置顶状态已更新')
      }
      
      return success
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '置顶操作失败'
      
      toasts.error('操作失败', errorMessage)
      return false
    }
  }, [pinConversationAction, toasts])

  const archiveConversation = useCallback(async (
    conversationId: string
  ): Promise<boolean> => {
    try {
      if (!conversationId?.trim()) {
        toasts.error('错误', '对话ID不能为空')
        return false
      }

      // 确认归档
      const confirmed = window.confirm('确定要归档这个对话吗？')
      if (!confirmed) {
        return false
      }

      const success = await archiveConversationAction(conversationId.trim())
      
      if (success) {
        toasts.success('成功', '对话已归档')
        
        // 如果归档的是当前活跃对话，清除活跃状态
        if (conversationId === activeConversationId) {
          setActiveConversationAction('')
        }
      }
      
      return success
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '归档操作失败'
      
      toasts.error('归档失败', errorMessage)
      return false
    }
  }, [archiveConversationAction, activeConversationId, setActiveConversationAction, toasts])

  const exportConversation = useCallback(async (
    conversationId: string
  ): Promise<boolean> => {
    try {
      if (!conversationId?.trim()) {
        toasts.error('错误', '对话ID不能为空')
        return false
      }

      const success = await exportConversationAction(conversationId.trim())
      
      if (success) {
        toasts.success('成功', '对话导出成功')
      }
      
      return success
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '导出操作失败'
      
      toasts.error('导出失败', errorMessage)
      return false
    }
  }, [exportConversationAction, toasts])

  return {
    // State
    conversations,
    activeConversationId,
    isLoading,
    error: conversationError,
    
    // Actions
    loadConversations,
    createConversation,
    setActiveConversation,
    pinConversation,
    archiveConversation,
    exportConversation,
    clearError,
  }
}