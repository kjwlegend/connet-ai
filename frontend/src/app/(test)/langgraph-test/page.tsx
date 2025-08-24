'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

export default function LangGraphTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    conversationId: '',
    title: 'LangGraph Test Conversation',
    conversationType: 'chat',
    initialAgentIds: '',
    content: 'Hello @agent1 and @agent2, can you help me with this task?',
    messageType: 'text',
    replyToId: '',
    agentId: '',
    role: 'member',
    workflowType: 'chat',
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testCreateConversation = async () => {
    try {
      addLog('Testing create LangGraph conversation...')
      
      const agentIds = testData.initialAgentIds
        .split(',')
        .map(id => id.trim())
        .filter(id => id.length > 0)

      const response = await fetch('/api/v1/langgraph/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: testData.title,
          conversation_type: testData.conversationType,
          initial_agent_ids: agentIds.length > 0 ? agentIds : undefined,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Conversation created: ${JSON.stringify(data, null, 2)}`)
        setTestData(prev => ({ ...prev, conversationId: data.conversation_id }))
      } else {
        const error = await response.text()
        addLog(`Create conversation failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Create conversation error: ${error.message}`)
    }
  }

  const testSendMessage = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing send message with LangGraph processing...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          content: testData.content,
          message_type: testData.messageType,
          reply_to_id: testData.replyToId || undefined,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Message sent: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Send message failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Send message error: ${error.message}`)
    }
  }

  const testGetConversation = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing get LangGraph conversation...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}`, {
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

  const testGetMessages = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing get conversation messages...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}/messages?limit=50`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Messages retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get messages failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get messages error: ${error.message}`)
    }
  }

  const testAddAgent = async () => {
    try {
      if (!testData.conversationId || !testData.agentId) {
        addLog('Error: Conversation ID and Agent ID are required')
        return
      }

      addLog('Testing add agent to conversation...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          agent_id: testData.agentId,
          role: testData.role,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Agent added: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Add agent failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Add agent error: ${error.message}`)
    }
  }

  const testGetWorkflowStatus = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing get workflow status...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}/workflow/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Workflow status: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get workflow status failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get workflow status error: ${error.message}`)
    }
  }

  const testTriggerWorkflow = async () => {
    try {
      if (!testData.conversationId) {
        addLog('Error: No conversation ID provided')
        return
      }

      addLog('Testing trigger workflow execution...')
      
      const response = await fetch(`/api/v1/langgraph/conversations/${testData.conversationId}/workflow/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          workflow_type: testData.workflowType,
          trigger_context: {
            user_message: testData.content,
            mentioned_agents: testData.initialAgentIds.split(',').map(id => id.trim()).filter(id => id.length > 0)
          }
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Workflow triggered: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Trigger workflow failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Trigger workflow error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">LangGraph Enhanced Chat API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>LangGraph Test Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Conversation Title</label>
                <Input
                  value={testData.title}
                  onChange={(e) => setTestData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter conversation title"
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

              <div>
                <label className="text-sm font-medium">Initial Agent IDs (comma-separated)</label>
                <Input
                  value={testData.initialAgentIds}
                  onChange={(e) => setTestData(prev => ({ ...prev, initialAgentIds: e.target.value }))}
                  placeholder="agent1, agent2, agent3"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Message Content (supports @mentions)</label>
                <Textarea
                  value={testData.content}
                  onChange={(e) => setTestData(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Enter message with @mentions"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Conversation Type</label>
                  <Select
                    value={testData.conversationType}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, conversationType: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="chat">Chat</SelectItem>
                      <SelectItem value="workflow">Workflow</SelectItem>
                      <SelectItem value="collaboration">Collaboration</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Message Type</label>
                  <Select
                    value={testData.messageType}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, messageType: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Text</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                      <SelectItem value="workflow">Workflow</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Agent ID (for adding)</label>
                  <Input
                    value={testData.agentId}
                    onChange={(e) => setTestData(prev => ({ ...prev, agentId: e.target.value }))}
                    placeholder="Enter agent ID"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Agent Role</label>
                  <Select
                    value={testData.role}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, role: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="member">Member</SelectItem>
                      <SelectItem value="moderator">Moderator</SelectItem>
                      <SelectItem value="assistant">Assistant</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Workflow Type</label>
                <Select
                  value={testData.workflowType}
                  onValueChange={(value) => setTestData(prev => ({ ...prev, workflowType: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="chat">Chat</SelectItem>
                    <SelectItem value="task_planning">Task Planning</SelectItem>
                    <SelectItem value="collaboration">Collaboration</SelectItem>
                    <SelectItem value="research">Research</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>LangGraph Test Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testCreateConversation} className="w-full" variant="default">
                Create LangGraph Conversation
              </Button>
              
              <Button onClick={testSendMessage} className="w-full" variant="outline">
                Send Message (with @mentions)
              </Button>
              
              <Button onClick={testGetConversation} className="w-full" variant="outline">
                Get Conversation Details
              </Button>
              
              <Button onClick={testGetMessages} className="w-full" variant="outline">
                Get Conversation Messages
              </Button>
              
              <Button onClick={testAddAgent} className="w-full" variant="outline">
                Add Agent to Conversation
              </Button>
              
              <Button onClick={testGetWorkflowStatus} className="w-full" variant="outline">
                Get Workflow Status
              </Button>
              
              <Button onClick={testTriggerWorkflow} className="w-full" variant="outline">
                Trigger Workflow Execution
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="secondary">
                Clear Logs
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Test Results & LangGraph Logs</CardTitle>
            <p className="text-sm text-gray-500">
              Tests multi-agent workflows, @mention parsing, and conversation orchestration
            </p>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No test results yet</p>
                  <p className="text-xs mt-2">
                    Start with "Create LangGraph Conversation" to test multi-agent workflows
                  </p>
                </div>
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