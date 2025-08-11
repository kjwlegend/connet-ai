/**
 * API Services exports
 */

export { apiClient, ApiClientClass } from './client'
export { conversationService, ConversationService } from './conversationService'
export { AuthAPI } from './auth'
export { API_ENDPOINTS } from './endpoints'
export { waitlistService, WaitlistService } from './waitlistService'

// Import other services as they are created
// export { contactService, ContactService } from './contactService'
// export { fileService, FileService } from './fileService'

// Export common types
export type { ApiResponse, ApiError } from '../types'

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