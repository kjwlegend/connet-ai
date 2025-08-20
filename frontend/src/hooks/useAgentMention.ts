import { useState, useCallback, useMemo } from 'react'
// Note: These stores don't exist in current architecture, need to be implemented
// import { useAgentStore } from '@/store/slices/agentSlice'
// import { useChatStore } from '@/store/slices/chatSlice'
import type { Agent } from '@/types'

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

  // TODO: Implement agent store integration
  const availableAgents: Agent[] = [] // Placeholder
  const searchAgents = (query: string) => {} // Placeholder
  const mentionAgentAction = async (roomId: string, agentId: string, context?: string) => {} // Placeholder
  const currentChatroom = '' // Placeholder

  // Filter and search agents based on query
  const suggestions = useMemo(() => {
    if (!query.trim()) {
      return availableAgents.slice(0, 10) // Show first 10 available agents
    }

    const normalizedQuery = query.toLowerCase().trim()

    return availableAgents
      .filter(
        (agent) =>
          agent.name.toLowerCase().includes(normalizedQuery) ||
          (agent as any).displayName?.toLowerCase().includes(normalizedQuery) ||
          (agent as any).specialty?.toLowerCase().includes(normalizedQuery) ||
          (agent as any).tags?.some((tag: string) => tag.toLowerCase().includes(normalizedQuery))
      )
      .sort((a, b) => {
        // Prioritize exact name matches
        const aNameMatch = a.name.toLowerCase().startsWith(normalizedQuery)
        const bNameMatch = b.name.toLowerCase().startsWith(normalizedQuery)

        if (aNameMatch && !bNameMatch) return -1
        if (!aNameMatch && bNameMatch) return 1

        // Then by rating if available
        const aRating = (a as any).rating || 0
        const bRating = (b as any).rating || 0

        return bRating - aRating
      })
      .slice(0, 8) // Limit to 8 suggestions
  }, [query, availableAgents])

  // Reset selected index when suggestions change
  const resetSelectedIndex = useCallback(() => {
    setSelectedIndex(0)
  }, [])

  // Open mention popover
  const openMentionPopover = useCallback((initialQuery = '') => {
    setIsOpen(true)
    setQuery(initialQuery)
    setSelectedIndex(0)
  }, [])

  // Close mention popover
  const closeMentionPopover = useCallback(() => {
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [])

  // Update search query
  const updateQuery = useCallback(
    (newQuery: string) => {
      setQuery(newQuery)
      resetSelectedIndex()

      // Trigger search if query is substantial
      if (newQuery.length >= 2) {
        searchAgents(newQuery)
      }
    },
    [searchAgents, resetSelectedIndex]
  )

  // Select suggestion by index
  const selectSuggestion = useCallback(
    (index: number) => {
      if (index >= 0 && index < suggestions.length) {
        setSelectedIndex(index)
      }
    },
    [suggestions.length]
  )

  // Select and use an agent
  const selectAgent = useCallback(
    (agent: Agent) => {
      closeMentionPopover()
      return agent
    },
    [closeMentionPopover]
  )

  // Mention an agent in the current chatroom
  const mentionAgent = useCallback(
    async (agent: Agent, context?: string) => {
      const roomId = chatroomId || currentChatroom

      if (!roomId) {
        console.warn('No chatroom selected for agent mention')
        return
      }

      try {
        await mentionAgentAction(roomId, agent.id, context)
        closeMentionPopover()
      } catch (error) {
        console.error('Failed to mention agent:', error)
        // Keep popover open on error so user can retry
      }
    },
    [chatroomId, currentChatroom, mentionAgentAction, closeMentionPopover]
  )

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent): boolean => {
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
          // Allow tab to select current suggestion
          if (suggestions[selectedIndex]) {
            event.preventDefault()
            selectAgent(suggestions[selectedIndex])
            return true
          }
          return false

        default:
          return false
      }
    },
    [isOpen, suggestions, selectedIndex, selectAgent, closeMentionPopover]
  )

  // Format agent mention for display/insertion
  const formatMention = useCallback((agent: Agent): string => {
    return `@${agent.name}`
  }, [])

  // Parse mentions from text
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
