/**
 * AI Agents Slice for Store
 * Manages AI Agents state and operations
 */

import { StateCreator } from 'zustand'
import {
  AgentsService,
  type AIAgentResponse,
  type AIAgentCreateRequest,
  type AIAgentUpdateRequest,
  type AIAgentListParams,
  type AIAgentVersionResponse,
  type DeployAgentResponse,
  type APIError,
} from '@/services/api'

// Runtime-safe API error guard
const isAPIError = (e: unknown): e is APIError =>
  typeof e === 'object' && e !== null && 'message' in e

export interface AgentsState {
  // Data
  agents: AIAgentResponse[]
  currentAgent: AIAgentResponse | null
  agentVersions: AIAgentVersionResponse[]

  // Pagination
  agentsPagination: {
    total: number
    page: number
    size: number
    hasMore: boolean
  }

  // UI state
  agentsUI: {
    isLoading: boolean
    isCreating: boolean
    isUpdating: boolean
    isDeleting: boolean
    isDeploying: boolean
    showCreateModal: boolean
    showEditModal: boolean
  }

  // Error state
  agentsError: {
    current: string | null
    history: Array<{
      message: string
      timestamp: Date
      action: string
    }>
  }

  // Filters and search
  agentsFilters: {
    agentType?: string
    status?: string
    search?: string
    sortBy?: string
    sortOrder: 'asc' | 'desc'
  }
}

export interface AgentsActions {
  // Data actions
  setAgents: (agents: AIAgentResponse[]) => void
  addAgent: (agent: AIAgentResponse) => void
  updateAgentInList: (agent: AIAgentResponse) => void
  removeAgent: (agentId: string) => void
  setCurrentAgent: (agent: AIAgentResponse | null) => void
  setAgentVersions: (versions: AIAgentVersionResponse[]) => void

  // UI actions
  setLoading: (loading: boolean) => void
  setCreating: (creating: boolean) => void
  setUpdating: (updating: boolean) => void
  setDeleting: (deleting: boolean) => void
  setDeploying: (deploying: boolean) => void
  toggleCreateModal: (show?: boolean) => void
  toggleEditModal: (show?: boolean) => void

  // Error actions
  setError: (error: string | null, action?: string) => void
  clearError: () => void
  clearErrorHistory: () => void

  // Filter actions
  setAgentsFilters: (filters: Partial<AgentsState['agentsFilters']>) => void
  clearAgentsFilters: () => void

  // Pagination actions
  setAgentsPagination: (pagination: Partial<AgentsState['agentsPagination']>) => void

  // API operations
  createAgent: (data: AIAgentCreateRequest) => Promise<AIAgentResponse>
  listAgents: (params?: AIAgentListParams, append?: boolean) => Promise<void>
  getAgent: (agentId: string) => Promise<AIAgentResponse>
  updateAgent: (
    agentId: string,
    data: AIAgentUpdateRequest
  ) => Promise<AIAgentResponse>
  deleteAgent: (agentId: string) => Promise<void>
  deployAgent: (agentId: string) => Promise<DeployAgentResponse>
  getAgentVersions: (agentId: string) => Promise<void>
  rollbackAgent: (
    agentId: string,
    versionNumber: string
  ) => Promise<AIAgentResponse>

  // Utility operations
  refreshAgents: () => Promise<void>
  searchAgents: (query: string) => Promise<void>
  loadMoreAgents: () => Promise<void>
}

export type AgentsSlice = AgentsState & AgentsActions

// Initial state
const initialAgentsState: AgentsState = {
  agents: [],
  currentAgent: null,
  agentVersions: [],
  agentsPagination: {
    total: 0,
    page: 1,
    size: 20,
    hasMore: false,
  },
  agentsUI: {
    isLoading: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    isDeploying: false,
    showCreateModal: false,
    showEditModal: false,
  },
  agentsError: {
    current: null,
    history: [],
  },
  agentsFilters: {
    sortOrder: 'desc',
  },
}

