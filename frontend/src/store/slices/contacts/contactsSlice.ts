/**
 * Contacts Slice for Store
 * Manages Contacts state and operations
 */

import { StateCreator } from "zustand";
import {
  ContactsService,
  type ContactResponse,
  type ContactCreateRequest,
  type ContactUpdateRequest,
  type ContactSearchResponse,
  type ContactKnowledgeResponse,
  type ContactToolResponse,
  type ContactListParams,
  type ContactSearchParams,
  type ContactType,
  type APIError
} from "@/services/api";

// Runtime-safe API error guard
const isAPIError = (e: unknown): e is APIError =>
  typeof e === "object" && e !== null && "message" in e;

export interface ContactsState {
  // Data
  contacts: ContactResponse[]
  searchResults: ContactSearchResponse[]
  currentContact: ContactResponse | null
  contactKnowledge: ContactKnowledgeResponse[]
  contactTools: ContactToolResponse[]
  
  // UI state
  contactsUI: {
    isLoading: boolean
    isSearching: boolean
    isCreating: boolean
    isUpdating: boolean
    isDeleting: boolean
    showAddModal: boolean
    showEditModal: boolean
    showSearchModal: boolean
  }
  
  // Error state
  contactsError: {
    current: string | null
    history: Array<{
      message: string
      timestamp: Date
      action: string
    }>
  }
  
  // Filters and search
  contactsFilters: {
    contactType?: ContactType
    status?: string
    tags?: string[]
    favoritesOnly?: boolean
    search?: string
  }
  
  // Pagination for contacts list
  contactsPagination: {
    skip: number
    limit: number
    hasMore: boolean
    total: number
  }
}

export interface ContactsActions {
  // Data actions
  setContacts: (contacts: ContactResponse[]) => void
  addContact: (contact: ContactResponse) => void
  updateContactInList: (contact: ContactResponse) => void
  removeContact: (contactId: string, contactType: ContactType) => void
  setCurrentContact: (contact: ContactResponse | null) => void
  setSearchResults: (results: ContactSearchResponse[]) => void
  setContactKnowledge: (knowledge: ContactKnowledgeResponse[]) => void
  setContactTools: (tools: ContactToolResponse[]) => void
  
  // UI actions
  setLoading: (loading: boolean) => void
  setSearching: (searching: boolean) => void
  setCreating: (creating: boolean) => void
  setUpdating: (updating: boolean) => void
  setDeleting: (deleting: boolean) => void
  toggleAddModal: (show?: boolean) => void
  toggleEditModal: (show?: boolean) => void
  toggleSearchModal: (show?: boolean) => void
  
  // Error actions
  setError: (error: string | null, action?: string) => void
  clearError: () => void
  clearErrorHistory: () => void
  
  // Filter actions
  setContactsFilters: (filters: Partial<ContactsState['contactsFilters']>) => void
  clearContactsFilters: () => void
  
  // Pagination actions
  setContactsPagination: (pagination: Partial<ContactsState['contactsPagination']>) => void
  
  // API operations - Contact Management
  createContact: (data: ContactCreateRequest) => Promise<ContactResponse>
  getUserContacts: (params?: ContactListParams, append?: boolean) => Promise<void>
  searchContacts: (params: ContactSearchParams) => Promise<void>
  getContact: (contactId: string, contactType: ContactType) => Promise<ContactResponse | null>
  updateContact: (contactId: string, contactType: ContactType, data: ContactUpdateRequest) => Promise<ContactResponse | null>
  deleteContact: (contactId: string, contactType: ContactType) => Promise<void>
  toggleFavorite: (contactId: string, contactType: ContactType) => Promise<boolean>
  
  // API operations - Knowledge Management
  addKnowledgeToContact: (contactId: string, contactType: ContactType, knowledgeBaseId: string, alias?: string) => Promise<ContactKnowledgeResponse>
  removeKnowledgeFromContact: (contactId: string, contactType: ContactType, knowledgeBaseId: string) => Promise<void>
  getContactKnowledgeBases: (contactId: string, contactType: ContactType) => Promise<void>
  
