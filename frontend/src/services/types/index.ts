/**
 * Service layer types
 */

export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message?: string
  error?: string
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  timestamp: string
}

export interface PaginationParams {
  page?: number
  limit?: number
  cursor?: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    hasNext: boolean
    hasPrev: boolean
    nextCursor?: string
    prevCursor?: string
  }
}

// Request/Response types for conversations
export interface CreateConversationRequest {
  title: string
  participants: string[] // participant IDs
  type?: 'direct' | 'group' | 'channel'
  description?: string
}

export interface UpdateConversationRequest {
  title?: string
  description?: string
  settings?: Record<string, any>
}

export interface GetConversationsParams extends PaginationParams {
  type?: 'direct' | 'group' | 'channel'
  archived?: boolean
  search?: string
}

// Request/Response types for messages
export interface SendMessageRequest {
  conversationId: string
  content: string
  type?: 'text' | 'image' | 'file' | 'code'
  replyTo?: string
  attachments?: string[]
}

export interface GetMessagesParams extends PaginationParams {
  conversationId: string
  before?: string
  after?: string
}

// Request/Response types for contacts
export interface CreateContactRequest {
  name: string
  email?: string
  phone?: string
  type: 'human' | 'agent'
  metadata?: Record<string, any>
}

export interface UpdateContactRequest {
  name?: string
  email?: string
  phone?: string
  metadata?: Record<string, any>
}

export interface GetContactsParams extends PaginationParams {
  type?: 'human' | 'agent' | 'all'
  search?: string
  status?: 'pending' | 'accepted' | 'blocked'
}

// Service configuration
export interface ServiceConfig {
  baseURL: string
  timeout: number
  retries: number
  retryDelay: number
}

// Cache types
export interface CacheOptions {
  ttl?: number
  key?: string
  tags?: string[]
}

export interface CachedResult<T> {
  data: T
  timestamp: number
  ttl: number
  tags: string[]
}