/**
 * Conversation Service - API calls for chat functionality
 */

import { apiClient } from './client'
import { 
  ApiResponse, 
  PaginatedResponse,
  CreateConversationRequest,
  UpdateConversationRequest,
  GetConversationsParams,
  SendMessageRequest,
  GetMessagesParams
} from '../types'
import { Conversation, Message } from '@/store/types/chat'

export class ConversationService {
  private readonly baseURL = '/api/conversations'

  // Conversation CRUD
  async getConversations(params: GetConversationsParams = {}): Promise<PaginatedResponse<Conversation>> {
    const cacheKey = apiClient.getCacheKey(`${this.baseURL}/list`, params)
    const cached = apiClient.getFromCache<PaginatedResponse<Conversation>>(cacheKey)
    
    if (cached) {
      return cached
    }

    const response = await apiClient.get<PaginatedResponse<Conversation>['data']>(
      `${this.baseURL}`,
      params
    )

    const result: PaginatedResponse<Conversation> = {
      ...response,
      data: response.data?.map(this.transformConversation) || [],
      pagination: response.data?.pagination || {
        page: 1,
        limit: 20,
        total: 0,
        hasNext: false,
        hasPrev: false
      }
    }

    // Cache for 5 minutes
    apiClient.setCache(cacheKey, result, 5 * 60 * 1000)
    return result
  }

  async getConversation(id: string): Promise<ApiResponse<Conversation>> {
    const cacheKey = `${this.baseURL}/${id}`
    const cached = apiClient.getFromCache<Conversation>(cacheKey)
    
    if (cached) {
      return { data: cached, success: true }
    }

    const response = await apiClient.get<any>(`${this.baseURL}/${id}`)
    
    const conversation = this.transformConversation(response.data)
    
    // Cache for 15 minutes
    apiClient.setCache(cacheKey, conversation, 15 * 60 * 1000)
    
    return {
      ...response,
      data: conversation
    }
  }

  async createConversation(payload: CreateConversationRequest): Promise<ApiResponse<Conversation>> {
    const response = await apiClient.post<any>(this.baseURL, {
      title: payload.title,
      participant_ids: payload.participants,
      type: payload.type || 'direct',
      description: payload.description,
    })

    const conversation = this.transformConversation(response.data)

    // Clear conversations list cache
    apiClient.clearCache(`${this.baseURL}.*`)

    return {
      ...response,
      data: conversation
    }
  }

  async updateConversation(id: string, payload: UpdateConversationRequest): Promise<ApiResponse<Conversation>> {
    const response = await apiClient.patch<any>(`${this.baseURL}/${id}`, payload)
    
    const conversation = this.transformConversation(response.data)

    // Clear related cache
    apiClient.clearCache(`${this.baseURL}/${id}`)
    apiClient.clearCache(`${this.baseURL}.*`)

    return {
      ...response,
      data: conversation
    }
  }

  async deleteConversation(id: string): Promise<ApiResponse<void>> {
    const response = await apiClient.delete<void>(`${this.baseURL}/${id}`)

    // Clear related cache
    apiClient.clearCache(`${this.baseURL}/${id}`)
    apiClient.clearCache(`${this.baseURL}.*`)

    return response
  }

  // Conversation actions
  async pinConversation(id: string, pinned: boolean): Promise<ApiResponse<void>> {
    const response = await apiClient.patch<void>(`${this.baseURL}/${id}/pin`, { pinned })

    // Clear cache
    apiClient.clearCache(`${this.baseURL}/${id}`)
    apiClient.clearCache(`${this.baseURL}.*`)

    return response
  }

  async archiveConversation(id: string, archived: boolean): Promise<ApiResponse<void>> {
    const response = await apiClient.patch<void>(`${this.baseURL}/${id}/archive`, { archived })

    // Clear cache
    apiClient.clearCache(`${this.baseURL}/${id}`)
    apiClient.clearCache(`${this.baseURL}.*`)

    return response
  }

  async muteConversation(id: string, muted: boolean): Promise<ApiResponse<void>> {
    const response = await apiClient.patch<void>(`${this.baseURL}/${id}/mute`, { muted })

    // Clear cache
    apiClient.clearCache(`${this.baseURL}/${id}`)

    return response
  }

  // Export functionality
  async exportConversation(id: string, format: 'markdown' | 'json' = 'markdown'): Promise<ApiResponse<string>> {
    const response = await apiClient.get<{ content: string }>(
      `${this.baseURL}/${id}/export`,
      { format }
    )

    return {
      ...response,
      data: response.data?.content || ''
    }
  }

