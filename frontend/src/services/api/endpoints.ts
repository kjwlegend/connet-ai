export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },

  // Chat & Conversations
  CHAT: {
    CONVERSATIONS: '/chat/conversations',
    CONVERSATION: (id: string) => `/chat/conversations/${id}`,
    MESSAGES: (conversationId: string) => `/chat/conversations/${conversationId}/messages`,
    SEND_MESSAGE: (conversationId: string) => `/chat/conversations/${conversationId}/messages`,
  },

  // Agents & Contacts
  AGENTS: {
    LIST: '/agents',
    DETAIL: (id: string) => `/agents/${id}`,
    SEARCH: '/agents/search',
    AVAILABLE: '/agents/available',
  },

  // Files
  FILES: {
    LIST: '/files',
    UPLOAD: '/files/upload',
    DOWNLOAD: (id: string) => `/files/${id}/download`,
    DELETE: (id: string) => `/files/${id}`,
    METADATA: (id: string) => `/files/${id}/metadata`,
  },

  // Timeline & Social
  TIMELINE: {
    FEED: '/timeline/feed',
    POST: '/timeline/posts',
    POST_DETAIL: (id: string) => `/timeline/posts/${id}`,
    LIKE: (postId: string) => `/timeline/posts/${postId}/like`,
    COMMENT: (postId: string) => `/timeline/posts/${postId}/comments`,
  },

  // Plugins
  PLUGINS: {
    LIST: '/plugins',
    INSTALLED: '/plugins/installed',
    INSTALL: '/plugins/install',
    UNINSTALL: (id: string) => `/plugins/${id}/uninstall`,
    CONFIGURE: (id: string) => `/plugins/${id}/configure`,
  },

  // Settings
  SETTINGS: {
    USER: '/settings/user',
    PREFERENCES: '/settings/preferences',
    NOTIFICATIONS: '/settings/notifications',
    THEME: '/settings/theme',
  },

  // WebSocket
  WEBSOCKET: {
    CONNECT: '/ws/connect',
    CHAT: '/ws/chat',
    PRESENCE: '/ws/presence',
  },
} as const

export type APIEndpoints = typeof API_ENDPOINTS