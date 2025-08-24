/**
 * LLM Settings Business Hook
 * 处理 LLM 设置相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface LLMSettings {
  id: string
  user_id: string
  preferred_provider: 'openai' | 'anthropic' | 'google' | 'azure'
  default_model: string
  default_max_tokens: number
  default_temperature: number
  system_prompt?: string
  enable_streaming: boolean
  enable_function_calling: boolean
  custom_endpoints?: Record<string, string>
  api_keys?: Record<string, string>
}

interface LLMSettingsUpdate {
  preferred_provider?: 'openai' | 'anthropic' | 'google' | 'azure'
  default_model?: string
  default_max_tokens?: number
  default_temperature?: number
  system_prompt?: string
  enable_streaming?: boolean
  enable_function_calling?: boolean
  custom_endpoints?: Record<string, string>
  api_keys?: Record<string, string>
}

export const useLLMSettings = () => {
  const getLLMSettings = useCallback(async (): Promise<LLMSettings | null> => {
    try {
      const response = await fetch('/api/v1/settings/llm', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get LLM settings failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get LLM settings failed:', error)
      toast({
        title: "Get LLM settings failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updateLLMSettings = useCallback(async (
    settings: LLMSettingsUpdate
  ): Promise<LLMSettings | null> => {
    try {
      const response = await fetch('/api/v1/settings/llm', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(settings),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update LLM settings failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "LLM settings updated",
        description: "Your LLM settings have been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update LLM settings failed:', error)
      toast({
        title: "Update LLM settings failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const resetLLMSettings = useCallback(async (): Promise<LLMSettings | null> => {
    try {
      const response = await fetch('/api/v1/settings/llm/reset', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Reset LLM settings failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "LLM settings reset",
        description: "Your LLM settings have been reset to default values",
      })

      return data
    } catch (error: any) {
      console.error('Reset LLM settings failed:', error)
      toast({
        title: "Reset LLM settings failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  return {
    getLLMSettings,
    updateLLMSettings,
    resetLLMSettings,
  }
}