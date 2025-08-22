/**
 * Contacts API Service
 * Handles all Contacts-related API calls
 */

import { apiClient } from '../client'
import type {
  ContactCreateRequest,
  ContactUpdateRequest,
  ContactResponse,
  ContactSearchResponse,
  ContactKnowledgeResponse,
  ContactToolResponse,
  ContactListParams,
  ContactSearchParams,
  AddKnowledgeToContactRequest,
  AddToolToContactRequest,
  UpdateContactToolRequest,
  QRCodeResponse,
  ConversationStartResponse,
  ContactType,
} from '../types/contacts'

export class ContactsService {
  private static readonly BASE_PATH = '/api/v1/contacts'

  /**
   * Add a new contact (follow user or agent)
   */
  static async addContact(
    data: ContactCreateRequest
  ): Promise<ContactResponse> {
    try {
      const response = await apiClient.post<ContactResponse>(
        this.BASE_PATH,
        data
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to add contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get user's contacts with filtering
   */
  static async getUserContacts(
    params: ContactListParams = {}
  ): Promise<ContactResponse[]> {
    try {
      const searchParams = new URLSearchParams()

      if (params.skip) searchParams.append('skip', params.skip.toString())
      if (params.limit) searchParams.append('limit', params.limit.toString())
      if (params.contact_type)
        searchParams.append('contact_type', params.contact_type)
      if (params.status) searchParams.append('status', params.status)
      if (params.tags)
        params.tags.forEach((tag) => searchParams.append('tags', tag))
      if (params.favorites_only) searchParams.append('favorites_only', 'true')
      if (params.search) searchParams.append('search', params.search)

      const response = await apiClient.get<ContactResponse[]>(
        `${this.BASE_PATH}?${searchParams.toString()}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to get contacts. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Search for users and agents to add as contacts
   */
  static async searchContacts(
    params: ContactSearchParams
  ): Promise<ContactSearchResponse[]> {
    try {
      const searchParams = new URLSearchParams()

      searchParams.append('query', params.query)
      if (params.contact_type)
        searchParams.append('contact_type', params.contact_type)
      if (params.limit) searchParams.append('limit', params.limit.toString())
      if (params.current_user_id)
        searchParams.append('current_user_id', params.current_user_id)

      const response = await apiClient.get<ContactSearchResponse[]>(
        `${this.BASE_PATH}/search?${searchParams.toString()}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to search contacts. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get specific contact details
   */
  static async getContact(
    contactId: string,
    contactType: ContactType
  ): Promise<ContactResponse | null> {
    try {
      const response = await apiClient.get<ContactResponse>(
        `${this.BASE_PATH}/${contactId}?contact_type=${contactType}`
      )
      return response.data
    } catch (error: any) {
      if (error?.status === 404) {
        return null
      }
      const errorMessage =
        error?.message || 'Failed to get contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Update contact information
   */
  static async updateContact(
    contactId: string,
    contactType: ContactType,
    data: ContactUpdateRequest
  ): Promise<ContactResponse | null> {
    try {
      const response = await apiClient.put<ContactResponse>(
        `${this.BASE_PATH}/${contactId}?contact_type=${contactType}`,
        data
      )
      return response.data
    } catch (error: any) {
      if (error?.status === 404) {
        return null
      }
      const errorMessage =
        error?.message || 'Failed to update contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Remove a contact (unfollow)
   */
  static async removeContact(
    contactId: string,
    contactType: ContactType
  ): Promise<boolean> {
    try {
      await apiClient.delete(`${this.BASE_PATH}/${contactId}?contact_type=${contactType}`)
      return true
    } catch (error: any) {
      if (error?.status === 404) {
        return false
      }
      const errorMessage =
        error?.message || 'Failed to remove contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Toggle favorite status for a contact
   */
  static async toggleFavorite(
    contactId: string,
    contactType: ContactType
  ): Promise<boolean> {
    try {
      const response = await apiClient.post<{ message: string }>(
        `${this.BASE_PATH}/${contactId}/toggle-favorite?contact_type=${contactType}`
      )
      // The backend returns a message indicating if it was added or removed
      // We'll parse this to determine the current state
      const isAdded = response.data.message.includes('added to')
      return isAdded
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to toggle favorite. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Contact Knowledge Base Management

  /**
   * Add knowledge base to a contact
   */
  static async addKnowledgeToContact(
    contactId: string,
    contactType: ContactType,
    data: AddKnowledgeToContactRequest
  ): Promise<ContactKnowledgeResponse> {
    try {
      const response = await apiClient.post<ContactKnowledgeResponse>(
        `${this.BASE_PATH}/${contactId}/knowledge/${data.knowledge_base_id}?contact_type=${contactType}&alias=${data.alias || ''}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message ||
        'Failed to add knowledge to contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Remove knowledge base from a contact
   */
  static async removeKnowledgeFromContact(
    contactId: string,
    contactType: ContactType,
    knowledgeBaseId: string
  ): Promise<boolean> {
    try {
      await apiClient.delete(
        `${this.BASE_PATH}/${contactId}/knowledge/${knowledgeBaseId}?contact_type=${contactType}`
      )
      return true
    } catch (error: any) {
      const errorMessage =
        error?.message ||
        'Failed to remove knowledge from contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get all knowledge bases for a contact
   */
  static async getContactKnowledgeBases(
    contactId: string,
    contactType: ContactType
  ): Promise<ContactKnowledgeResponse[]> {
    try {
      const response = await apiClient.get<ContactKnowledgeResponse[]>(
        `${this.BASE_PATH}/${contactId}/knowledge?contact_type=${contactType}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message ||
        'Failed to get contact knowledge bases. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Contact Tool Management

  /**
   * Add tool to a contact
   */
  static async addToolToContact(
    contactId: string,
    contactType: ContactType,
    data: AddToolToContactRequest
  ): Promise<ContactToolResponse> {
    try {
      const response = await apiClient.post<ContactToolResponse>(
        `${this.BASE_PATH}/${contactId}/tools/${data.tool_id}?contact_type=${contactType}&enabled=${data.enabled}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to add tool to contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Remove tool from a contact
   */
  static async removeToolFromContact(
    contactId: string,
    contactType: ContactType,
    toolId: string
  ): Promise<boolean> {
    try {
      await apiClient.delete(`${this.BASE_PATH}/${contactId}/tools/${toolId}?contact_type=${contactType}`)
      return true
    } catch (error: any) {
      const errorMessage =
        error?.message ||
        'Failed to remove tool from contact. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Get all tools for a contact
   */
  static async getContactTools(
    contactId: string,
    contactType: ContactType
  ): Promise<ContactToolResponse[]> {
    try {
      const response = await apiClient.get<ContactToolResponse[]>(
        `${this.BASE_PATH}/${contactId}/tools?contact_type=${contactType}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to get contact tools. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Update tool configuration for a contact
   */
  static async updateContactToolConfig(
    contactId: string,
    contactType: ContactType,
    toolId: string,
    data: UpdateContactToolRequest
  ): Promise<ContactToolResponse | null> {
    try {
      const response = await apiClient.put<ContactToolResponse>(
        `${this.BASE_PATH}/${contactId}/tools/${toolId}?contact_type=${contactType}&enabled=${data.enabled}`
      )
      return response.data
    } catch (error: any) {
      if (error?.status === 404) {
        return null
      }
      const errorMessage =
        error?.message ||
        'Failed to update contact tool config. Please try again.'
      throw new Error(errorMessage)
    }
  }

  // Additional Features (Placeholder implementations)

  /**
   * Start a conversation with a contact
   */
  static async startConversationWithContact(
    contactId: string,
    contactType: ContactType
  ): Promise<ConversationStartResponse> {
    try {
      const response = await apiClient.post<ConversationStartResponse>(
        `${this.BASE_PATH}/${contactId}/start-conversation?contact_type=${contactType}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to start conversation. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Generate QR code for adding user as contact
   */
  static async generateContactQRCode(
    targetUserId: string
  ): Promise<QRCodeResponse> {
    try {
      const response = await apiClient.post<QRCodeResponse>(
        `${this.BASE_PATH}/qr-code/${targetUserId}`
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to generate QR code. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Scan QR code to add contact
   */
  static async addContactViaQRCode(qrData: string): Promise<ContactResponse> {
    try {
      const response = await apiClient.post<ContactResponse>(
        `${this.BASE_PATH}/qr-scan`,
        { qr_data: qrData }
      )
      return response.data
    } catch (error: any) {
      const errorMessage =
        error?.message || 'Failed to add contact via QR code. Please try again.'
      throw new Error(errorMessage)
    }
  }
}

export default ContactsService
