export const APP_CONFIG = {
  NAME: 'Connet.AI',
  VERSION: '1.0.0',
  DESCRIPTION: 'AI协作平台',
  
  // UI Constants
  SIDEBAR_WIDTH: {
    MIN: 60,
    MAX: 120,
    DEFAULT: 80,
  },
  
  MIDDLE_PANEL_WIDTH: {
    MIN: 300,
    MAX: 400,
    DEFAULT: 350,
  },

  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // Chat
  MAX_MESSAGE_LENGTH: 4000,
  TYPING_TIMEOUT: 3000,
  MESSAGE_BATCH_SIZE: 50,

  // File Upload
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks
  MAX_CONCURRENT_UPLOADS: 3,

  // Cache
  CACHE_TTL: {
    SHORT: 5 * 60 * 1000, // 5 minutes
    MEDIUM: 30 * 60 * 1000, // 30 minutes
    LONG: 24 * 60 * 60 * 1000, // 24 hours
  },

  // WebSocket
  RECONNECT_INTERVAL: 5000,
  MAX_RECONNECT_ATTEMPTS: 5,
} as const

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  CHAT: '/chat',
  CONTACTS: '/contacts',
  FILES: '/files',
  TIMELINE: '/timeline',
  PLUGINS: '/plugins',
  SETTINGS: '/settings',
} as const

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  LANGUAGE: 'language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
} as const

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const