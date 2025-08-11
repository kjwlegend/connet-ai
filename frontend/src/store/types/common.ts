/**
 * Common types used across the store
 */

// Cache-related types
export interface CachedData<T> {
  data: T
  timestamp: number
  ttl: number // Time to live in ms
  version?: number
}

export interface SyncStatus {
  lastSyncTime: number
  isOnline: boolean
  pendingOperations: number
  syncInProgress: boolean
}

// Base entity interface
export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
}

// Pagination types
export interface PaginationMeta {
  page: number
  limit: number
  total: number
  hasMore: boolean
}

export interface PaginatedResult<T> {
  data: T[]
  meta: PaginationMeta
}

// API response wrapper
export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

// Error types
export interface StoreError {
  id: string
  message: string
  code?: string
  context?: Record<string, any>
  timestamp: string
  resolved: boolean
}

// Loading states
export interface LoadingState {
  global: boolean
  operations: Record<string, boolean>
}

// Device information
export interface DeviceInfo {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  screenWidth: number
  screenHeight: number
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type RequiredKeys<T, K extends keyof T> = T & Required<Pick<T, K>>

export type OptionalKeys<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

// Store slice helpers
export type SliceState<T> = T
export type SliceActions<T> = T
export type Slice<TState, TActions> = SliceState<TState> & SliceActions<TActions>