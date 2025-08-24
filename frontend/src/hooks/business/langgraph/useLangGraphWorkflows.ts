/**
 * LangGraph Workflows Business Hook
 * 处理 LangGraph 工作流相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface WorkflowExecution {
  execution_id: string
  conversation_id: string
  workflow_type: 'chat' | 'task_planning' | 'collaboration' | 'research'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  current_step: string
  steps_completed: number
  total_steps: number
  progress_percentage: number
  start_time: string
  end_time?: string
  metadata?: Record<string, any>
  error_message?: string
}

interface WorkflowTriggerRequest {
  workflow_type: 'chat' | 'task_planning' | 'collaboration' | 'research'
  trigger_context?: {
    user_message?: string
    mentioned_agents?: string[]
    task_description?: string
    parameters?: Record<string, any>
  }
}

interface WorkflowStep {
  step_id: string
  step_name: string
  step_type: 'agent_action' | 'user_input' | 'system_process' | 'decision_point'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  assigned_agent_id?: string
  input_data?: any
  output_data?: any
  execution_time?: number
  error_message?: string
  created_at: string
  completed_at?: string
}

interface WorkflowStatus {
  execution_id: string
  status: string
  current_step: string
  progress: number
  steps: WorkflowStep[]
  estimated_time_remaining?: number
  metadata?: Record<string, any>
}

export const useLangGraphWorkflows = () => {
  const triggerWorkflow = useCallback(async (
    conversationId: string,
    request: WorkflowTriggerRequest
  ): Promise<WorkflowExecution | null> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Trigger workflow failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Workflow triggered",
        description: `Multi-agent ${request.workflow_type} workflow has been started`,
      })

      return data
    } catch (error: any) {
      console.error('Trigger workflow failed:', error)
      toast({
        title: "Trigger workflow failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getWorkflowStatus = useCallback(async (
    conversationId: string,
    executionId?: string
  ): Promise<WorkflowStatus | null> => {
    try {
      const url = executionId 
        ? `/api/v1/langgraph/conversations/${conversationId}/workflow/${executionId}/status`
        : `/api/v1/langgraph/conversations/${conversationId}/workflow/status`

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get workflow status failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get workflow status failed:', error)
      toast({
        title: "Get workflow status failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const pauseWorkflow = useCallback(async (
    conversationId: string,
    executionId: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/${executionId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Pause workflow failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Workflow paused",
        description: "The workflow execution has been paused",
      })

      return true
    } catch (error: any) {
      console.error('Pause workflow failed:', error)
      toast({
        title: "Pause workflow failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const resumeWorkflow = useCallback(async (
    conversationId: string,
    executionId: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/${executionId}/resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Resume workflow failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Workflow resumed",
        description: "The workflow execution has been resumed",
      })

      return true
    } catch (error: any) {
      console.error('Resume workflow failed:', error)
      toast({
        title: "Resume workflow failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const cancelWorkflow = useCallback(async (
    conversationId: string,
    executionId: string,
    reason?: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/${executionId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ reason: reason || 'User requested cancellation' }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Cancel workflow failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Workflow cancelled",
        description: "The workflow execution has been cancelled",
        variant: "destructive",
      })

      return true
    } catch (error: any) {
      console.error('Cancel workflow failed:', error)
      toast({
        title: "Cancel workflow failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const getWorkflowHistory = useCallback(async (
    conversationId: string,
    limit: number = 10
  ): Promise<WorkflowExecution[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
      })

      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/history?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get workflow history failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get workflow history failed:', error)
      toast({
        title: "Get workflow history failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const getWorkflowLogs = useCallback(async (
    conversationId: string,
    executionId: string,
    level: 'debug' | 'info' | 'warning' | 'error' = 'info'
  ): Promise<any[]> => {
    try {
      const params = new URLSearchParams({
        level,
      })

      const response = await fetch(`/api/v1/langgraph/conversations/${conversationId}/workflow/${executionId}/logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get workflow logs failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get workflow logs failed:', error)
      toast({
        title: "Get workflow logs failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  return {
    triggerWorkflow,
    getWorkflowStatus,
    pauseWorkflow,
    resumeWorkflow,
    cancelWorkflow,
    getWorkflowHistory,
    getWorkflowLogs,
  }
}