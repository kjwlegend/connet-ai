'use client'

import { useState, useEffect, useCallback } from 'react'
import { AIAgent, ContactRequest, UseContactsReturn, AddContactSearchResult } from '@/types/contact'

// Mock data - replace with real API calls
const mockContacts: AIAgent[] = [
  {
    id: 'ai-coding-assistant',
    name: 'AI编程助手',
    displayName: 'CodeBot Pro',
    avatar: '/placeholder.svg',
    specialty: '全栈开发',
    description: '代码优化专家',
    status: 'online',
    type: 'agent',
    tags: ['编程', '代码审查'],
    isVerified: true,
    capabilities: ['code-generation', 'code-review'],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  }
]

const mockPendingRequests: ContactRequest[] = [
  {
    id: 'req-1',
    fromUserId: 'alice-cooper',
    fromUserName: 'Alice Cooper',
    fromUserAvatar: '/placeholder.svg',
    toUserId: 'current-user',
    message: '你好，希望能够添加你为联系人。',
    status: 'pending',
    createdAt: '2024-01-20',
    type: 'human'
  }
]

export function useContacts(): UseContactsReturn {
  const [contacts, setContacts] = useState<AIAgent[]>([])
  const [pendingRequests, setPendingRequests] = useState<ContactRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize data
  useEffect(() => {
    const loadContacts = async () => {
      try {
        setLoading(true)
        // In real app, these would be API calls
        await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
        setContacts(mockContacts)
        setPendingRequests(mockPendingRequests)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load contacts')
      } finally {
        setLoading(false)
      }
    }

    loadContacts()
  }, [])

  const addContact = useCallback(async (contactId: string) => {
    try {
      setLoading(true)
      // TODO: Implement API call to add contact
      console.log('Adding contact:', contactId)
      
      // Mock: Add contact to list if not already present
      const existingContact = contacts.find(c => c.id === contactId)
      if (!existingContact) {
        // In real app, fetch contact details from API
        const newContact: AIAgent = {
          id: contactId,
          name: 'New Contact',
          avatar: '/placeholder.svg',
          specialty: 'Unknown',
          description: 'New contact',
          status: 'offline',
          type: 'agent',
          tags: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        setContacts(prev => [...prev, newContact])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add contact')
      throw err
    } finally {
      setLoading(false)
    }
  }, [contacts])

  const removeContact = useCallback(async (contactId: string) => {
    try {
      setLoading(true)
      // TODO: Implement API call to remove contact
      console.log('Removing contact:', contactId)
      
      setContacts(prev => prev.filter(c => c.id !== contactId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove contact')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updateContact = useCallback(async (contactId: string, updates: Partial<AIAgent>) => {
    try {
      setLoading(true)
      // TODO: Implement API call to update contact
      console.log('Updating contact:', contactId, updates)
      
      setContacts(prev => prev.map(c => 
        c.id === contactId 
          ? { ...c, ...updates, updatedAt: new Date().toISOString() }
          : c
      ))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update contact')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const searchContacts = useCallback(async (query: string): Promise<AddContactSearchResult[]> => {
    try {
      // TODO: Implement API call to search contacts
      console.log('Searching contacts:', query)
      
      // Mock search results
      return new Promise((resolve) => {
        setTimeout(() => {
          const results = mockContacts
            .filter(contact => 
              contact.name.toLowerCase().includes(query.toLowerCase()) ||
              contact.id.toLowerCase().includes(query.toLowerCase()) ||
              (contact.displayName && contact.displayName.toLowerCase().includes(query.toLowerCase()))
            )
            .map(contact => ({ ...contact, searchScore: Math.random() }))
          resolve(results)
        }, 300)
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
      return []
    }
  }, [])

  const sendContactRequest = useCallback(async (contactId: string, message: string) => {
    try {
      setLoading(true)
      // TODO: Implement API call to send contact request
      console.log('Sending contact request:', contactId, message)
      
      // Mock: Add to pending requests (in real app this would be handled on the recipient's side)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send contact request')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const approveContactRequest = useCallback(async (requestId: string) => {
    try {
      setLoading(true)
      // TODO: Implement API call to approve contact request
      console.log('Approving contact request:', requestId)
      
      const request = pendingRequests.find(r => r.id === requestId)
      if (request) {
        // Add to contacts
        const newContact: AIAgent = {
          id: request.fromUserId,
          name: request.fromUserName,
          avatar: request.fromUserAvatar,
          specialty: 'Unknown',
          description: 'New contact from request',
          status: 'offline',
          type: 'human',
          tags: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        
        setContacts(prev => [...prev, newContact])
        setPendingRequests(prev => prev.filter(r => r.id !== requestId))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve contact request')
      throw err
    } finally {
      setLoading(false)
    }
  }, [pendingRequests])

  const rejectContactRequest = useCallback(async (requestId: string) => {
    try {
      setLoading(true)
      // TODO: Implement API call to reject contact request
      console.log('Rejecting contact request:', requestId)
      
      setPendingRequests(prev => prev.filter(r => r.id !== requestId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject contact request')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const getPendingRequestsCount = useCallback(() => {
    return pendingRequests.length
  }, [pendingRequests.length])

  return {
    contacts,
    pendingRequests,
    loading,
    error,
    addContact,
    removeContact,
    updateContact,
    searchContacts,
    sendContactRequest,
    approveContactRequest,
    rejectContactRequest,
    getPendingRequestsCount,
  }
}