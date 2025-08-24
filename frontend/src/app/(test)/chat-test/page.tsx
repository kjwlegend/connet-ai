'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export default function ChatTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    agentId: '',
    message: 'Hello, how are you?',
    conversationId: '',
    maxTokens: 1000,
    temperature: 0.7,
    streamResponse: false,
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testChatWithAgent = async () => {
    try {
      addLog('Testing chat with AI agent...')
      
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          agent_id: testData.agentId,
          message: testData.message,
          conversation_id: testData.conversationId || undefined,
          max_tokens: testData.maxTokens,
          temperature: testData.temperature,
          stream: testData.streamResponse,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Chat success: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Chat failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Chat error: ${error.message}`)
    }
  }

  const testCreateMemory = async () => {
    try {
      addLog('Testing create memory entry...')
      
      const response = await fetch('/api/v1/chat/memory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          conversation_id: testData.conversationId,
          content: 'This is a test memory entry',
          memory_type: 'context',
          metadata: {
            importance: 'high',
            tags: ['test', 'memory']
          }
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Memory created: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Memory creation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Memory creation error: ${error.message}`)
    }
  }

  const testGetMemory = async () => {
    try {
      addLog('Testing get memory entries...')
      
      const response = await fetch(`/api/v1/chat/memory?conversation_id=${testData.conversationId}&limit=10`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Memory retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Memory retrieval failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Memory retrieval error: ${error.message}`)
    }
  }

  const testConversationSummary = async () => {
    try {
      addLog('Testing get conversation summary...')
      
      const response = await fetch(`/api/v1/chat/summary?conversation_id=${testData.conversationId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation summary: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Summary retrieval failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Summary retrieval error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">AI Chat API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Chat Test Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Agent ID</label>
                <Input
                  value={testData.agentId}
                  onChange={(e) => setTestData(prev => ({ ...prev, agentId: e.target.value }))}
                  placeholder="Enter agent ID"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Message</label>
                <Textarea
                  value={testData.message}
                  onChange={(e) => setTestData(prev => ({ ...prev, message: e.target.value }))}
                  placeholder="Enter message to send"
                  rows={3}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Conversation ID (Optional)</label>
                <Input
                  value={testData.conversationId}
                  onChange={(e) => setTestData(prev => ({ ...prev, conversationId: e.target.value }))}
                  placeholder="Enter conversation ID"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Max Tokens</label>
                  <Input
                    type="number"
                    value={testData.maxTokens}
                    onChange={(e) => setTestData(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Temperature</label>
                  <Input
                    type="number"
                    step="0.1"
                    min="0"
                    max="2"
                    value={testData.temperature}
                    onChange={(e) => setTestData(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="stream"
                  checked={testData.streamResponse}
                  onChange={(e) => setTestData(prev => ({ ...prev, streamResponse: e.target.checked }))}
                />
                <label htmlFor="stream" className="text-sm font-medium">Stream Response</label>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Test Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testChatWithAgent} className="w-full" variant="default">
                Test Chat with Agent
              </Button>
              
              <Button onClick={testCreateMemory} className="w-full" variant="outline">
                Test Create Memory
              </Button>
              
              <Button onClick={testGetMemory} className="w-full" variant="outline">
                Test Get Memory
              </Button>
              
              <Button onClick={testConversationSummary} className="w-full" variant="outline">
                Test Conversation Summary
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="destructive">
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