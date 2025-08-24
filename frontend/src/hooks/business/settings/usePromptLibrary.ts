/**
 * Prompt Library Business Hook
 * 处理用户提示词库相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface PromptLibraryItem {
  id: string
  user_id: string
  title: string
  content: string
  category: string
  tags: string[]
  is_public: boolean
  is_favorite: boolean
  usage_count: number
  created_at: string
  updated_at: string
}

interface PromptLibraryCreate {
  title: string
  content: string
  category: string
  tags?: string[]
  is_public?: boolean
}

interface PromptLibraryUpdate {
  title?: string
  content?: string
  category?: string
  tags?: string[]
  is_public?: boolean
  is_favorite?: boolean
}

export const usePromptLibrary = () => {
  const getPromptLibrary = useCallback(async (
    limit: number = 20,
    category?: string,
    search?: string
  ): Promise<PromptLibraryItem[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        ...(category && { category }),
        ...(search && { search }),
      })

      const response = await fetch(`/api/v1/settings/prompts?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get prompt library failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get prompt library failed:', error)
      toast({
        title: "Get prompt library failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const createPrompt = useCallback(async (
    promptData: PromptLibraryCreate
  ): Promise<PromptLibraryItem | null> => {
    try {
      const response = await fetch('/api/v1/settings/prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(promptData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Create prompt failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Prompt created",
        description: "Your prompt has been added to the library",
      })

      return data
    } catch (error: any) {
      console.error('Create prompt failed:', error)
      toast({
        title: "Create prompt failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updatePrompt = useCallback(async (
    promptId: string,
    promptData: PromptLibraryUpdate
  ): Promise<PromptLibraryItem | null> => {
    try {
      const response = await fetch(`/api/v1/settings/prompts/${promptId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(promptData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update prompt failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Prompt updated",
        description: "Your prompt has been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update prompt failed:', error)
      toast({
        title: "Update prompt failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const deletePrompt = useCallback(async (promptId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/settings/prompts/${promptId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Delete prompt failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Prompt deleted",
        description: "Your prompt has been removed from the library",
      })

      return true
    } catch (error: any) {
      console.error('Delete prompt failed:', error)
      toast({
        title: "Delete prompt failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const getPromptById = useCallback(async (promptId: string): Promise<PromptLibraryItem | null> => {
    try {
      const response = await fetch(`/api/v1/settings/prompts/${promptId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get prompt failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get prompt failed:', error)
      toast({
        title: "Get prompt failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const toggleFavorite = useCallback(async (promptId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/settings/prompts/${promptId}/favorite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Toggle favorite failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Favorite updated",
        description: "Prompt favorite status updated",
      })

      return true
    } catch (error: any) {
      console.error('Toggle favorite failed:', error)
      toast({
        title: "Toggle favorite failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  return {
    getPromptLibrary,
    createPrompt,
    updatePrompt,
    deletePrompt,
    getPromptById,
    toggleFavorite,
  }
}