'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'

export default function SettingsTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    // Subscription settings
    planType: 'premium',
    billingCycle: 'monthly',
    
    // LLM settings
    preferredProvider: 'openai',
    defaultModel: 'gpt-4',
    maxTokens: 2000,
    temperature: 0.7,
    systemPrompt: 'You are a helpful AI assistant.',
    enableStreaming: true,
    enableFunctionCalling: false,
    
    // Prompt library
    promptTitle: 'Test Prompt',
    promptContent: 'This is a test prompt for API testing',
    promptCategory: 'general',
    isPublic: false,
    tags: 'test,api,demo',
    promptId: '',
    
    // Order history filters
    orderStatus: 'completed',
    orderLimit: 10,
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testGetSubscription = async () => {
    try {
      addLog('Testing get user subscription...')
      
      const response = await fetch('/api/v1/settings/subscription', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Subscription retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get subscription failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get subscription error: ${error.message}`)
    }
  }

  const testUpgradeSubscription = async () => {
    try {
      addLog('Testing upgrade subscription...')
      
      const response = await fetch(`/api/v1/settings/subscription/upgrade?plan_type=${testData.planType}&billing_cycle=${testData.billingCycle}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Subscription upgraded: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Upgrade subscription failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Upgrade subscription error: ${error.message}`)
    }
  }

  const testGetLLMSettings = async () => {
    try {
      addLog('Testing get LLM settings...')
      
      const response = await fetch('/api/v1/settings/llm', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`LLM settings retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get LLM settings failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get LLM settings error: ${error.message}`)
    }
  }

  const testUpdateLLMSettings = async () => {
    try {
      addLog('Testing update LLM settings...')
      
      const response = await fetch('/api/v1/settings/llm', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          preferred_provider: testData.preferredProvider,
          default_model: testData.defaultModel,
          default_max_tokens: testData.maxTokens,
          default_temperature: testData.temperature,
          system_prompt: testData.systemPrompt,
          enable_streaming: testData.enableStreaming,
          enable_function_calling: testData.enableFunctionCalling,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`LLM settings updated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Update LLM settings failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Update LLM settings error: ${error.message}`)
    }
  }

  const testGetPromptLibrary = async () => {
    try {
      addLog('Testing get prompt library...')
      
      const response = await fetch('/api/v1/settings/prompts?limit=20', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Prompt library retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get prompt library failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get prompt library error: ${error.message}`)
    }
  }

  const testCreatePrompt = async () => {
    try {
      addLog('Testing create prompt...')
      
      const response = await fetch('/api/v1/settings/prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: testData.promptTitle,
          content: testData.promptContent,
          category: testData.promptCategory,
          is_public: testData.isPublic,
          tags: testData.tags.split(',').map(tag => tag.trim()),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Prompt created: ${JSON.stringify(data, null, 2)}`)
        setTestData(prev => ({ ...prev, promptId: data.id }))
      } else {
        const error = await response.text()
        addLog(`Create prompt failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Create prompt error: ${error.message}`)
    }
  }

  const testUpdatePrompt = async () => {
    try {
      if (!testData.promptId) {
        addLog('Error: No prompt ID provided')
        return
      }

      addLog('Testing update prompt...')
      
      const response = await fetch(`/api/v1/settings/prompts/${testData.promptId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          title: testData.promptTitle + ' (Updated)',
          content: testData.promptContent + ' - Updated via API test',
          category: testData.promptCategory,
          is_public: testData.isPublic,
          tags: testData.tags.split(',').map(tag => tag.trim()),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Prompt updated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Update prompt failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Update prompt error: ${error.message}`)
    }
  }

  const testDeletePrompt = async () => {
    try {
      if (!testData.promptId) {
        addLog('Error: No prompt ID provided')
        return
      }

      addLog('Testing delete prompt...')
      
      const response = await fetch(`/api/v1/settings/prompts/${testData.promptId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        addLog(`Prompt deleted successfully`)
        setTestData(prev => ({ ...prev, promptId: '' }))
      } else {
        const error = await response.text()
        addLog(`Delete prompt failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Delete prompt error: ${error.message}`)
    }
  }

  const testGetInviteStats = async () => {
    try {
      addLog('Testing get invite statistics...')
      
      const response = await fetch('/api/v1/settings/invite-stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Invite stats retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get invite stats failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get invite stats error: ${error.message}`)
    }
  }

  const testGetOrderHistory = async () => {
    try {
      addLog('Testing get order history...')
      
      const params = new URLSearchParams({
        limit: testData.orderLimit.toString(),
        ...(testData.orderStatus && { status: testData.orderStatus })
      })

      const response = await fetch(`/api/v1/settings/orders?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Order history retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get order history failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get order history error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">User Settings API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          {/* Subscription Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Subscription Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Plan Type</label>
                  <Select
                    value={testData.planType}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, planType: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basic">Basic</SelectItem>
                      <SelectItem value="premium">Premium</SelectItem>
                      <SelectItem value="enterprise">Enterprise</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Billing Cycle</label>
                  <Select
                    value={testData.billingCycle}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, billingCycle: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="yearly">Yearly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testGetSubscription} variant="outline">
                  Get Subscription
                </Button>
                <Button onClick={testUpgradeSubscription} variant="default">
                  Upgrade Plan
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* LLM Settings */}
          <Card>
            <CardHeader>
              <CardTitle>LLM Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Provider</label>
                  <Select
                    value={testData.preferredProvider}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, preferredProvider: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="openai">OpenAI</SelectItem>
                      <SelectItem value="anthropic">Anthropic</SelectItem>
                      <SelectItem value="google">Google</SelectItem>
                      <SelectItem value="azure">Azure</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Model</label>
                  <Input
                    value={testData.defaultModel}
                    onChange={(e) => setTestData(prev => ({ ...prev, defaultModel: e.target.value }))}
                    placeholder="e.g., gpt-4"
                  />
                </div>
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

              <div>
                <label className="text-sm font-medium">System Prompt</label>
                <Textarea
                  value={testData.systemPrompt}
                  onChange={(e) => setTestData(prev => ({ ...prev, systemPrompt: e.target.value }))}
                  placeholder="System prompt"
                  rows={2}
                />
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="streaming"
                    checked={testData.enableStreaming}
                    onCheckedChange={(checked) => setTestData(prev => ({ ...prev, enableStreaming: !!checked }))}
                  />
                  <label htmlFor="streaming" className="text-sm">Enable Streaming</label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="functions"
                    checked={testData.enableFunctionCalling}
                    onCheckedChange={(checked) => setTestData(prev => ({ ...prev, enableFunctionCalling: !!checked }))}
                  />
                  <label htmlFor="functions" className="text-sm">Function Calling</label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testGetLLMSettings} variant="outline">
                  Get LLM Settings
                </Button>
                <Button onClick={testUpdateLLMSettings} variant="default">
                  Update Settings
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Prompt Library */}
          <Card>
            <CardHeader>
              <CardTitle>Prompt Library</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Prompt ID</label>
                <Input
                  value={testData.promptId}
                  onChange={(e) => setTestData(prev => ({ ...prev, promptId: e.target.value }))}
                  placeholder="Enter prompt ID for update/delete"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Title</label>
                <Input
                  value={testData.promptTitle}
                  onChange={(e) => setTestData(prev => ({ ...prev, promptTitle: e.target.value }))}
                  placeholder="Enter prompt title"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Content</label>
                <Textarea
                  value={testData.promptContent}
                  onChange={(e) => setTestData(prev => ({ ...prev, promptContent: e.target.value }))}
                  placeholder="Enter prompt content"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Category</label>
                  <Input
                    value={testData.promptCategory}
                    onChange={(e) => setTestData(prev => ({ ...prev, promptCategory: e.target.value }))}
                    placeholder="e.g., general, coding, writing"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Tags (comma-separated)</label>
                  <Input
                    value={testData.tags}
                    onChange={(e) => setTestData(prev => ({ ...prev, tags: e.target.value }))}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="public"
                  checked={testData.isPublic}
                  onCheckedChange={(checked) => setTestData(prev => ({ ...prev, isPublic: !!checked }))}
                />
                <label htmlFor="public" className="text-sm">Make Public</label>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testGetPromptLibrary} variant="outline">
                  Get Prompts
                </Button>
                <Button onClick={testCreatePrompt} variant="default">
                  Create Prompt
                </Button>
                <Button onClick={testUpdatePrompt} variant="outline">
                  Update Prompt
                </Button>
                <Button onClick={testDeletePrompt} variant="destructive">
                  Delete Prompt
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Other Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Other Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testGetInviteStats} className="w-full" variant="outline">
                Get Invite Statistics
              </Button>
              <Button onClick={testGetOrderHistory} className="w-full" variant="outline">
                Get Order History
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