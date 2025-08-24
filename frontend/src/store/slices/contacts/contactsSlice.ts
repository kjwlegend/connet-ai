/**
 * 简化的联系人状态管理 Slice
 * 只负责状态管理，不包含业务逻辑
 * 业务逻辑已移至 /hooks/business/contacts/
 */

import { StateCreator } from "zustand"

// 基础类型（从API服务中导入）
export interface ContactResponse {
  following_id: string
  following_type: 'human' | 'agent'
  follower_id: string
  is_favorite: boolean
  created_at: string
  updated_at: string
  // 扩展属性
  name?: string
  avatar?: string
  description?: string
  tags?: string[]
}

export interface ContactSearchResponse extends ContactResponse {
  searchScore?: number
}

export interface ContactKnowledgeResponse {
  knowledge_base_id: string
  name: string
  description?: string
  alias?: string
  created_at: string
}

export interface ContactToolResponse {
  tool_id: string
  name: string
  description?: string
  enabled: boolean
  tool_config: Record<string, any>
  created_at: string
  updated_at: string
}

// 联系人状态接口
export interface ContactsState {
  // 数据状态
  data: {
    contacts: ContactResponse[]
    searchResults: ContactSearchResponse[]
    currentContact: ContactResponse | null
    contactKnowledge: ContactKnowledgeResponse[]
    contactTools: ContactToolResponse[]
  }
  
  // UI状态
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
  
  // 错误状态
  error: {
    current: string | null
    history: Array<{
      message: string
      timestamp: Date
      action: string
    }>
  }
  
  // 筛选和分页
  contactsFilters: {
    contactType?: 'human' | 'agent'
    status?: string
    tags?: string[]
    favoritesOnly?: boolean
    search?: string
  }
  
  pagination: {
    skip: number
    limit: number
    hasMore: boolean
    total: number
  }
}

// 联系人动作接口
export interface ContactsActions {
  // 数据状态管理
  setContacts: (contacts: ContactResponse[]) => void
  addContact: (contact: ContactResponse) => void
  updateContactInList: (contact: ContactResponse) => void
  removeContactFromList: (contactId: string, contactType: 'human' | 'agent') => void
  setCurrentContact: (contact: ContactResponse | null) => void
  setSearchResults: (results: ContactSearchResponse[]) => void
  setContactKnowledge: (knowledge: ContactKnowledgeResponse[]) => void
  setContactTools: (tools: ContactToolResponse[]) => void
  clearSearchResults: () => void
  
  // UI状态管理
  setLoading: (loading: boolean) => void
  setSearching: (searching: boolean) => void
  setCreating: (creating: boolean) => void
  setUpdating: (updating: boolean) => void
  setDeleting: (deleting: boolean) => void
  toggleAddModal: (show?: boolean) => void
  toggleEditModal: (show?: boolean) => void
  toggleSearchModal: (show?: boolean) => void
  
  // 错误状态管理
  setError: (error: string | null, action?: string) => void
  clearError: () => void
  clearErrorHistory: () => void
  
  // 筛选和分页管理
  setFilters: (filters: Partial<ContactsState['contactsFilters']>) => void
  clearFilters: () => void
  setPagination: (pagination: Partial<ContactsState['pagination']>) => void
  resetPagination: () => void
  
  // 批量操作
  clearAllData: () => void
}

export type ContactsSlice = ContactsState & ContactsActions

// 初始状态
const initialContactsState: ContactsState = {
  data: {
    contacts: [],
    searchResults: [],
    currentContact: null,
    contactKnowledge: [],
    contactTools: [],
  },
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
  error: {
    current: null,
    history: [],
  },
  contactsFilters: {},
  pagination: {
    skip: 0,
    limit: 20,
    hasMore: false,
    total: 0,
  },
}

const createContactsSlice: StateCreator<ContactsSlice, [], [], ContactsSlice> = (set, get) => ({
  ...initialContactsState,

  // 数据状态管理
  setContacts: (contacts) => {
    set(state => ({
      data: { ...state.data, contacts }
    }))
  },

  addContact: (contact) => {
    set(state => ({
      data: {
        ...state.data,
        contacts: [contact, ...state.data.contacts],
      },
      pagination: {
        ...state.pagination,
        total: state.pagination.total + 1,
      },
    }))
  },

  updateContactInList: (contact) => {
    set(state => ({
      data: {
        ...state.data,
        contacts: state.data.contacts.map(c => 
          c.following_id === contact.following_id && c.following_type === contact.following_type
            ? contact 
            : c
        ),
        currentContact: state.data.currentContact?.following_id === contact.following_id 
          ? contact 
          : state.data.currentContact,
      }
    }))
  },

  removeContactFromList: (contactId, contactType) => {
    set(state => ({
      data: {
        ...state.data,
        contacts: state.data.contacts.filter(c => 
          !(c.following_id === contactId && c.following_type === contactType)
        ),
        currentContact: state.data.currentContact?.following_id === contactId 
          ? null 
          : state.data.currentContact,
      },
      pagination: {
        ...state.pagination,
        total: Math.max(0, state.pagination.total - 1),
      },
    }))
  },

  setCurrentContact: (contact) => {
    set(state => ({
      data: { ...state.data, currentContact: contact }
    }))
  },

  setSearchResults: (searchResults) => {
    set(state => ({
      data: { ...state.data, searchResults }
    }))
  },

  setContactKnowledge: (contactKnowledge) => {
    set(state => ({
      data: { ...state.data, contactKnowledge }
    }))
  },

  setContactTools: (contactTools) => {
    set(state => ({
      data: { ...state.data, contactTools }
    }))
  },

  clearSearchResults: () => {
    set(state => ({
      data: { ...state.data, searchResults: [] }
    }))
  },

  // UI状态管理
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

  // 错误状态管理
  setError: (error, action = 'unknown') => {
    set(state => ({
      error: {
        current: error,
        history: error ? [
          ...state.error.history.slice(-4),
          {
            message: error,
            timestamp: new Date(),
            action,
          }
        ] : state.error.history,
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
      error: { ...state.error, current: null }
    }))
  },

  clearErrorHistory: () => {
    set(state => ({
      error: { ...state.error, history: [] }
    }))
  },

  // 筛选和分页管理
  setFilters: (filters) => {
    set(state => ({
      contactsFilters: { ...state.contactsFilters, ...filters }
    }))
  },

  clearFilters: () => {
    set(state => ({
      contactsFilters: {}
    }))
  },

  setPagination: (pagination) => {
    set(state => ({
      pagination: { ...state.pagination, ...pagination }
    }))
  },

  resetPagination: () => {
    set(state => ({
      pagination: {
        ...initialContactsState.pagination,
      }
    }))
  },

  // 批量操作
  clearAllData: () => {
    set(state => ({
      ...initialContactsState,
    }))
  },
})

export default createContactsSlice