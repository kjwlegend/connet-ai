import { BaseEntity, CachedData, PaginatedResult } from './common'

/**
 * Chat-related types for messaging functionality
 */

// Core chat entity types
export type UserType = 'user' | 'agent' | 'system'
export type MessageContentType = 'text' | 'image' | 'file' | 'code' | 'markdown' | 'rich'
export type ConversationType = 'individual' | 'group' | 'channel' | 'announcement'
export type ParticipantStatus = 'online' | 'offline' | 'busy' | 'away' | 'invisible'

// Message types
export interface MessageMetadata {
  mentions?: string[]
  attachments?: AttachmentInfo[]
  reactions?: Record<string, string[]> // emoji -> userIds
  editHistory?: {
    timestamp: string
    previousContent: string
    reason?: string
  }[]
  threadId?: string
  replyToId?: string
  forwarded?: boolean
  encrypted?: boolean
}

export interface AttachmentInfo {
  id: string
  name: string
  type: 'image' | 'file' | 'audio' | 'video'
  url: string
  thumbnailUrl?: string
  size: number
  mimeType: string
}

export interface Message extends BaseEntity {
  conversationId: string
  senderId: string
  senderName: string
  senderType: UserType
  content: string
  contentType: MessageContentType
  timestamp: string
  isRead: boolean
  isEdited: boolean
  isDeleted: boolean
  metadata?: MessageMetadata
}

// Participant types
export interface Participant extends BaseEntity {
  name: string
  displayName?: string
  type: UserType
  avatar?: string
  status: ParticipantStatus
  capabilities?: string[]
  permissions?: {
    canSendMessages: boolean
    canEditMessages: boolean
    canDeleteMessages: boolean
    canMentionAll: boolean
    canInviteOthers: boolean
  }
  lastSeenAt?: string
  joinedAt: string
}

// Conversation types
export interface ConversationSettings {
  allowNotifications: boolean
  soundEnabled: boolean
  archiveAfterDays?: number
  autoTranslate?: boolean
  theme?: string
}

export interface ConversationMetadata {
  description?: string
  category?: string
  tags?: string[]
  priority?: 'low' | 'normal' | 'high' | 'urgent'
  project?: string
  department?: string
}

export interface Conversation extends BaseEntity {
  title: string
  type: ConversationType
  participants: Participant[]
  lastMessage?: Message
  unreadCount: number
  totalMessages: number
  isPinned: boolean
  isArchived: boolean
  isMuted: boolean
  settings: ConversationSettings
  metadata?: ConversationMetadata
  ownerId?: string
  permissions?: {
    canRename: boolean
    canAddParticipants: boolean
    canRemoveParticipants: boolean
    canDelete: boolean
    canArchive: boolean
  }
}

// Typing indicator types
export interface TypingIndicator {
  conversationId: string
  userId: string
  userName: string
  timestamp: string
}

// Draft types
export interface MessageDraft {
  conversationId: string
  content: string
  mentions: string[]
  attachments: AttachmentInfo[]
  replyToId?: string
  lastModified: string
}

// Thread types
export interface MessageThread {
  id: string
  parentMessageId: string
  conversationId: string
  messages: Message[]
  participantIds: string[]
  createdAt: string
  updatedAt: string
}

// Search types
export interface MessageSearchQuery {
  text?: string
  senderId?: string
  conversationId?: string
  dateFrom?: string
  dateTo?: string
  contentType?: MessageContentType
  hasAttachments?: boolean
  limit?: number
  offset?: number
}

export interface MessageSearchResult {
  message: Message
  conversation: Conversation
  matchScore: number
  highlightedContent: string
}

// Realtime types
export interface RealtimeEvent {
  id: string
  type: 'message' | 'typing' | 'presence' | 'conversation_update' | 'reaction'
  conversationId?: string
  userId?: string
  timestamp: string
  data: any
}

export interface PresenceInfo {
  userId: string
  status: ParticipantStatus
  lastSeen: string
  currentConversation?: string
}

// State interfaces
export interface ConversationState {
  conversations: CachedData<Conversation[]>
  activeConversationId: string | null
  searchResults: MessageSearchResult[]
  filters: {
    showArchived: boolean
    showMuted: boolean
    category?: string
    participant?: string
  }
}

export interface MessageState {
  messages: Record<string, CachedData<Message[]>> // conversationId -> messages
  threads: Record<string, MessageThread> // threadId -> thread
  drafts: Record<string, MessageDraft> // conversationId -> draft
  searchCache: Record<string, MessageSearchResult[]> // queryHash -> results
}

export interface RealtimeState {
  isConnected: boolean
  reconnecting: boolean
  typingIndicators: TypingIndicator[]
  presenceInfo: Record<string, PresenceInfo> // userId -> presence
  pendingEvents: RealtimeEvent[]
  subscriptions: string[] // conversationIds
}

// Action payload types
export interface SendMessagePayload {
  conversationId: string
  content: string
  contentType?: MessageContentType
  mentions?: string[]
  attachments?: AttachmentInfo[]
  replyToId?: string
  metadata?: Partial<MessageMetadata>
}

export interface UpdateMessagePayload {
  messageId: string
  content?: string
  metadata?: Partial<MessageMetadata>
  reason?: string
}

export interface CreateConversationPayload {
  title: string
  type: ConversationType
  participantIds: string[]
  settings?: Partial<ConversationSettings>
  metadata?: ConversationMetadata
}

export interface UpdateConversationPayload {
  conversationId: string
  title?: string
  settings?: Partial<ConversationSettings>
  metadata?: Partial<ConversationMetadata>
}

// API response types
export interface ConversationListResponse {
  conversations: PaginatedResult<Conversation>
  totalUnread: number
  lastSyncTime: string
}

export interface MessageListResponse {
  messages: PaginatedResult<Message>
  threads: MessageThread[]
  participants: Participant[]
}

// Export grouped types
export type ChatEntities = {
  Message: Message
  Conversation: Conversation
  Participant: Participant
  MessageThread: MessageThread
}

export type ChatStates = {
  ConversationState: ConversationState
  MessageState: MessageState
  RealtimeState: RealtimeState
}

export type ChatPayloads = {
  SendMessage: SendMessagePayload
  UpdateMessage: UpdateMessagePayload
  CreateConversation: CreateConversationPayload
  UpdateConversation: UpdateConversationPayload
}