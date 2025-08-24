'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { useContacts } from '@/store'
import { useContactsQuery, useContactsMutation, useContactsSearch, useContactsKnowledge, useContactsTools } from '@/hooks/business/contacts'
import type { ContactType, RelationshipType, NotificationLevel } from '@/services/api'

export default function ContactsTestPage() {
  const contacts = useContacts()
  const { loadContacts, getContact } = useContactsQuery()
  const { createContact, updateContact, deleteContact, toggleFavorite } = useContactsMutation()
  const { searchContacts } = useContactsSearch()
  const { loadContactKnowledgeBases } = useContactsKnowledge()
  const { loadContactTools } = useContactsTools()
  
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    followingId: '',
    followingType: 'user' as ContactType,
    displayName: 'Test Contact',
    relationshipType: 'follow' as RelationshipType,
    notes: 'This is a test contact',
    tags: ['test', 'demo'],
    isFavorite: false,
    notificationLevel: 'normal' as NotificationLevel,
    searchQuery: '',
    limit: 20,
    skip: 0,
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testAddContact = async () => {
    try {
      addLog('Testing add contact with new business hooks...')
      const contactData = {
        following_id: testData.followingId,
        following_type: testData.followingType,
        display_name: testData.displayName,
        relationship_type: testData.relationshipType,
        notes: testData.notes,
        tags: testData.tags,
        is_favorite: testData.isFavorite,
        notification_level: testData.notificationLevel,
      }

      const result = await createContact(contactData)
      addLog(`✅ Add contact success: ${result.display_name || result.following_id}`)
      addLog(`   Type: ${result.following_type}, Relationship: ${result.relationship_type}`)
      addLog(`   Is favorite: ${result.is_favorite}`)
    } catch (error: any) {
      addLog(`❌ Add contact failed: ${error.message}`)
    }
  }

  const testGetUserContacts = async () => {
    try {
      addLog('Testing get user contacts with new business hooks...')
      const params = {
        skip: testData.skip,
        limit: testData.limit,
        ...(testData.followingType && { contact_type: testData.followingType }),
        ...(testData.isFavorite && { favorites_only: true }),
        ...(testData.searchQuery && { search: testData.searchQuery }),
      }

      await loadContacts(params)
      addLog(`✅ Get user contacts success: Found ${contacts.contacts.length} contacts`)
      addLog(`   Total in pagination: ${contacts.pagination.total}`)
      contacts.contacts.forEach((contact, index) => {
        addLog(`  ${index + 1}. ${contact.display_name || 'Unknown'} (${contact.following_type})`)
      })
    } catch (error: any) {
      addLog(`❌ Get user contacts failed: ${error.message}`)
    }
  }

  const testSearchContacts = async () => {
    try {
      if (!testData.searchQuery) {
        addLog('❌ Please enter a search query first.')
        return
      }
      addLog(`Testing search contacts with new business hooks: "${testData.searchQuery}"`)
      const params = {
        query: testData.searchQuery,
        limit: testData.limit,
        ...(testData.followingType && { contact_type: testData.followingType }),
      }

      await searchContacts(params)
      addLog(`✅ Search contacts success: Found ${contacts.searchResults.length} results`)
      contacts.searchResults.forEach((contact, index) => {
        addLog(`  ${index + 1}. ${contact.name || contact.display_name} (${contact.type}) - Followed: ${contact.is_followed}`)
      })
    } catch (error: any) {
      addLog(`❌ Search contacts failed: ${error.message}`)
    }
  }

  const testGetContact = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing get specific contact with new business hooks: ${testData.followingId}`)
      const result = await getContact(testData.followingId, testData.followingType)
      if (result) {
        addLog(`✅ Get contact success: ${result.display_name || 'Unknown'}`)
        addLog(`   Notes: ${result.notes || 'None'}`)
        addLog(`   Tags: ${result.tags?.join(', ') || 'None'}`)
        addLog(`   Favorite: ${result.is_favorite}, Muted: ${result.is_muted}`)
      } else {
        addLog('❌ Contact not found')
      }
    } catch (error: any) {
      addLog(`❌ Get contact failed: ${error.message}`)
    }
  }

  const testUpdateContact = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing update contact with new business hooks: ${testData.followingId}`)
      const updateData = {
        display_name: `${testData.displayName} (Updated)`,
        notes: `${testData.notes} - Updated at ${new Date().toLocaleTimeString()}`,
        tags: [...testData.tags, 'updated'],
      }

      const result = await updateContact(testData.followingId, testData.followingType, updateData)
      if (result) {
        addLog(`✅ Update contact success: ${result.display_name}`)
        addLog(`   Updated notes: ${result.notes}`)
      } else {
        addLog('❌ Contact not found for update')
      }
    } catch (error: any) {
      addLog(`❌ Update contact failed: ${error.message}`)
    }
  }

  const testToggleFavorite = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing toggle favorite with new business hooks: ${testData.followingId}`)
      const result = await toggleFavorite(testData.followingId, testData.followingType)
      addLog(`✅ Toggle favorite success: ${result ? 'Now favorite' : 'No longer favorite'}`)
    } catch (error: any) {
      addLog(`❌ Toggle favorite failed: ${error.message}`)
    }
  }

  const testRemoveContact = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing remove contact with new business hooks: ${testData.followingId}`)
      await deleteContact(testData.followingId, testData.followingType)
      addLog(`✅ Remove contact success`)
    } catch (error: any) {
      addLog(`❌ Remove contact failed: ${error.message}`)
    }
  }

  const testGetContactKnowledge = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing get contact knowledge bases with new business hooks: ${testData.followingId}`)
      await loadContactKnowledgeBases(testData.followingId, testData.followingType)
      addLog(`✅ Get contact knowledge success: Found ${contacts.contactKnowledge.length} knowledge bases`)
      contacts.contactKnowledge.forEach((kb, index) => {
        addLog(`  ${index + 1}. ${kb.knowledge_base_name || 'Unknown'} - ${kb.alias || 'No alias'}`)
      })
    } catch (error: any) {
      addLog(`❌ Get contact knowledge failed: ${error.message}`)
    }
  }

  const testGetContactTools = async () => {
    try {
      if (!testData.followingId) {
        addLog('❌ Please enter a following ID first.')
        return
      }
      addLog(`Testing get contact tools with new business hooks: ${testData.followingId}`)
      await loadContactTools(testData.followingId, testData.followingType)
      addLog(`✅ Get contact tools success: Found ${contacts.contactTools.length} tools`)
      contacts.contactTools.forEach((tool, index) => {
        addLog(`  ${index + 1}. ${tool.tool_name || 'Unknown'} - Enabled: ${tool.enabled}`)
      })
    } catch (error: any) {
      addLog(`❌ Get contact tools failed: ${error.message}`)
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">Contacts API Test Page (with New Business Hooks)</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Following ID (UUID)</label>
                <Input
                  value={testData.followingId}
                  onChange={(e) => setTestData(prev => ({ ...prev, followingId: e.target.value }))}
                  placeholder="UUID of user/agent to follow"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Following Type</label>
                <Select
                  value={testData.followingType}
                  onValueChange={(value) => setTestData(prev => ({ ...prev, followingType: value as ContactType }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="agent">Agent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Display Name</label>
              <Input
                value={testData.displayName}
                onChange={(e) => setTestData(prev => ({ ...prev, displayName: e.target.value }))}
                placeholder="Custom display name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Relationship Type</label>
              <Select
                value={testData.relationshipType}
                onValueChange={(value) => setTestData(prev => ({ ...prev, relationshipType: value as RelationshipType }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="follow">Follow</SelectItem>
                  <SelectItem value="friend">Friend</SelectItem>
                  <SelectItem value="colleague">Colleague</SelectItem>
                  <SelectItem value="mentor">Mentor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Notes</label>
              <Textarea
                value={testData.notes}
                onChange={(e) => setTestData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Personal notes about the contact"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Tags (comma-separated)</label>
              <Input
                value={testData.tags.join(', ')}
                onChange={(e) => setTestData(prev => ({ 
                  ...prev, 
                  tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                }))}
                placeholder="tag1, tag2, tag3"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Notification Level</label>
                <Select
                  value={testData.notificationLevel}
                  onValueChange={(value) => setTestData(prev => ({ ...prev, notificationLevel: value as NotificationLevel }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="important">Important</SelectItem>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="all">All</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="favorite"
                  checked={testData.isFavorite}
                  onCheckedChange={(checked) => setTestData(prev => ({ ...prev, isFavorite: !!checked }))}
                />
                <label htmlFor="favorite" className="text-sm font-medium">Mark as Favorite</label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Search Query</label>
              <Input
                value={testData.searchQuery}
                onChange={(e) => setTestData(prev => ({ ...prev, searchQuery: e.target.value }))}
                placeholder="Search for contacts"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Skip</label>
                <Input
                  type="number"
                  value={testData.skip}
                  onChange={(e) => setTestData(prev => ({ ...prev, skip: parseInt(e.target.value) || 0 }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Limit</label>
                <Input
                  type="number"
                  value={testData.limit}
                  onChange={(e) => setTestData(prev => ({ ...prev, limit: parseInt(e.target.value) || 20 }))}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button 
                onClick={testAddContact} 
                size="sm"
                disabled={contacts.contactsUI.isCreating}
              >
                {contacts.contactsUI.isCreating ? 'Adding...' : 'Add Contact'}
              </Button>
              <Button 
                onClick={testGetUserContacts} 
                size="sm" 
                variant="outline"
                disabled={contacts.contactsUI.isLoading}
              >
                {contacts.contactsUI.isLoading ? 'Loading...' : 'Get Contacts'}
              </Button>
              <Button 
                onClick={testSearchContacts} 
                size="sm"
                disabled={contacts.contactsUI.isSearching}
              >
                {contacts.contactsUI.isSearching ? 'Searching...' : 'Search Contacts'}
              </Button>
              <Button 
                onClick={testGetContact} 
                size="sm"
                disabled={contacts.contactsUI.isLoading}
              >
                Get Contact
              </Button>
              <Button 
                onClick={testUpdateContact} 
                size="sm"
                disabled={contacts.contactsUI.isUpdating}
              >
                {contacts.contactsUI.isUpdating ? 'Updating...' : 'Update Contact'}
              </Button>
              <Button 
                onClick={testToggleFavorite} 
                size="sm"
                disabled={contacts.contactsUI.isLoading}
              >
                Toggle Favorite
              </Button>
              <Button 
                onClick={testGetContactKnowledge} 
                size="sm"
                disabled={contacts.contactsUI.isLoading}
              >
                Get Knowledge
              </Button>
              <Button 
                onClick={testGetContactTools} 
                size="sm"
                disabled={contacts.contactsUI.isLoading}
              >
                Get Tools
              </Button>
              <Button 
                onClick={testRemoveContact} 
                size="sm" 
                variant="destructive"
                disabled={contacts.contactsUI.isDeleting}
              >
                {contacts.contactsUI.isDeleting ? 'Removing...' : 'Remove Contact'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Logs */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Test Logs</CardTitle>
            <Button onClick={clearLogs} variant="outline" size="sm">Clear</Button>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md h-96 overflow-y-auto font-mono text-sm">
              {logs.length === 0 ? (
                <p className="text-gray-500">No logs yet. Click buttons to test APIs.</p>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current State */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Current State</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-mono text-sm">
            <div>
              <strong>Following ID:</strong> {testData.followingId || 'None'}
            </div>
            <div>
              <strong>Following Type:</strong> {testData.followingType}
            </div>
            <div>
              <strong>Display Name:</strong> {testData.displayName}
            </div>
            <div>
              <strong>Relationship:</strong> {testData.relationshipType}
            </div>
            <div>
              <strong>Is Favorite:</strong> {testData.isFavorite ? '✅ Yes' : '❌ No'}
            </div>
            <div>
              <strong>Notification Level:</strong> {testData.notificationLevel}
            </div>
            <div>
              <strong>Search Query:</strong> {testData.searchQuery || 'None'}
            </div>
            <div>
              <strong>Skip/Limit:</strong> {testData.skip}/{testData.limit}
            </div>
            <div>
              <strong>Store Loading:</strong> {contacts.contactsUI.isLoading ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Store Creating:</strong> {contacts.contactsUI.isCreating ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Store Error:</strong> {contacts.error.current || '✅ None'}
            </div>
            <div>
              <strong>Contacts Count:</strong> {contacts.contacts.length}
            </div>
            <div>
              <strong>Search Results:</strong> {contacts.searchResults.length}
            </div>
            <div>
              <strong>Current Contact:</strong> {contacts.currentContact?.display_name || 'None'}
            </div>
            <div>
              <strong>Knowledge Count:</strong> {contacts.contactKnowledge.length}
            </div>
            <div>
              <strong>Tools Count:</strong> {contacts.contactTools.length}
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <strong>Notes:</strong> {testData.notes}
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <strong>Tags:</strong> {testData.tags.join(', ') || 'None'}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}