  // API operations - Tool Management
  addToolToContact: (contactId: string, contactType: ContactType, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<ContactToolResponse>
  removeToolFromContact: (contactId: string, contactType: ContactType, toolId: string) => Promise<void>
  getContactTools: (contactId: string, contactType: ContactType) => Promise<void>
  updateContactToolConfig: (contactId: string, contactType: ContactType, toolId: string, enabled?: boolean, toolConfig?: Record<string, any>) => Promise<ContactToolResponse | null>
  
  // Utility operations
  refreshContacts: () => Promise<void>
  loadMoreContacts: () => Promise<void>
  clearSearchResults: () => void
}

export type ContactsSlice = ContactsState & ContactsActions

// Initial state
const initialContactsState: ContactsState = {
  contacts: [],
  searchResults: [],
  currentContact: null,
  contactKnowledge: [],
  contactTools: [],
  contactsUI: {
    isLoading: false,
    isSearching: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    showAddModal: false,
    showEditModal: false,
    showSearchModal: false,
  },
  contactsError: {
    current: null,
    history: [],
  },
  contactsFilters: {},
  contactsPagination: {
    skip: 0,
    limit: 20,
    hasMore: false,
    total: 0,
  },
}

const createContactsSlice: StateCreator<ContactsSlice, [], [], ContactsSlice> = (set, get) => ({
  ...initialContactsState,

  // Data actions
  setContacts: (contacts) => {
    set({ contacts })
  },

  addContact: (contact) => {
    set(state => ({
      contacts: [contact, ...state.contacts],
      contactsPagination: {
        ...state.contactsPagination,
        total: state.contactsPagination.total + 1,
      },
    }))
  },

  updateContactInList: (contact) => {
    set(state => ({
      contacts: state.contacts.map(c => 
        c.following_id === contact.following_id && c.following_type === contact.following_type
          ? contact 
          : c
      ),
      currentContact: state.currentContact?.following_id === contact.following_id 
        ? contact 
        : state.currentContact,
    }))
  },

  removeContact: (contactId, contactType) => {
    set(state => ({
      contacts: state.contacts.filter(c => 
        !(c.following_id === contactId && c.following_type === contactType)
      ),
      currentContact: state.currentContact?.following_id === contactId 
        ? null 
        : state.currentContact,
      contactsPagination: {
        ...state.contactsPagination,
        total: Math.max(0, state.contactsPagination.total - 1),
      },
    }))
  },

  setCurrentContact: (contact) => {
    set({ currentContact: contact })
  },

  setSearchResults: (searchResults) => {
    set({ searchResults })
  },

  setContactKnowledge: (contactKnowledge) => {
    set({ contactKnowledge })
  },

  setContactTools: (contactTools) => {
    set({ contactTools })
  },

  // UI actions
  setLoading: (isLoading) => {
    set(state => ({
      contactsUI: { ...state.contactsUI, isLoading }
    }))
  },

  setSearching: (isSearching) => {
    set(state => ({
      contactsUI: { ...state.contactsUI, isSearching }
    }))
  },

  setCreating: (isCreating) => {
    set(state => ({
      contactsUI: { ...state.contactsUI, isCreating }
    }))
  },

  setUpdating: (isUpdating) => {
    set(state => ({
      contactsUI: { ...state.contactsUI, isUpdating }
    }))
  },

  setDeleting: (isDeleting) => {
    set(state => ({
      contactsUI: { ...state.contactsUI, isDeleting }
    }))
  },

  toggleAddModal: (show) => {
    set(state => ({
      contactsUI: {
        ...state.contactsUI,
        showAddModal: show !== undefined ? show : !state.contactsUI.showAddModal,
      }
    }))
  },

  toggleEditModal: (show) => {
    set(state => ({
      contactsUI: {
        ...state.contactsUI,
        showEditModal: show !== undefined ? show : !state.contactsUI.showEditModal,
      }
    }))
  },

  toggleSearchModal: (show) => {
    set(state => ({
      contactsUI: {
        ...state.contactsUI,
        showSearchModal: show !== undefined ? show : !state.contactsUI.showSearchModal,
      }
    }))
  },

  // Error actions
  setError: (error, action = 'unknown') => {
    set(state => ({
      contactsError: {
        current: error,
        history: error ? [
          ...state.contactsError.history.slice(-4), // Keep last 5 errors
          {
            message: error,
            timestamp: new Date(),
            action,
          }
        ] : state.contactsError.history,
      },
      contactsUI: {
        ...state.contactsUI,
        isLoading: false,
        isSearching: false,
        isCreating: false,
        isUpdating: false,
        isDeleting: false,
      }
    }))
  },

  clearError: () => {
    set(state => ({
      contactsError: { ...state.contactsError, current: null }
    }))
  },

  clearErrorHistory: () => {
    set(state => ({
      contactsError: { ...state.contactsError, history: [] }
    }))
  },

  // Filter actions
  setContactsFilters: (filters) => {
    set(state => ({
      contactsFilters: { ...state.contactsFilters, ...filters }
    }))
  },

  clearContactsFilters: () => {
    set({ contactsFilters: {} })
  },

  // Pagination actions
  setContactsPagination: (pagination) => {
    set(state => ({
      contactsPagination: { ...state.contactsPagination, ...pagination }
    }))
  },

  // API operations - Contact Management
  createContact: async (data) => {
    const { addContact, setError, setCreating } = get()

    try {
      setCreating(true)
      setError(null)

      const contact = await ContactsService.addContact(data)
      addContact(contact)
      
      return contact
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to add contact. Please try again."
      setError(errorMessage, 'createContact')
      throw error
    } finally {
      setCreating(false)
    }
  },

  getUserContacts: async (params = {}, append = false) => {
    const { setContacts, setError, setLoading, setContactsPagination, contactsFilters } = get()

    try {
      setLoading(true)
      setError(null)

      // Merge with current filters
      const mergedParams = {
        skip: 0,
        limit: 20,
        ...contactsFilters,
        ...params,
      }

      const contacts = await ContactsService.getUserContacts(mergedParams)
      
      if (append) {
        set(state => ({
          contacts: [...state.contacts, ...contacts]
        }))
      } else {
        setContacts(contacts)
      }

      setContactsPagination({
        skip: mergedParams.skip || 0,
        limit: mergedParams.limit || 20,
        hasMore: contacts.length === (mergedParams.limit || 20),
        total: contacts.length, // Note: API doesn't return total, so we use length
      })
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to load contacts. Please try again."
      setError(errorMessage, 'getUserContacts')
      throw error
    } finally {
      setLoading(false)
    }
  },

  searchContacts: async (params) => {
    const { setSearchResults, setError, setSearching } = get()

    try {
      setSearching(true)
      setError(null)

      const results = await ContactsService.searchContacts(params)
      setSearchResults(results)
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to search contacts. Please try again."
      setError(errorMessage, 'searchContacts')
      throw error
    } finally {
      setSearching(false)
    }
  },

  getContact: async (contactId, contactType) => {
    const { setCurrentContact, setError } = get()

    try {
      setError(null)

      const contact = await ContactsService.getContact(contactId, contactType)
      setCurrentContact(contact)
      
      return contact
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to get contact. Please try again."
      setError(errorMessage, 'getContact')
      throw error
    }
  },

  updateContact: async (contactId, contactType, data) => {
    const { updateContactInList, setError, setUpdating } = get()

    try {
      setUpdating(true)
      setError(null)

      const contact = await ContactsService.updateContact(contactId, contactType, data)
      if (contact) {
        updateContactInList(contact)
      }
      
      return contact
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to update contact. Please try again."
      setError(errorMessage, 'updateContact')
      throw error
    } finally {
      setUpdating(false)
    }
  },

  deleteContact: async (contactId, contactType) => {
    const { removeContact, setError, setDeleting } = get()

    try {
      setDeleting(true)
      setError(null)

      const success = await ContactsService.removeContact(contactId, contactType)
      if (success) {
        removeContact(contactId, contactType)
      }
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to remove contact. Please try again."
      setError(errorMessage, 'deleteContact')
      throw error
    } finally {
      setDeleting(false)
    }
  },

  toggleFavorite: async (contactId, contactType) => {
    const { updateContactInList, setError } = get()

    try {
      setError(null)

      const isFavorite = await ContactsService.toggleFavorite(contactId, contactType)
      
      // Update the contact in the list
      set(state => ({
        contacts: state.contacts.map(c => 
          c.following_id === contactId && c.following_type === contactType
            ? { ...c, is_favorite: isFavorite }
            : c
        ),
        currentContact: state.currentContact?.following_id === contactId
          ? { ...state.currentContact, is_favorite: isFavorite }
          : state.currentContact,
      }))
      
      return isFavorite
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to toggle favorite. Please try again."
      setError(errorMessage, 'toggleFavorite')
      throw error
    }
  },

  // API operations - Knowledge Management
  addKnowledgeToContact: async (contactId, contactType, knowledgeBaseId, alias) => {
    const { setError } = get()

    try {
      setError(null)

      const knowledge = await ContactsService.addKnowledgeToContact(contactId, contactType, {
        knowledge_base_id: knowledgeBaseId,
        alias,
      })
      
      // Add to current knowledge list if viewing this contact
      set(state => ({
        contactKnowledge: [...state.contactKnowledge, knowledge]
      }))
      
      return knowledge
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to add knowledge to contact. Please try again."
      setError(errorMessage, 'addKnowledgeToContact')
      throw error
    }
  },

  removeKnowledgeFromContact: async (contactId, contactType, knowledgeBaseId) => {
    const { setError } = get()

    try {
      setError(null)

      const success = await ContactsService.removeKnowledgeFromContact(contactId, contactType, knowledgeBaseId)
      
      if (success) {
        // Remove from current knowledge list
        set(state => ({
          contactKnowledge: state.contactKnowledge.filter(k => k.knowledge_base_id !== knowledgeBaseId)
        }))
      }
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to remove knowledge from contact. Please try again."
      setError(errorMessage, 'removeKnowledgeFromContact')
      throw error
    }
  },

  getContactKnowledgeBases: async (contactId, contactType) => {
    const { setContactKnowledge, setError } = get()

    try {
      setError(null)

      const knowledge = await ContactsService.getContactKnowledgeBases(contactId, contactType)
      setContactKnowledge(knowledge)
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to get contact knowledge bases. Please try again."
      setError(errorMessage, 'getContactKnowledgeBases')
      throw error
    }
  },

  // API operations - Tool Management
  addToolToContact: async (contactId, contactType, toolId, enabled = true, toolConfig) => {
    const { setError } = get()

    try {
      setError(null)

      const tool = await ContactsService.addToolToContact(contactId, contactType, {
        tool_id: toolId,
        enabled,
        tool_config: toolConfig,
      })
      
      // Add to current tools list if viewing this contact
      set(state => ({
        contactTools: [...state.contactTools, tool]
      }))
      
      return tool
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to add tool to contact. Please try again."
      setError(errorMessage, 'addToolToContact')
      throw error
    }
  },

  removeToolFromContact: async (contactId, contactType, toolId) => {
    const { setError } = get()

    try {
      setError(null)

      const success = await ContactsService.removeToolFromContact(contactId, contactType, toolId)
      
      if (success) {
        // Remove from current tools list
        set(state => ({
          contactTools: state.contactTools.filter(t => t.tool_id !== toolId)
        }))
      }
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to remove tool from contact. Please try again."
      setError(errorMessage, 'removeToolFromContact')
      throw error
    }
  },

  getContactTools: async (contactId, contactType) => {
    const { setContactTools, setError } = get()

    try {
      setError(null)

      const tools = await ContactsService.getContactTools(contactId, contactType)
      setContactTools(tools)
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to get contact tools. Please try again."
      setError(errorMessage, 'getContactTools')
      throw error
    }
  },

  updateContactToolConfig: async (contactId, contactType, toolId, enabled, toolConfig) => {
    const { setError } = get()

    try {
      setError(null)

      const tool = await ContactsService.updateContactToolConfig(contactId, contactType, toolId, {
        enabled,
        tool_config: toolConfig,
      })
      
      if (tool) {
        // Update in current tools list
        set(state => ({
          contactTools: state.contactTools.map(t => t.tool_id === toolId ? tool : t)
        }))
      }
      
      return tool
    } catch (error) {
      const errorMessage = isAPIError(error) ? error.message : "Failed to update contact tool config. Please try again."
      setError(errorMessage, 'updateContactToolConfig')
      throw error
    }
  },

  // Utility operations
  refreshContacts: async () => {
    const { getUserContacts, contactsPagination } = get()
    await getUserContacts({ skip: 0, limit: contactsPagination.limit })
  },

  loadMoreContacts: async () => {
    const { getUserContacts, contactsPagination } = get()
    if (contactsPagination.hasMore) {
      await getUserContacts({ 
        skip: contactsPagination.skip + contactsPagination.limit, 
        limit: contactsPagination.limit 
      }, true)
    }
  },

  clearSearchResults: () => {
    set({ searchResults: [] })
  },
})

export default createContactsSlice