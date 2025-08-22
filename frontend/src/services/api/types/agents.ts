/**
 * AI Agents API Types
 * Types for AI Agents service API endpoints
 */

export type AIAgentType = "system" | "custom" | "specialized"
export type AIAgentStatus = "active" | "inactive" | "deprecated"

export interface PersonalityProfile {
  role: string
  expertise: string[]
  communication_style: string
  language_traits: string[]
  emotional_tendency: string
  creativity_level: number
  formality_level: number
  empathy_level: number
  curiosity_level: number
  behavior_rules: string[]
  goals: string[]
}

export interface ModelPreferences {
  default_model: string
  fallback_models: string[]
  intent_model?: string
  code_model?: string
  creative_model?: string
  temperature: number
  max_tokens?: number
  top_p: number
  frequency_penalty: number
  presence_penalty: number
}

export interface AIAgentCreateRequest {
  name: string
  display_name: string
  description?: string
  agent_type: AIAgentType
  system_prompt: string
  personality_config: PersonalityProfile
  model_preferences: ModelPreferences
  enabled_tools: string[]
  behavior_rules: string[]
  conversation_style: string
  capabilities: string[]
  max_context_length: number
  timeout_seconds: number
  required_permissions: string[]
}

export interface AIAgentUpdateRequest {
  display_name?: string
  description?: string
  system_prompt?: string
  personality_config?: Partial<PersonalityProfile>
  model_preferences?: Partial<ModelPreferences>
  enabled_tools?: string[]
  behavior_rules?: string[]
  conversation_style?: string
  max_context_length?: number
  timeout_seconds?: number
  status?: AIAgentStatus
}

export interface AIAgentResponse {
  id: string
  name: string
  display_name: string
  description?: string
  agent_type: string
  version: string
  status: string
  personality_config: Record<string, any>
  model_preferences: Record<string, any>
  enabled_tools: string[]
  capabilities: string[]
  created_by: string
  created_at: string
  updated_at: string
  last_used_at?: string
  usage_count: number
  success_rate: number
  avg_response_time: number
  deployment_status: string
}

export interface AIAgentListResponse {
  agents: AIAgentResponse[]
  total: number
  page: number
  size: number
}

export interface PaginationParams {
  page: number
  size: number
  sort_by?: string
  sort_order: "asc" | "desc"
}

export interface AIAgentListParams extends Partial<PaginationParams> {
  agent_type?: string
  status?: string
  search?: string
}

export interface AIAgentVersionResponse {
  version: string
  created_at: string
  changes: string[]
  is_current: boolean
}

export interface DeployAgentResponse {
  message: string
  agent_id: string
  deployment_status: string
}