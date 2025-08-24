/**
 * Timeline Comments Business Hook
 * 处理时间轴评论相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface TimelineComment {
  id: string
  post_id: string
  author_id: string
  author_type: 'user' | 'agent'
  content: string
  parent_comment_id?: string
  like_count: number
  is_liked: boolean
  created_at: string
  updated_at: string
  replies?: TimelineComment[]
}

interface TimelineCommentCreate {
  content: string
  parent_comment_id?: string
}

export const useTimelineComments = () => {
  const getComments = useCallback(async (
    postId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<TimelineComment[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      })

      const response = await fetch(`/api/v1/timeline/posts/${postId}/comments?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get comments failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get comments failed:', error)
      toast({
        title: "Get comments failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  const createComment = useCallback(async (
    postId: string,
    commentData: TimelineCommentCreate
  ): Promise<TimelineComment | null> => {
    try {
      const response = await fetch(`/api/v1/timeline/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(commentData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Create comment failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Comment added",
        description: "Your comment has been added successfully",
      })

      return data
    } catch (error: any) {
      console.error('Create comment failed:', error)
      toast({
        title: "Create comment failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updateComment = useCallback(async (
    commentId: string,
    content: string
  ): Promise<TimelineComment | null> => {
    try {
      const response = await fetch(`/api/v1/timeline/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ content }),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update comment failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Comment updated",
        description: "Your comment has been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update comment failed:', error)
      toast({
        title: "Update comment failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const deleteComment = useCallback(async (commentId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/v1/timeline/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Delete comment failed: ${response.status} - ${error}`)
      }

      toast({
        title: "Comment deleted",
        description: "Your comment has been deleted successfully",
      })

      return true
    } catch (error: any) {
      console.error('Delete comment failed:', error)
      toast({
        title: "Delete comment failed",
        description: error.message,
        variant: "destructive",
      })
      return false
    }
  }, [])

  return {
    getComments,
    createComment,
    updateComment,
    deleteComment,
  }
}