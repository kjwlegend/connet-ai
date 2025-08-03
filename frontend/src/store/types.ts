import { AuthSlice } from './slices/authSlice'
import { UISlice } from './slices/uiSlice'

/**
 * Represents the complete state of the application store.
 * Combines all individual slice states and actions.
 */
export type StoreState = 
  & AuthSlice 
  & UISlice

// Re-export commonly used types
export type { User, UserPreferences } from './slices/authSlice'
export type { Toast, Modal } from './slices/uiSlice'
