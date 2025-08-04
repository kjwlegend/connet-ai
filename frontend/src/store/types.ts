import { AuthSlice } from './slices/authSlice'
import { UISlice } from './slices/uiSlice'
import { ChatSlice } from './slices/chatSlice'

/**
 * Represents the complete state of the application store.
 * Combines all individual slice states and actions.
 */
export type StoreState = 
  & AuthSlice 
  & UISlice
  & ChatSlice

// Re-export commonly used types
export type { User, UserPreferences } from './slices/authSlice'
export type { Toast, Modal } from './slices/uiSlice'
export type { Message, Conversation, Participant } from './slices/chatSlice'
