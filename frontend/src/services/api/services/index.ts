/**
 * API Services Index
 * Centralized exports for all API services matching BFF endpoint structure
 */

// Auth service
export { AuthService } from './auth'
export { AuthService as default } from './auth'

// Re-export for backward compatibility with existing code
export { AuthService as AuthAPI } from './auth'

// TODO: Add other services as they are implemented to match BFF endpoints
// export { ContactsService } from './contacts'
// export { ConversationsService } from './conversations'
// export { AIAgentsService } from './ai-agents'  
// export { AIChatService } from './ai-chat'
// export { TimelineService } from './timeline'
// export { SettingsService } from './settings'
// export { UsersService } from './users'
// export { HealthService } from './health'

// Types
export * from '../types'