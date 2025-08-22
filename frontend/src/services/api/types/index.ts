/**
 * API Types Index
 * Re-exports all API types for easy importing
 */

// Auth types
export * from './auth'

// Agents types
export * from './agents'

// Contacts types
export * from './contacts'

// Common API response types
export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message: string
}

export interface ApiError {
  code: string
  message: string
  timestamp: string
  details?: any
}

export interface ServiceConfig {
  baseURL: string
  timeout: number
  retries: number
  retryDelay: number
}

// Conversation types (from existing conversationService.ts)
export interface Conversation {
  id: string
  title: string
  lastMessage?: string
  lastMessageAt?: Date
  participants: string[]
  isGroup: boolean
  isPinned: boolean
}

export interface Message {
  id: string
  conversationId: string
  content: string
  senderId: string
  senderName?: string
  timestamp: Date
  type: 'text' | 'image' | 'file'
}

export interface CreateConversationRequest {
  title: string
  participants: string[]
  isGroup?: boolean
}

export interface SendMessageRequest {
  content: string
  type?: 'text' | 'image' | 'file'
}

// Waitlist types (from existing waitlistService.ts)
export interface WaitlistEntry {
  email: string
  name?: string
  company?: string
  useCase?: string
  referralSource?: string
}

export interface WaitlistResponse {
  success: boolean
  message: string
  position?: number
}