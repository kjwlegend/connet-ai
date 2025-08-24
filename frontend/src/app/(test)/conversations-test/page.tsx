'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'

export default function ConversationsTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    title: 'Test Conversation',
    description: 'A test conversation for API testing',
    conversationType: 'chat',
    conversationId: '',
    participantId: '',
    participantType: 'user' as 'user' | 'agent',
    messageContent: 'Hello, this is a test message',
    messageType: 'text',
    replyToId: '',
    priority: 'normal',
    limit: 20,
    skip: 0,
    includeArchived: false,
    includePinnedOnly: false,
    searchQuery: '',
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testGetConversations = async () => {
    try {
      addLog('Testing get user conversations...')
      
      const params = new URLSearchParams({
        skip: testData.skip.toString(),
        limit: testData.limit.toString(),
        include_archived: testData.includeArchived.toString(),
        include_pinned_only: testData.includePinnedOnly.toString(),
        ...(testData.searchQuery && { search: testData.searchQuery })
      })

      const response = await fetch(`/api/v1/conversations/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversations retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get conversations failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get conversations error: ${error.message}`)
    }
  }

  const testCreateConversation = async () => {
    try {
      addLog('Testing create conversation...')
      
      const response = await fetch('/api/v1/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: testData.title,
          description: testData.description,
          conversation_type: testData.conversationType,
          priority: testData.priority,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation created: ${JSON.stringify(data, null, 2)}`)
        setTestData(prev => ({ ...prev, conversationId: data.id }))
      } else {
        const error = await response.text()
        addLog(`Create conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Create conversation error: ${error.message}`)
    }
  }

  const testGetConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing get single conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get conversation error: ${error.message}`)
    }
  }

  const testUpdateConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing update conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: testData.title + ' (Updated)',
          description: testData.description + ' - Updated via API test',
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation updated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Update conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Update conversation error: ${error.message}`)
    }
  }

  const testAddParticipant = async () => {
    try {
      if (!testData.conversationId || !testData.participantId) {
        addLog('Error: Conversation ID and Participant ID are required')
        return
      }

      addLog('Testing add participant to conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}/participants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          participant_id: testData.participantId,
          participant_type: testData.participantType,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Participant added: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Add participant failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Add participant error: ${error.message}`)
    }
  }

  const testPinConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing pin conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}/pin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          pinned: true,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation pinned: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Pin conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Pin conversation error: ${error.message}`)
    }
  }

  const testExportConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing export conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}/export`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation exported: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Export conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Export conversation error: ${error.message}`)
    }
  }

  const testDeleteConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing delete conversation...')
      
      const response = await fetch(`/api/v1/conversations/${testData.conversationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        addLog(`Conversation deleted successfully`)
        setTestData(prev => ({ ...prev, conversationId: '' }))
      } else {
        const error = await response.text()
        addLog(`Delete conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Delete conversation error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Conversations API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Conversation Test Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Title</label>
                <Input
                  value={testData.title}
                  onChange={(e) => setTestData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter conversation title"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  value={testData.description}
                  onChange={(e) => setTestData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter conversation description"
                  rows={3}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Conversation ID</label>
                <Input
                  value={testData.conversationId}
                  onChange={(e) => setTestData(prev => ({ ...prev, conversationId: e.target.value }))}
                  placeholder="Enter conversation ID"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Participant ID</label>
                  <Input
                    value={testData.participantId}
                    onChange={(e) => setTestData(prev => ({ ...prev, participantId: e.target.value }))}
                    placeholder="Enter participant ID"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Participant Type</label>
                  <Select
                    value={testData.participantType}
                    onValueChange={(value: 'user' | 'agent') => setTestData(prev => ({ ...prev, participantType: value }))}
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
                <label className="text-sm font-medium">Search Query</label>
                <Input
                  value={testData.searchQuery}
                  onChange={(e) => setTestData(prev => ({ ...prev, searchQuery: e.target.value }))}
                  placeholder="Enter search query"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Limit</label>
                  <Input
                    type="number"
                    value={testData.limit}
                    onChange={(e) => setTestData(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Skip</label>
                  <Input
                    type="number"
                    value={testData.skip}
                    onChange={(e) => setTestData(prev => ({ ...prev, skip: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="archived"
                    checked={testData.includeArchived}
                    onCheckedChange={(checked) => setTestData(prev => ({ ...prev, includeArchived: !!checked }))}
                  />
                  <label htmlFor="archived" className="text-sm font-medium">Include Archived</label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="pinned"
                    checked={testData.includePinnedOnly}
                    onCheckedChange={(checked) => setTestData(prev => ({ ...prev, includePinnedOnly: !!checked }))}
                  />
                  <label htmlFor="pinned" className="text-sm font-medium">Pinned Only</label>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Test Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testGetConversations} className="w-full" variant="default">
                Get Conversations
              </Button>
              
              <Button onClick={testCreateConversation} className="w-full" variant="outline">
                Create Conversation
              </Button>
              
              <Button onClick={testGetConversation} className="w-full" variant="outline">
                Get Single Conversation
              </Button>
              
              <Button onClick={testUpdateConversation} className="w-full" variant="outline">
                Update Conversation
              </Button>
              
              <Button onClick={testAddParticipant} className="w-full" variant="outline">
                Add Participant
              </Button>
              
              <Button onClick={testPinConversation} className="w-full" variant="outline">
                Pin Conversation
              </Button>
              
              <Button onClick={testExportConversation} className="w-full" variant="outline">
                Export Conversation
              </Button>
              
              <Button onClick={testDeleteConversation} className="w-full" variant="destructive">
                Delete Conversation
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="secondary">
                Clear Logs
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-gray-500">No test results yet</p>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="text-sm font-mono mb-2 break-all">
                    {log}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}