  // Messages
  async getMessages(params: GetMessagesParams): Promise<PaginatedResponse<Message>> {
    const { conversationId, ...queryParams } = params
    const cacheKey = apiClient.getCacheKey(`${this.baseURL}/${conversationId}/messages`, queryParams)
    const cached = apiClient.getFromCache<PaginatedResponse<Message>>(cacheKey)
    
    if (cached) {
      return cached
    }

    const response = await apiClient.get<PaginatedResponse<Message>['data']>(
      `${this.baseURL}/${conversationId}/messages`,
      queryParams
    )

    const result: PaginatedResponse<Message> = {
      ...response,
      data: response.data?.map(this.transformMessage) || [],
      pagination: response.data?.pagination || {
        page: 1,
        limit: 50,
        total: 0,
        hasNext: false,
        hasPrev: false
      }
    }

    // Cache messages for 2 minutes
    apiClient.setCache(cacheKey, result, 2 * 60 * 1000)
    return result
  }

  async sendMessage(payload: SendMessageRequest): Promise<ApiResponse<Message>> {
    const { conversationId, ...messageData } = payload
    
    const response = await apiClient.post<any>(
      `${this.baseURL}/${conversationId}/messages`,
      {
        content: messageData.content,
        type: messageData.type || 'text',
        reply_to: messageData.replyTo,
        attachment_ids: messageData.attachments,
      }
    )

    const message = this.transformMessage(response.data)

    // Clear messages cache for this conversation
    apiClient.clearCache(`${this.baseURL}/${conversationId}/messages.*`)

    return {
      ...response,
      data: message
    }
  }

  async updateMessage(conversationId: string, messageId: string, content: string): Promise<ApiResponse<Message>> {
    const response = await apiClient.patch<any>(
      `${this.baseURL}/${conversationId}/messages/${messageId}`,
      { content }
    )

    const message = this.transformMessage(response.data)

    // Clear messages cache
    apiClient.clearCache(`${this.baseURL}/${conversationId}/messages.*`)

    return {
      ...response,
      data: message
    }
  }

  async deleteMessage(conversationId: string, messageId: string): Promise<ApiResponse<void>> {
    const response = await apiClient.delete<void>(
      `${this.baseURL}/${conversationId}/messages/${messageId}`
    )

    // Clear messages cache
    apiClient.clearCache(`${this.baseURL}/${conversationId}/messages.*`)

    return response
  }

  // Data transformation methods
  private transformConversation(raw: any): Conversation {
    return {
      id: raw.id,
      title: raw.title,
      type: raw.type || 'direct',
      description: raw.description,
      participants: raw.participants?.map(this.transformParticipant) || [],
      createdAt: new Date(raw.created_at).toISOString(),
      updatedAt: new Date(raw.updated_at).toISOString(),
      isPinned: Boolean(raw.is_pinned),
      isArchived: Boolean(raw.is_archived),
      isMuted: Boolean(raw.is_muted),
      unreadCount: raw.unread_count || 0,
      lastMessage: raw.last_message ? this.transformMessage(raw.last_message) : null,
      settings: raw.settings || {},
      metadata: raw.metadata || {},
    }
  }

  private transformParticipant(raw: any) {
    return {
      id: raw.id,
      name: raw.name,
      type: raw.type || 'human',
      avatar: raw.avatar,
      status: raw.status || 'offline',
      role: raw.role || 'member',
      joinedAt: new Date(raw.joined_at).toISOString(),
    }
  }

  private transformMessage(raw: any): Message {
    return {
      id: raw.id,
      conversationId: raw.conversation_id,
      senderId: raw.sender_id,
      content: raw.content,
      type: raw.type || 'text',
      createdAt: new Date(raw.created_at).toISOString(),
      updatedAt: new Date(raw.updated_at).toISOString(),
      isEdited: Boolean(raw.is_edited),
      replyTo: raw.reply_to,
      attachments: raw.attachments?.map(this.transformAttachment) || [],
      metadata: raw.metadata || {},
      reactions: raw.reactions || [],
      mentions: raw.mentions || [],
      thread: raw.thread ? {
        id: raw.thread.id,
        messageCount: raw.thread.message_count,
        participants: raw.thread.participants,
        lastReply: raw.thread.last_reply ? new Date(raw.thread.last_reply).toISOString() : null,
      } : null,
    }
  }

  private transformAttachment(raw: any) {
    return {
      id: raw.id,
      name: raw.name,
      type: raw.type,
      size: raw.size,
      url: raw.url,
      thumbnailUrl: raw.thumbnail_url,
    }
  }
}

// Export singleton instance
export const conversationService = new ConversationService()