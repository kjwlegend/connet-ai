/**
 * Timeline Posts Business Hook
 * 处理时间轴帖子相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface TimelinePost {
  id: string
  author_id: string
  author_type: 'user' | 'agent'
  content: string
  post_type: 'text' | 'image' | 'video' | 'link' | 'poll'
  visibility: 'public' | 'friends' | 'private'
  tags: string[]
  attachment_url?: string
  like_count: number
  comment_count: number
  is_liked: boolean
  created_at: string
  updated_at: string
}

interface TimelinePostCreate {
  content: string
  post_type?: 'text' | 'image' | 'video' | 'link' | 'poll'
  visibility?: 'public' | 'friends' | 'private'
  tags?: string[]
  attachment_url?: string
}

interface TimelinePostUpdate {
  content?: string
  post_type?: 'text' | 'image' | 'video' | 'link' | 'poll'
  visibility?: 'public' | 'friends' | 'private'
  tags?: string[]
  attachment_url?: string
}

export const useTimelinePosts = () => {
  const getTimelinePosts = useCallback(async (
    category: 'friends_circle' | 'public_square' | 'my_circle' | 'favorites' = 'friends_circle',
    skip: number = 0,
    limit: number = 20,
    authorType?: 'user' | 'agent' | 'all'
  ): Promise<TimelinePost[]> => {
    try {
      const params = new URLSearchParams({
        category,
        skip: skip.toString(),
        limit: limit.toString(),
        ...(authorType && authorType !== 'all' && { author_type: authorType })
      })

      const response = await fetch(`/api/v1/timeline/posts?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get timeline posts failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get timeline posts failed:', error)
      toast({
        title: "Get timeline posts failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const createPost = useCallback(async (
    postData: TimelinePostCreate
  ): Promise<TimelinePost | null> => {
    try {
      const response = await fetch('/api/v1/timeline/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          ...postData,
          post_type: postData.post_type || 'text',
          visibility: postData.visibility || 'public',
          tags: postData.tags || [],
        }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Create post failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Post created",
        description: "Your timeline post has been created successfully",
      })

      return data
    } catch (error: any) {
      console.error('Create post failed:', error)
      toast({
        title: "Create post failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getPost = useCallback(async (postId: string): Promise<TimelinePost | null> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get post failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get post failed:', error)
      toast({
        title: "Get post failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updatePost = useCallback(async (
    postId: string,
    postData: TimelinePostUpdate
  ): Promise<TimelinePost | null> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(postData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update post failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Post updated",
        description: "Your timeline post has been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update post failed:', error)
      toast({
        title: "Update post failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const deletePost = useCallback(async (postId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Delete post failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Post deleted",
        description: "Your timeline post has been deleted successfully",
      })

      return true
    } catch (error: any) {
      console.error('Delete post failed:', error)
      toast({
        title: "Delete post failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  return {
    getTimelinePosts,
    createPost,
    getPost,
    updatePost,
    deletePost,
  }
}