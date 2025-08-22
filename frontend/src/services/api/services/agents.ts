/**
 * AI Agents API Service
 * Handles all AI Agents-related API calls
 */

import { apiClient } from '../client'
import type {
  AIAgentCreateRequest,
  AIAgentUpdateRequest,
  AIAgentResponse,
  AIAgentListResponse,
  AIAgentListParams,
  AIAgentVersionResponse,
  DeployAgentResponse,
} from '../types/agents'

export class AgentsService {
  private static readonly BASE_PATH = '/api/v1/agents'

  /**
   * Create a new AI agent
   */
  static async createAgent(data: AIAgentCreateRequest): Promise<AIAgentResponse> {
    try {
      const response = await apiClient.post<AIAgentResponse>(
        this.BASE_PATH,
        data
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to create agent. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * List AI agents with optional filtering and pagination
   */
  static async listAgents(params: AIAgentListParams = {}): Promise<AIAgentListResponse> {
    try {
      const searchParams = new URLSearchParams()
      
      if (params.page) searchParams.append('page', params.page.toString())
      if (params.size) searchParams.append('size', params.size.toString())
      if (params.agent_type) searchParams.append('agent_type', params.agent_type)
      if (params.status) searchParams.append('status', params.status)
      if (params.search) searchParams.append('search', params.search)
      if (params.sort_by) searchParams.append('sort_by', params.sort_by)
      if (params.sort_order) searchParams.append('sort_order', params.sort_order)

      const response = await apiClient.get<AIAgentListResponse>(
        `${this.BASE_PATH}?${searchParams.toString()}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to list agents. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get agent by ID
   */
  static async getAgent(agentId: string): Promise<AIAgentResponse> {
    try {
      const response = await apiClient.get<AIAgentResponse>(
        `${this.BASE_PATH}/${agentId}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to get agent. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Update agent configuration
   */
  static async updateAgent(
    agentId: string,
    data: AIAgentUpdateRequest
  ): Promise<AIAgentResponse> {
    try {
      const response = await apiClient.put<AIAgentResponse>(
        `${this.BASE_PATH}/${agentId}`,
        data
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to update agent. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Delete agent
   */
  static async deleteAgent(agentId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.BASE_PATH}/${agentId}`)
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to delete agent. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Deploy agent to production
   */
  static async deployAgent(agentId: string): Promise<DeployAgentResponse> {
    try {
      const response = await apiClient.post<DeployAgentResponse>(
        `${this.BASE_PATH}/${agentId}/deploy`
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to deploy agent. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get agent version history
   */
  static async getAgentVersions(agentId: string): Promise<AIAgentVersionResponse[]> {
    try {
      const response = await apiClient.get<AIAgentVersionResponse[]>(
        `${this.BASE_PATH}/${agentId}/versions`
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to get agent versions. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Rollback agent to specific version
   */
  static async rollbackAgent(
    agentId: string,
    versionNumber: string
  ): Promise<AIAgentResponse> {
    try {
      const response = await apiClient.post<AIAgentResponse>(
        `${this.BASE_PATH}/${agentId}/rollback/${versionNumber}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to rollback agent. Please try again.'
      throw new Error(errorMessage)
    }
  }
}

export default AgentsService