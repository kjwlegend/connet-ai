// Navigation Types
export type NavigationMode = 'chat' | 'contacts' | 'files' | 'social' | 'plugins' | 'settings'

// User and Authentication Types
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: 'user' | 'admin'
  subscription?: {
    plan: 'free' | 'pro' | 'enterprise'
    status: 'active' | 'inactive' | 'trial'
    expiresAt?: Date
  }
  preferences: {
    theme: 'light' | 'dark' | 'system'
    language: 'en' | 'zh'
    notifications: boolean
  }
  createdAt: Date
  updatedAt: Date
}

// Agent Types
export interface Agent {
  id: string
  name: string
  displayName: string
  description: string
  specialty: string
  avatar?: string
  capabilities: string[]
  personality: {
    tone: 'professional' | 'casual' | 'friendly' | 'technical'
    style: 'concise' | 'detailed' | 'creative'
  }
  isActive: boolean
  responseTimeAvg: number
  rating?: number
  tags: string[]
}

export interface AgentStatus {
  agentId: string
  status: 'idle' | 'thinking' | 'responding' | 'offline'
  lastActive: Date
  currentTask?: string
}

// Chat and Message Types
export interface Conversation {
  id: string
  name: string
  title?: string
  avatar?: string
  lastMessage: string
  timestamp: string
  unreadCount: number
  isActive?: boolean
  isGroup?: boolean
  participants?: string[]
}

export interface ChatRoom {
  id: string
  name: string
  description?: string
  creatorId: string
  participants: User[]
  activeAgents: Agent[]
  settings: {
    isPublic: boolean
    maxAgents: number
    allowGuestAgents: boolean
    autoSave: boolean
  }
  metadata: {
    messageCount: number
    lastActivity: Date
    avgResponseTime: number
  }
  createdAt: Date
  updatedAt: Date
}

export interface Message {
  id: string
  chatroomId: string
  senderId: string // User ID or Agent ID
  senderType: 'user' | 'agent' | 'system'
  content: string
  messageType: 'text' | 'image' | 'file' | 'system' | 'agent_response'
  metadata: {
    mentions?: string[] // Agent IDs mentioned
    referencedMessages?: string[] // Message IDs referenced
    processingTime?: number
    confidence?: number
    agentInteractions?: string[] // Other agent IDs this message interacted with
  }
  status: 'sending' | 'sent' | 'delivered' | 'failed'
  createdAt: Date
  updatedAt: Date
}

export interface AgentResponse {
  id: string
  messageId: string
  agentId: string
  content: string
  confidence: number
  processingTime: number
  agentInteractions: string[]
  isPartOfCollaboration: boolean
  status: 'generating' | 'completed' | 'error'
  createdAt: Date
}

// WebSocket and Real-time Types
export interface WebSocketMessage {
  type:
    | 'message'
    | 'agent_join'
    | 'agent_leave'
    | 'typing'
    | 'status_update'
    | 'error'
  payload: any
  timestamp: Date
}

export interface TypingIndicator {
  userId?: string
  agentId?: string
  chatroomId: string
  isTyping: boolean
}

// UI State Types
export interface ChatUIState {
  selectedChatroom?: string
  isAgentPanelOpen: boolean
  isMentionPopoverOpen: boolean
  mentionQuery: string
  selectedAgents: string[]
  typingUsers: TypingIndicator[]
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error'
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: {
    message: string
    code: string
    details?: any
  }
  meta?: {
    pagination?: {
      page: number
      limit: number
      total: number
    }
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    page: number
    limit: number
    total: number
    hasNext: boolean
    hasPrevious: boolean
  }
}

// Form Types
export interface CreateChatroomForm {
  name: string
  description?: string
  isPublic: boolean
  maxAgents: number
  initialAgents: string[]
}

export interface AgentMentionForm {
  agentId: string
  context?: string
  urgency: 'low' | 'medium' | 'high'
}

// Error Types
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: Date
}

// Event Types for Analytics
export interface UserEvent {
  type:
    | 'chat_created'
    | 'agent_mentioned'
    | 'message_sent'
    | 'agent_response_received'
  userId: string
  chatroomId?: string
  agentId?: string
  metadata?: Record<string, any>
  timestamp: Date
}

// Configuration Types
export interface AppConfig {
  apiUrl: string
  wsUrl: string
  features: {
    multiAgent: boolean
    voiceChat: boolean
    fileSharing: boolean
  }
  limits: {
    maxAgentsPerRoom: number
    maxMessageLength: number
    maxRoomsPerUser: number
  }
}

// Store Types
export interface RootState {
  auth: AuthState
  chat: ChatState
  agents: AgentState
  ui: UIState
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface ChatState {
  chatrooms: ChatRoom[]
  messages: Record<string, Message[]>
  currentChatroom: string | null
  isLoading: boolean
  error: string | null
}

export interface AgentState {
  agents: Agent[]
  agentStatuses: Record<string, AgentStatus>
  availableAgents: Agent[]
  isLoading: boolean
  error: string | null
}

export interface UIState {
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'zh'
  sidebarOpen: boolean
  agentPanelOpen: boolean
  notifications: Notification[]
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  autoClose?: boolean
  duration?: number
  createdAt: Date
}