const createAgentsSlice: StateCreator<AgentsSlice, [], [], AgentsSlice> = (
  set,
  get
) => ({
  ...initialAgentsState,

  // Data actions
  setAgents: (agents) => {
    set({ agents })
  },

  addAgent: (agent) => {
    set((state) => ({
      agents: [agent, ...state.agents],
      agentsPagination: {
        ...state.agentsPagination,
        total: state.agentsPagination.total + 1,
      },
    }))
  },

  updateAgentInList: (agent) => {
    set((state) => ({
      agents: state.agents.map((a) => (a.id === agent.id ? agent : a)),
      currentAgent:
        state.currentAgent?.id === agent.id ? agent : state.currentAgent,
    }))
  },

  removeAgent: (agentId) => {
    set((state) => ({
      agents: state.agents.filter((a) => a.id !== agentId),
      currentAgent:
        state.currentAgent?.id === agentId ? null : state.currentAgent,
      agentsPagination: {
        ...state.agentsPagination,
        total: Math.max(0, state.agentsPagination.total - 1),
      },
    }))
  },

  setCurrentAgent: (agent) => {
    set({ currentAgent: agent })
  },

  setAgentVersions: (versions) => {
    set({ agentVersions: versions })
  },

  // UI actions
  setLoading: (isLoading) => {
    set((state) => ({
      agentsUI: { ...state.agentsUI, isLoading },
    }))
  },

  setCreating: (isCreating) => {
    set((state) => ({
      agentsUI: { ...state.agentsUI, isCreating },
    }))
  },

  setUpdating: (isUpdating) => {
    set((state) => ({
      agentsUI: { ...state.agentsUI, isUpdating },
    }))
  },

  setDeleting: (isDeleting) => {
    set((state) => ({
      agentsUI: { ...state.agentsUI, isDeleting },
    }))
  },

  setDeploying: (isDeploying) => {
    set((state) => ({
      agentsUI: { ...state.agentsUI, isDeploying },
    }))
  },

  toggleCreateModal: (show) => {
    set((state) => ({
      agentsUI: {
        ...state.agentsUI,
        showCreateModal: show !== undefined ? show : !state.agentsUI.showCreateModal,
      },
    }))
  },

  toggleEditModal: (show) => {
    set((state) => ({
      agentsUI: {
        ...state.agentsUI,
        showEditModal: show !== undefined ? show : !state.agentsUI.showEditModal,
      },
    }))
  },

  // Error actions
  setError: (error, action = 'unknown') => {
    set((state) => ({
      agentsError: {
        current: error,
        history: error
          ? [
              ...state.agentsError.history.slice(-4), // Keep last 5 errors
              {
                message: error,
                timestamp: new Date(),
                action,
              },
            ]
          : state.agentsError.history,
      },
      agentsUI: {
        ...state.agentsUI,
        isLoading: false,
        isCreating: false,
        isUpdating: false,
        isDeleting: false,
        isDeploying: false,
      },
    }))
  },

  clearError: () => {
    set((state) => ({
      agentsError: { ...state.agentsError, current: null },
    }))
  },

  clearErrorHistory: () => {
    set((state) => ({
      agentsError: { ...state.agentsError, history: [] },
    }))
  },

  // Filter actions
  setAgentsFilters: (filters) => {
    set((state) => ({
      agentsFilters: { ...state.agentsFilters, ...filters },
    }))
  },

  clearAgentsFilters: () => {
    set({
      agentsFilters: { sortOrder: 'desc' },
    })
  },

  // Pagination actions
  setAgentsPagination: (pagination) => {
    set((state) => ({
      agentsPagination: { ...state.agentsPagination, ...pagination },
    }))
  },

  // API operations
  createAgent: async (data) => {
    const { addAgent, setError, setCreating } = get()

    try {
      setCreating(true)
      setError(null)

      const agent = await AgentsService.createAgent(data)
      addAgent(agent)

      return agent
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to create agent. Please try again.'
      setError(errorMessage, 'createAgent')
      throw error
    } finally {
      setCreating(false)
    }
  },

  listAgents: async (params = {}, append = false) => {
    const { setAgents, setError, setLoading, setAgentsPagination, agentsFilters } = get()

    try {
      setLoading(true)
      setError(null)

      // Merge with current filters
      const mergedParams = {
        page: 1,
        size: 20,
        ...agentsFilters,
        ...params,
      }

      const response = await AgentsService.listAgents(mergedParams)

      if (append) {
        set((state) => ({
          agents: [...state.agents, ...response.agents],
        }))
      } else {
        setAgents(response.agents)
      }

      setAgentsPagination({
        total: response.total,
        page: response.page,
        size: response.size,
        hasMore:
          response.agents.length === response.size &&
          response.page * response.size < response.total,
      })
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to load agents. Please try again.'
      setError(errorMessage, 'listAgents')
      throw error
    } finally {
      setLoading(false)
    }
  },

  getAgent: async (agentId) => {
    const { setCurrentAgent, setError } = get()

    try {
      setError(null)

      const agent = await AgentsService.getAgent(agentId)
      setCurrentAgent(agent)

      return agent
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to get agent. Please try again.'
      setError(errorMessage, 'getAgent')
      throw error
    }
  },

  updateAgent: async (agentId, data) => {
    const { updateAgentInList, setError, setUpdating } = get()

    try {
      setUpdating(true)
      setError(null)

      const agent = await AgentsService.updateAgent(agentId, data)
      updateAgentInList(agent)

      return agent
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to update agent. Please try again.'
      setError(errorMessage, 'updateAgent')
      throw error
    } finally {
      setUpdating(false)
    }
  },

  deleteAgent: async (agentId) => {
    const { removeAgent, setError, setDeleting } = get()

    try {
      setDeleting(true)
      setError(null)

      await AgentsService.deleteAgent(agentId)
      removeAgent(agentId)
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to delete agent. Please try again.'
      setError(errorMessage, 'deleteAgent')
      throw error
    } finally {
      setDeleting(false)
    }
  },

  deployAgent: async (agentId) => {
    const { updateAgentInList, setError, setDeploying } = get()

    try {
      setDeploying(true)
      setError(null)

      const response = await AgentsService.deployAgent(agentId)

      // Refresh the agent to get updated deployment status
      const updatedAgent = await AgentsService.getAgent(agentId)
      updateAgentInList(updatedAgent)

      return response
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to deploy agent. Please try again.'
      setError(errorMessage, 'deployAgent')
      throw error
    } finally {
      setDeploying(false)
    }
  },

  getAgentVersions: async (agentId) => {
    const { setAgentVersions, setError } = get()

    try {
      setError(null)

      const versions = await AgentsService.getAgentVersions(agentId)
      setAgentVersions(versions)
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to get agent versions. Please try again.'
      setError(errorMessage, 'getAgentVersions')
      throw error
    }
  },

  rollbackAgent: async (agentId, versionNumber) => {
    const { updateAgentInList, setError } = get()

    try {
      setError(null)

      const agent = await AgentsService.rollbackAgent(agentId, versionNumber)
      updateAgentInList(agent)

      return agent
    } catch (error) {
      const errorMessage = isAPIError(error)
        ? error.message
        : 'Failed to rollback agent. Please try again.'
      setError(errorMessage, 'rollbackAgent')
      throw error
    }
  },

  // Utility operations
  refreshAgents: async () => {
    const { listAgents, agentsPagination } = get()
    await listAgents({ page: 1, size: agentsPagination.size })
  },

  searchAgents: async (query) => {
    const { setAgentsFilters, listAgents } = get()
    setAgentsFilters({ search: query })
    await listAgents({ search: query, page: 1 })
  },

  loadMoreAgents: async () => {
    const { listAgents, agentsPagination } = get()
    if (agentsPagination.hasMore) {
      await listAgents({ page: agentsPagination.page + 1 }, true)
    }
  },
})

export default createAgentsSlice