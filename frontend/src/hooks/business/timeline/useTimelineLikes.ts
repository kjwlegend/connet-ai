/**
 * Timeline Likes Business Hook
 * 处理时间轴点赞相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface TimelineLike {
  id: string
  post_id: string
  user_id: string
  created_at: string
}

export const useTimelineLikes = () => {
  const likePost = useCallback(async (postId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Like post failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Post liked",
        description: "You liked this post",
      })

      return true
    } catch (error: any) {
      console.error('Like post failed:', error)
      toast({
        title: "Like post failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const unlikePost = useCallback(async (postId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}/like`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Unlike post failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Post unliked",
        description: "You unliked this post",
      })

      return true
    } catch (error: any) {
      console.error('Unlike post failed:', error)
      toast({
        title: "Unlike post failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const toggleLike = useCallback(async (postId: string, isCurrentlyLiked: boolean): Promise<boolean> => {
    if (isCurrentlyLiked) {
      return await unlikePost(postId)
    } else {
      return await likePost(postId)
    }
  }, [likePost, unlikePost])

  const getLikes = useCallback(async (
    postId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<TimelineLike[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      })

      const response = await fetch(`/api/v1/timeline/posts/${postId}/likes?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get likes failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get likes failed:', error)
      toast({
        title: "Get likes failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const likeComment = useCallback(async (commentId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/comments/${commentId}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Like comment failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Comment liked",
        description: "You liked this comment",
      })

      return true
    } catch (error: any) {
      console.error('Like comment failed:', error)
      toast({
        title: "Like comment failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  const unlikeComment = useCallback(async (commentId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/comments/${commentId}/like`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Unlike comment failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Comment unliked",
        description: "You unliked this comment",
      })

      return true
    } catch (error: any) {
      console.error('Unlike comment failed:', error)
      toast({
        title: "Unlike comment failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  return {
    likePost,
    unlikePost,
    toggleLike,
    getLikes,
    likeComment,
    unlikeComment,
  }
}