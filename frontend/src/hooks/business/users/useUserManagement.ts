/**
 * User Management Business Hook
 * 处理用户管理相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface UserItem {
  id: string
  email: string
  full_name: string
  username?: string
  is_active: boolean
  created_at: string
  updated_at: string
  last_login_at?: string
  bio?: string
  location?: string
  website?: string
  avatar_url?: string
}

interface PaginatedUserResponse {
  items: UserItem[]
  total: number
  page: number
  size: number
  pages: number
}

interface UserUpdateData {
  full_name?: string
  username?: string
  bio?: string
  location?: string
  website?: string
  avatar_url?: string
}

interface UserStats {
  total_posts: number
  total_comments: number
  total_likes_received: number
  total_followers: number
  total_following: number
  account_age_days: number
  last_activity_at: string
}

export const useUserManagement = () => {
  const listUsers = useCallback(async (
    page: number = 1,
    size: number = 20,
    search?: string
  ): Promise<PaginatedUserResponse | null> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
        ...(search && { search })
      })

      const response = await fetch(`/api/v1/users/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`List users failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('List users failed:', error)
      toast({
        title: "List users failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getUser = useCallback(async (userId: string): Promise<UserItem | null> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get user failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get user failed:', error)
      toast({
        title: "Get user failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updateUser = useCallback(async (
    userId: string,
    userData: UserUpdateData
  ): Promise<UserItem | null> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update user failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "User updated",
        description: "User information has been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update user failed:', error)
      toast({
        title: "Update user failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const deactivateUser = useCallback(async (
    userId: string,
    reason?: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}/deactivate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ reason: reason || 'Administrative action' }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Deactivate user failed: ${response.status} - ${error}`)
      }

      toast({
        title: "User deactivated",
        description: "User account has been deactivated",
        variant: "destructive",
      })

      return true
    } catch (error: any) {
      console.error('Deactivate user failed:', error)
      toast({
        title: "Deactivate user failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const reactivateUser = useCallback(async (userId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}/reactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Reactivate user failed: ${response.status} - ${error}`)
      }

      toast({
        title: "User reactivated",
        description: "User account has been reactivated",
      })

      return true
    } catch (error: any) {
      console.error('Reactivate user failed:', error)
      toast({
        title: "Reactivate user failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const deleteUser = useCallback(async (userId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Delete user failed: ${response.status} - ${error}`)
      }

      toast({
        title: "User deleted",
        description: "User account has been permanently deleted",
        variant: "destructive",
      })

      return true
    } catch (error: any) {
      console.error('Delete user failed:', error)
      toast({
        title: "Delete user failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const getUserStats = useCallback(async (userId: string): Promise<UserStats | null> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get user stats failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get user stats failed:', error)
      toast({
        title: "Get user stats failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getCurrentUser = useCallback(async (): Promise<UserItem | null> => {
    try {
      const response = await fetch('/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get current user failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get current user failed:', error)
      toast({
        title: "Get current user failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  return {
    listUsers,
    getUser,
    updateUser,
    deactivateUser,
    reactivateUser,
    deleteUser,
    getUserStats,
    getCurrentUser,
  }
}