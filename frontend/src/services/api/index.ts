/**
 * API Services exports
 * Centralized export point for all API services and utilities
 */

// Core API client
export { apiClient, ApiClientClass } from './client'
export type { RouteConfig } from './client'

// Services (new structure matching BFF endpoints)
export * from './services'

// Legacy services (to be migrated)
export { conversationService, ConversationService } from './conversationService'
export { waitlistService, WaitlistService } from './waitlistService'

// Endpoints config (deprecated - endpoints now defined within services)
export { API_ENDPOINTS } from './endpoints'

// Types
export * from './types'

// For backward compatibility with old lib/api imports
export const APIError = class extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.code = code
  }
}