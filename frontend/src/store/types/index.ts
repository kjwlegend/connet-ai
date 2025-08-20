/**
 * Centralized type exports for the enhanced store architecture
 */

// Common types
export type {
  CachedData,
  SyncStatus,
  BaseEntity,
  PaginationMeta,
  PaginatedResult,
  ApiResponse,
  StoreError,
  LoadingState,
  DeviceInfo,
  DeepPartial,
  RequiredKeys,
  OptionalKeys,
  Slice,
} from './common'

// UI types
export type {
  ThemeMode,
  ThemePreferences,
  LayoutState,
  LayoutPreferences,
  NavigationMode,
  NavigationState,
  BreadcrumbItem,
  Modal,
  ModalState,
  Toast,
  ToastType,
  NotificationState,
  ResponsiveState,
  AccessibilityState,
  UserUIPreferences,
  UIState,
} from './ui'

// Chat types
export type {
  UserType,
  MessageContentType,
  ConversationType,
  ParticipantStatus,
  Message,
  MessageMetadata,
  AttachmentInfo,
  Participant,
  Conversation,
  ConversationSettings,
  ConversationMetadata,
  ConversationState,
  MessageState,
  RealtimeState,
  TypingIndicator,
  MessageDraft,
  MessageThread,
  MessageSearchQuery,
  MessageSearchResult,
  RealtimeEvent,
  PresenceInfo,
  SendMessagePayload,
  UpdateMessagePayload,
  CreateConversationPayload,
  UpdateConversationPayload,
  ConversationListResponse,
  MessageListResponse,
  ChatEntities,
  ChatStates,
  ChatPayloads,
} from './chat'

// Auth types
export type {
  UserPreferences as AuthUserPreferences, // Renamed to avoid conflict with UI preferences
  UserProfile,
  Permission,
  Role,
  AuthTokens,
  AuthSession,
  Organization,
  OrganizationMembership,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RefreshTokenRequest,
  PasswordResetRequest,
  PasswordResetConfirmRequest,
  ChangePasswordRequest,
  UpdateProfileRequest,
  AuthState,
  AuthActions,
  AuthSlice,
  PermissionCheck,
  AuthContextType,
  AuthEntities,
  AuthRequests,
} from './auth'

// Store slice types (re-exports)
export type { PreferencesSlice } from '../slices/ui/preferencesSlice'
export type { LayoutSlice } from '../slices/ui/layoutSlice'
export type { NotificationSlice } from '../slices/ui/notificationSlice'
export type { ConversationSlice } from '../slices/chat/conversationSlice'

// Utility type collections for easier imports
export namespace StoreTypes {
  export namespace UI {
    export type Preferences = UserUIPreferences
    export type Layout = LayoutState
    export type Navigation = NavigationState
    export type Notifications = NotificationState
    export type Modals = ModalState
    export type ToastItem = Toast
    export type ModalItem = Modal
  }

  export namespace Chat {
    export type MessageItem = Message
    export type ConversationItem = Conversation
    export type ParticipantItem = Participant
    export type Thread = MessageThread
    export type Draft = MessageDraft
    export type SearchQuery = MessageSearchQuery
    export type SearchResult = MessageSearchResult
  }

  export namespace Auth {
    export type User = UserProfile
    export type Session = AuthSession
    export type Tokens = AuthTokens
    export type LoginData = LoginRequest
    export type RegisterData = RegisterRequest
  }

  export namespace Common {
    export type Cached<T> = CachedData<T>
    export type Entity = BaseEntity
    export type Error = StoreError
    export type Loading = LoadingState
    export type ApiResult<T> = ApiResponse<T>
    export type PaginatedData<T> = PaginatedResult<T>
  }
}

// Action type helpers
export type ActionCreator<T extends (...args: any[]) => any> = T
export type AsyncActionCreator<T extends (...args: any[]) => Promise<any>> = T

// Selector type helpers
export type Selector<TState, TResult> = (state: TState) => TResult
export type EqualityChecker<T> = (a: T, b: T) => boolean

// Store configuration types
export interface StoreConfig {
  enableDevtools: boolean
  enablePersistence: boolean
  enableLogging: boolean
  cacheDefaultTTL: number
  maxRetries: number
}

// Error boundary types for store
export interface StoreErrorInfo {
  componentStack: string
  errorBoundary: string
}

export interface StoreErrorState {
  hasError: boolean
  error: Error | null
  errorInfo: StoreErrorInfo | null
}

// Performance monitoring types
export interface StorePerformanceMetrics {
  renderCount: number
  lastRenderTime: number
  averageRenderTime: number
  slowRenderThreshold: number
  memoryUsage: number
  cacheHitRate: number
}

// Migration types for schema updates
export interface StoreMigration {
  version: number
  migrate: (oldState: any) => any
  rollback?: (newState: any) => any
}

export interface StoreMigrationConfig {
  currentVersion: number
  migrations: StoreMigration[]
}

// Testing utility types
export interface StoreTestUtils {
  createMockState: <T>(overrides?: Partial<T>) => T
  createMockActions: <T>(overrides?: Partial<T>) => T
  waitForState: <T>(predicate: (state: T) => boolean, timeout?: number) => Promise<T>
  resetStore: () => void
}

// Development utility types
export interface StoreDevUtils {
  getStoreStats: () => {
    stateSize: number
    actionCount: number
    subscriptionCount: number
    cacheStats: any
  }
  exportState: () => string
  importState: (serializedState: string) => void
  timeTravel: (timestamp: number) => void
}

// Type guards for runtime type checking
export const isStoreError = (value: any): value is StoreError => {
  return typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'message' in value &&
    'timestamp' in value
}

export const isCachedData = <T>(value: any): value is CachedData<T> => {
  return typeof value === 'object' &&
    value !== null &&
    'data' in value &&
    'timestamp' in value &&
    'ttl' in value
}

export const isMessage = (value: any): value is Message => {
  return typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'conversationId' in value &&
    'senderId' in value &&
    'content' in value
}

export const isConversation = (value: any): value is Conversation => {
  return typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'title' in value &&
    'participants' in value &&
    Array.isArray(value.participants)
}

// Constants for common values
export const STORE_CONSTANTS = {
  CACHE_TTL: {
    UI_PREFERENCES: Infinity,
    LAYOUT_STATE: 1000 * 60 * 60 * 24 * 30, // 30 days
    CONVERSATIONS: 1000 * 60 * 60 * 2, // 2 hours
    MESSAGES: 1000 * 60 * 30, // 30 minutes
    USER_PROFILE: 1000 * 60 * 15, // 15 minutes
  },
  LIMITS: {
    MAX_TOASTS: 10,
    MAX_MODALS: 5,
    MAX_HISTORY: 50,
    MAX_CACHE_SIZE: 100 * 1024 * 1024, // 100MB
  },
  DEFAULTS: {
    TOAST_DURATION: 5000,
    RETRY_DELAY: 1000,
    DEBOUNCE_DELAY: 300,
  },
} as const