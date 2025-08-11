export interface AIAgent {
  id: string // Unique identifier for @mentions
  name: string // Base name (required)
  displayName?: string // Custom display name (optional)
  avatar: string
  specialty: string
  description: string
  status: 'online' | 'offline' | 'busy'
  type: 'agent' | 'human'
  tags: string[]
  note?: string // User's personal note about this contact
  isVerified?: boolean // For verified agents or humans
  capabilities?: string[] // What this agent can do
  createdAt: string
  updatedAt: string
}

export interface ContactRequest {
  id: string
  fromUserId: string
  fromUserName: string
  fromUserAvatar: string
  toUserId: string
  message: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
  type: 'human' // Only humans require approval
}

export interface ShareContactDialog {
  isOpen: boolean
  contactId: string | null
}

export interface AddContactSearchResult extends AIAgent {
  searchScore?: number
  isAlreadyContact?: boolean
}

export interface ContactFilter {
  type: 'all' | 'agent' | 'human' | 'pending'
  tag?: string | null
}

// Hook interfaces for future API integration
export interface UseContactsReturn {
  contacts: AIAgent[]
  pendingRequests: ContactRequest[]
  loading: boolean
  error: string | null
  addContact: (contactId: string) => Promise<void>
  removeContact: (contactId: string) => Promise<void>
  updateContact: (contactId: string, updates: Partial<AIAgent>) => Promise<void>
  searchContacts: (query: string) => Promise<AddContactSearchResult[]>
  sendContactRequest: (contactId: string, message: string) => Promise<void>
  approveContactRequest: (requestId: string) => Promise<void>
  rejectContactRequest: (requestId: string) => Promise<void>
  getPendingRequestsCount: () => number
}

export interface UseShareContactReturn {
  shareDialog: ShareContactDialog
  openShareDialog: (contactId: string) => void
  closeShareDialog: () => void
  shareToConversation: (contactId: string) => Promise<void>
  generateShareLink: (contactId: string) => Promise<string>
}