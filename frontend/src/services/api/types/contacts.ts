/**
 * Contacts API Types
 * Types for Contacts service API endpoints
 */

export type ContactType = "user" | "agent"
export type RelationshipType = "follow" | "friend" | "colleague" | "mentor"
export type NotificationLevel = "none" | "important" | "normal" | "all"
export type OnlineStatus = "online" | "offline" | "away" | "busy" | "unknown"

export interface ContactCreateRequest {
  following_id: string
  following_type: ContactType
  display_name?: string
  relationship_type?: RelationshipType
  notes?: string
  tags?: string[]
  is_favorite?: boolean
  notification_level?: NotificationLevel
  shared_via?: string
}

export interface ContactUpdateRequest {
  display_name?: string
  notes?: string
  tags?: string[]
  notification_level?: NotificationLevel
  is_muted?: boolean
}

export interface ContactResponse {
  follower_id: string
  following_id: string
  following_type: ContactType
  relationship_type: RelationshipType
  display_name?: string
  notes?: string
  tags: string[]
  is_favorite: boolean
  is_muted: boolean
  is_blocked: boolean
  online_status: OnlineStatus
  last_seen_at?: string
  is_agent: boolean
  is_pinned: boolean
  notification_level: NotificationLevel
  created_at: string
  updated_at: string
  last_interaction_at?: string
}

export interface ContactSearchResponse {
  id: string
  type: ContactType
  name: string
  description?: string
  avatar_url?: string
  is_followed: boolean
}

export interface ContactKnowledgeResponse {
  id: string
  knowledge_base_id: string
  knowledge_base_name?: string
  alias?: string
  added_at: string
}

export interface ContactToolResponse {
  id: string
  tool_id: string
  tool_name?: string
  enabled: boolean
  tool_config?: Record<string, any>
  added_at: string
}

export interface ContactListParams {
  skip?: number
  limit?: number
  contact_type?: ContactType
  status?: string
  tags?: string[]
  favorites_only?: boolean
  search?: string
}

export interface ContactSearchParams {
  query: string
  contact_type?: ContactType
  limit?: number
  current_user_id?: string
}

export interface AddKnowledgeToContactRequest {
  knowledge_base_id: string
  alias?: string
}

export interface AddToolToContactRequest {
  tool_id: string
  enabled?: boolean
  tool_config?: Record<string, any>
}

export interface UpdateContactToolRequest {
  enabled?: boolean
  tool_config?: Record<string, any>
}

export interface QRCodeResponse {
  qr_code_data: string
  qr_code_image_url: string
  expires_at: string
  user_info: Record<string, any>
}

export interface ConversationStartResponse {
  conversation_id: string
  is_new_conversation: boolean
  message: string
}