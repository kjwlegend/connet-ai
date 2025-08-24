/**
 * Agent 提及业务逻辑 Hook
 * 处理AI代理@提及相关的所有业务逻辑
 */

import { useState, useCallback, useMemo } from 'react'
import { useAgents } from '@/store/index'
import { useConversations } from '@/store/index'
import { useDebounce } from '@/hooks/ui/useDebounce'

interface Agent {
  id: string
  name: string
  displayName?: string
  avatar?: string
  description?: string
  status?: 'online' | 'offline' | 'busy'
  tags?: string[]
  capabilities?: string[]
  rating?: number
}

interface AgentMentionHook {
  // State
  isOpen: boolean
  query: string
  suggestions: Agent[]
  selectedIndex: number

  // Actions
  openMentionPopover: (query?: string) => void
  closeMentionPopover: () => void
  updateQuery: (query: string) => void
  selectSuggestion: (index: number) => void
  selectAgent: (agent: Agent) => void
  mentionAgent: (agent: Agent, context?: string) => Promise<void>

  // Keyboard navigation
  handleKeyDown: (event: React.KeyboardEvent) => boolean

  // Utilities
  formatMention: (agent: Agent) => string
  parseMentions: (text: string) => string[]
}

export function useAgentMention(chatroomId?: string): AgentMentionHook {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const { agents, searchAgents } = useAgents()
  const { activeConversationId } = useConversations()
  
  // 防抖查询
  const debouncedQuery = useDebounce(query, 200)

  // 获取当前聊天室ID
  const currentChatroom = chatroomId || activeConversationId

  // 模拟 agent mention 操作（待实现具体API）
  const mentionAgentAction = useCallback(async (
    roomId: string, 
    agentId: string, 
    context?: string
  ) => {
    // TODO: 实现具体的 mention API 调用
    console.log('Mentioning agent:', { roomId, agentId, context })
  }, [])

  // 筛选和搜索agents
  const suggestions = useMemo(() => {
    const availableAgents = agents || []
    
    if (!query.trim()) {
      return availableAgents.slice(0, 10) // 显示前10个可用agents
    }

    const normalizedQuery = query.toLowerCase().trim()

    return availableAgents
      .filter((agent: any) => {
        // 根据名称、显示名称、专业领域、标签进行筛选
        const matchesName = agent.name?.toLowerCase().includes(normalizedQuery)
        const matchesDisplayName = agent.displayName?.toLowerCase().includes(normalizedQuery)
        const matchesDescription = agent.description?.toLowerCase().includes(normalizedQuery)
        const matchesTags = agent.tags?.some((tag: string) => 
          tag.toLowerCase().includes(normalizedQuery)
        )

        return matchesName || matchesDisplayName || matchesDescription || matchesTags
      })
      .sort((a: any, b: any) => {
        // 优先显示名称完全匹配的
        const aNameMatch = a.name?.toLowerCase().startsWith(normalizedQuery)
        const bNameMatch = b.name?.toLowerCase().startsWith(normalizedQuery)

        if (aNameMatch && !bNameMatch) return -1
        if (!aNameMatch && bNameMatch) return 1

        // 然后按评分排序
        const aRating = a.rating || 0
        const bRating = b.rating || 0
        return bRating - aRating
      })
      .slice(0, 8) // 限制建议数量
  }, [query, agents])

  // 重置选择索引
  const resetSelectedIndex = useCallback(() => {
    setSelectedIndex(0)
  }, [])

  // 打开提及弹窗
  const openMentionPopover = useCallback((initialQuery = '') => {
    setIsOpen(true)
    setQuery(initialQuery)
    setSelectedIndex(0)
  }, [])

  // 关闭提及弹窗
  const closeMentionPopover = useCallback(() => {
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [])

  // 更新搜索查询
  const updateQuery = useCallback((newQuery: string) => {
    setQuery(newQuery)
    resetSelectedIndex()

    // 如果查询足够长，触发搜索
    if (newQuery.length >= 2) {
      searchAgents({ query: newQuery, limit: 10 })
    }
  }, [searchAgents, resetSelectedIndex])

  // 选择建议
  const selectSuggestion = useCallback((index: number) => {
    if (index >= 0 && index < suggestions.length) {
      setSelectedIndex(index)
    }
  }, [suggestions.length])

  // 选择并使用agent
  const selectAgent = useCallback((agent: Agent) => {
    closeMentionPopover()
    return agent
  }, [closeMentionPopover])

  // 在当前聊天室中提及agent
  const mentionAgent = useCallback(async (
    agent: Agent, 
    context?: string
  ) => {
    const roomId = currentChatroom

    if (!roomId) {
      console.warn('No chatroom selected for agent mention')
      return
    }

    try {
      await mentionAgentAction(roomId, agent.id, context)
      closeMentionPopover()
    } catch (error) {
      console.error('Failed to mention agent:', error)
      // 保持弹窗打开，让用户可以重试
    }
  }, [currentChatroom, mentionAgentAction, closeMentionPopover])

  // 键盘导航处理
  const handleKeyDown = useCallback((event: React.KeyboardEvent): boolean => {
    if (!isOpen) return false

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : 0
        )
        return true

      case 'ArrowUp':
        event.preventDefault()
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        )
        return true

      case 'Enter':
        event.preventDefault()
        if (suggestions[selectedIndex]) {
          selectAgent(suggestions[selectedIndex])
          return true
        }
        return false

      case 'Escape':
        event.preventDefault()
        closeMentionPopover()
        return true

      case 'Tab':
        // 允许Tab键选择当前建议
        if (suggestions[selectedIndex]) {
          event.preventDefault()
          selectAgent(suggestions[selectedIndex])
          return true
        }
        return false

      default:
        return false
    }
  }, [isOpen, suggestions, selectedIndex, selectAgent, closeMentionPopover])

  // 格式化agent提及
  const formatMention = useCallback((agent: Agent): string => {
    return `@${agent.name}`
  }, [])

  // 解析文本中的提及
  const parseMentions = useCallback((text: string): string[] => {
    const mentionRegex = /@(\w+)/g
    const mentions: string[] = []
    let match

    while ((match = mentionRegex.exec(text)) !== null) {
      mentions.push(match[1])
    }

    return mentions
  }, [])

  return {
    // State
    isOpen,
    query,
    suggestions,
    selectedIndex,

    // Actions
    openMentionPopover,
    closeMentionPopover,
    updateQuery,
    selectSuggestion,
    selectAgent,
    mentionAgent,

    // Keyboard navigation
    handleKeyDown,

    // Utilities
    formatMention,
    parseMentions,
  }
}