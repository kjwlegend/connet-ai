/**
 * AI Chat Business Hook
 * 处理 AI 聊天相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface ChatRequest {
  agent_id: string
  message: string
  conversation_id?: string
  max_tokens?: number
  temperature?: number
  stream?: boolean
}

interface ChatResponse {
  message_id: string
  conversation_id: string
  response: string
  agent_id: string
  tokens_used?: number
  processing_time?: number
}

interface MemoryEntry {
  id: string
  conversation_id: string
  content: string
  memory_type: string
  metadata?: Record<string, any>
  created_at: string
}

interface ConversationSummary {
  conversation_id: string
  summary: string
  key_points: string[]
  participants: string[]
  message_count: number
  created_at: string
}

export const useAIChat = () => {
  const chatWithAgent = useCallback(async (request: ChatRequest): Promise<ChatResponse | null> => {
    try {
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Chat failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Chat successful",
        description: "AI agent responded successfully",
      })

      return data
    } catch (error: any) {
      console.error('Chat with AI agent failed:', error)
      toast({
        title: "Chat failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  return {
    chatWithAgent,
  }
}

export const useAIChatMemory = () => {
  const createMemory = useCallback(async (
    conversationId: string,
    content: string,
    memoryType: string = 'context',
    metadata?: Record<string, any>
  ): Promise<MemoryEntry | null> => {
    try {
      const response = await fetch('/api/v1/chat/memory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          content,
          memory_type: memoryType,
          metadata,
        }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Create memory failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Memory created",
        description: "Memory entry created successfully",
      })

      return data
    } catch (error: any) {
      console.error('Create memory failed:', error)
      toast({
        title: "Create memory failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getMemory = useCallback(async (
    conversationId: string,
    limit: number = 10
  ): Promise<MemoryEntry[]> => {
    try {
      const params = new URLSearchParams({
        conversation_id: conversationId,
        limit: limit.toString(),
      })

      const response = await fetch(`/api/v1/chat/memory?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get memory failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get memory failed:', error)
      toast({
        title: "Get memory failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const getConversationSummary = useCallback(async (
    conversationId: string
  ): Promise<ConversationSummary | null> => {
    try {
      const params = new URLSearchParams({
        conversation_id: conversationId,
      })

      const response = await fetch(`/api/v1/chat/summary?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get summary failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get conversation summary failed:', error)
      toast({
        title: "Get summary failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  return {
    createMemory,
    getMemory,
    getConversationSummary,
  }
}