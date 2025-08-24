/**
 * LangGraph Conversations Business Hook
 * 处理 LangGraph 增强型对话相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface LangGraphConversation {
  conversation_id: string
  title: string
  conversation_type: 'chat' | 'workflow' | 'collaboration'
  participants: ConversationParticipant[]
  workflow_state?: WorkflowState
  created_at: string
  updated_at: string
}

interface ConversationParticipant {
  id: string
  type: 'user' | 'agent'
  role: 'member' | 'moderator' | 'assistant'
  display_name: string
  is_active: boolean
}

interface WorkflowState {
  current_step: string
  execution_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  metadata?: Record<string, any>
}

interface LangGraphMessage {
  message_id: string
  conversation_id: string
  sender_id: string
  sender_type: 'user' | 'agent'
  content: string
  message_type: 'text' | 'system' | 'workflow'
  mentions?: string[]
  workflow_data?: any
  created_at: string
}

interface LangGraphMessageRequest {
  content: string
  message_type?: 'text' | 'system' | 'workflow'
  reply_to_id?: string
}

interface CreateConversationRequest {
  title: string
  conversation_type?: 'chat' | 'workflow' | 'collaboration'
  initial_agent_ids?: string[]
}

interface AddAgentRequest {
  agent_id: string
  role?: 'member' | 'moderator' | 'assistant'
}

export const useLangGraphConversations = () => {
  const createConversation = useCallback(async (
    request: CreateConversationRequest
  ): Promise<LangGraphConversation | null> => {
    try {
      const response = await fetch('/api/v1/langgraph/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          ...request,
          conversation_type: request.conversation_type || 'chat',
        }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Create LangGraph conversation failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "LangGraph conversation created",
        description: "Multi-agent conversation has been created successfully",
      })

      return data
    } catch (error: any) {
      console.error('Create LangGraph conversation failed:', error)
      toast({
        title: "Create conversation failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getConversation = useCallback(async (
    conversationId: string
  ): Promise<LangGraphConversation | null> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get LangGraph conversation failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get LangGraph conversation failed:', error)
      toast({
        title: "Get conversation failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const sendMessage = useCallback(async (
    conversationId: string,
    messageRequest: LangGraphMessageRequest
  ): Promise<LangGraphMessage | null> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          ...messageRequest,
          message_type: messageRequest.message_type || 'text',
        }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Send LangGraph message failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Message sent",
        description: "Your message has been processed by the multi-agent system",
      })

      return data
    } catch (error: any) {
      console.error('Send LangGraph message failed:', error)
      toast({
        title: "Send message failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getMessages = useCallback(async (
    conversationId: string,
    limit: number = 50,
    before?: string
  ): Promise<LangGraphMessage[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        ...(before && { before })
      })

      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/messages?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get LangGraph messages failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get LangGraph messages failed:', error)
      toast({
        title: "Get messages failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const addAgent = useCallback(async (
    conversationId: string,
    request: AddAgentRequest
  ): Promise<ConversationParticipant | null> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          ...request,
          role: request.role || 'member',
        }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Add agent to conversation failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Agent added",
        description: "AI agent has been added to the conversation",
      })

      return data
    } catch (error: any) {
      console.error('Add agent to conversation failed:', error)
      toast({
        title: "Add agent failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const removeAgent = useCallback(async (
    conversationId: string,
    agentId: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/agents/${agentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Remove agent from conversation failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Agent removed",
        description: "AI agent has been removed from the conversation",
      })

      return true
    } catch (error: any) {
      console.error('Remove agent from conversation failed:', error)
      toast({
        title: "Remove agent failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  return {
    createConversation,
    getConversation,
    sendMessage,
    getMessages,
    addAgent,
    removeAgent,
  }
}