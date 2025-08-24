'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAgents } from '@/store'
import { useAgentsQuery, useAgentsMutation, useAgentVersions } from '@/hooks/business/agents'
import type { AIAgentType } from '@/services/api'

export default function AgentTestPage() {
  const agents = useAgents()
  const { listAgents, getAgent, searchAgents } = useAgentsQuery()
  const { createAgent, updateAgent, deleteAgent, deployAgent } = useAgentsMutation()
  const { getAgentVersions } = useAgentVersions()
  
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    name: 'test_agent',
    displayName: 'Test Agent',
    description: 'A test AI agent',
    systemPrompt: 'You are a helpful AI assistant.',
    agentType: 'custom' as AIAgentType,
    conversationStyle: 'professional',
    maxContextLength: 4000,
    timeoutSeconds: 30,
    agentId: '',
    enabled_tools: ['search', 'calculator'],
    capabilities: ['text_generation', 'conversation'],
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testCreateAgent = async () => {
    try {
      addLog('Testing create agent with new business hooks...')
      const agentData = {
        name: testData.name,
        display_name: testData.displayName,
        description: testData.description,
        agent_type: testData.agentType,
        system_prompt: testData.systemPrompt,
        personality_config: {
          role: 'assistant',
          expertise: ['general'],
          communication_style: testData.conversationStyle,
          language_traits: [],
          emotional_tendency: 'neutral',
          creativity_level: 0.7,
          formality_level: 0.5,
          empathy_level: 0.6,
          curiosity_level: 0.5,
          behavior_rules: [],
          goals: [],
        },
        model_preferences: {
          default_model: 'gpt-3.5-turbo',
          fallback_models: [],
          temperature: 0.7,
          top_p: 1.0,
          frequency_penalty: 0.0,
          presence_penalty: 0.0,
        },
        enabled_tools: testData.enabled_tools,
        behavior_rules: [],
        conversation_style: testData.conversationStyle,
        capabilities: testData.capabilities,
        max_context_length: testData.maxContextLength,
        timeout_seconds: testData.timeoutSeconds,
        required_permissions: [],
      }

      const result = await createAgent(agentData)
      addLog(`✅ Create agent success: ${result.id}`)
      addLog(`   Display name: ${result.display_name}`)
      addLog(`   Status: ${result.status}`)
      setTestData(prev => ({ ...prev, agentId: result.id }))
    } catch (error: any) {
      addLog(`❌ Create agent failed: ${error.message}`)
    }
  }

  const testListAgents = async () => {
    try {
      addLog('Testing list agents with new business hooks...')
      await listAgents({ page: 1, size: 10 })
      addLog(`✅ List agents success: Found ${agents.agents?.length ?? 0} agents`)
      addLog(`   Total: ${agents.pagination.total}`)
      agents.agents?.forEach((agent, index) => {
        addLog(`  ${index + 1}. ${agent.display_name} (${agent.id})`)
      })
    } catch (error: any) {
      addLog(`❌ List agents failed: ${error.message}`)
    }
  }

  const testGetAgent = async () => {
    try {
      if (!testData.agentId) {
        addLog('❌ No agent ID. Create an agent first.')
        return
      }
      addLog(`Testing get agent with new business hooks: ${testData.agentId}`)
      const result = await getAgent(testData.agentId)
      addLog(`✅ Get agent success: ${result.display_name}`)
      addLog(`   Status: ${result.status}, Type: ${result.agent_type}`)
      addLog(`   Usage count: ${result.usage_count}`)
      addLog(`   Success rate: ${result.success_rate}`)
    } catch (error: any) {
      addLog(`❌ Get agent failed: ${error.message}`)
    }
  }

  const testUpdateAgent = async () => {
    try {
      if (!testData.agentId) {
        addLog('❌ No agent ID. Create an agent first.')
        return
      }
      addLog(`Testing update agent with new business hooks: ${testData.agentId}`)
      const updateData = {
        display_name: `${testData.displayName} (Updated)`,
        description: `${testData.description} - Updated at ${new Date().toLocaleTimeString()}`,
      }

      const result = await updateAgent(testData.agentId, updateData)
      addLog(`✅ Update agent success: ${result.display_name}`)
      addLog(`   Description: ${result.description}`)
    } catch (error: any) {
      addLog(`❌ Update agent failed: ${error.message}`)
    }
  }

  const testDeployAgent = async () => {
    try {
      if (!testData.agentId) {
        addLog('❌ No agent ID. Create an agent first.')
        return
      }
      addLog(`Testing deploy agent with new business hooks: ${testData.agentId}`)
      const result = await deployAgent(testData.agentId)
      addLog(`✅ Deploy agent success: ${result.message}`)
      addLog(`   Deployment status: ${result.deployment_status || 'deployed'}`)
    } catch (error: any) {
      addLog(`❌ Deploy agent failed: ${error.message}`)
    }
  }

  const testGetAgentVersions = async () => {
    try {
      if (!testData.agentId) {
        addLog('❌ No agent ID. Create an agent first.')
        return
      }
      addLog(`Testing get agent versions with new business hooks: ${testData.agentId}`)
      await getAgentVersions(testData.agentId)
      addLog(`✅ Get agent versions success: Found ${agents.agentVersions?.length ?? 0} versions`)
      agents.agentVersions?.forEach((version, index) => {
        addLog(`  ${index + 1}. Version ${version.version} - ${version.is_current ? 'Current' : 'Historical'}`)
      })
    } catch (error: any) {
      addLog(`❌ Get agent versions failed: ${error.message}`)
    }
  }

  const testDeleteAgent = async () => {
    try {
      if (!testData.agentId) {
        addLog('❌ No agent ID. Create an agent first.')
        return
      }
      addLog(`Testing delete agent with new business hooks: ${testData.agentId}`)
      await deleteAgent(testData.agentId)
      addLog(`✅ Delete agent success`)
      setTestData(prev => ({ ...prev, agentId: '' }))
    } catch (error: any) {
      addLog(`❌ Delete agent failed: ${error.message}`)
    }
  }

  const testSearchAgents = async () => {
    try {
      const searchQuery = testData.displayName.toLowerCase()
      addLog(`Testing search agents with new business hooks: "${searchQuery}"`)
      await searchAgents(searchQuery)
      addLog(`✅ Search agents success: Found ${agents.agents?.length ?? 0} results`)
      agents.agents?.forEach((agent, index) => {
        addLog(`  ${index + 1}. ${agent.display_name} (${agent.id})`)
      })
    } catch (error: any) {
      addLog(`❌ Search agents failed: ${error.message}`)
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">AI Agent API Test Page (with New Business Hooks)</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Agent Name</label>
                <Input
                  value={testData.name}
                  onChange={(e) => setTestData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Agent name (unique)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Display Name</label>
                <Input
                  value={testData.displayName}
                  onChange={(e) => setTestData(prev => ({ ...prev, displayName: e.target.value }))}
                  placeholder="Display name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <Input
                value={testData.description}
                onChange={(e) => setTestData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Agent description"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">System Prompt</label>
              <Textarea
                value={testData.systemPrompt}
                onChange={(e) => setTestData(prev => ({ ...prev, systemPrompt: e.target.value }))}
                placeholder="System prompt for the agent"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Agent Type</label>
                <Select
                  value={testData.agentType}
                  onValueChange={(value) => setTestData(prev => ({ ...prev, agentType: value as AIAgentType }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="system">System</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                    <SelectItem value="specialized">Specialized</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Conversation Style</label>
                <Select
                  value={testData.conversationStyle}
                  onValueChange={(value) => setTestData(prev => ({ ...prev, conversationStyle: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="formal">Formal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Max Context Length</label>
                <Input
                  type="number"
                  value={testData.maxContextLength}
                  onChange={(e) => setTestData(prev => ({ ...prev, maxContextLength: parseInt(e.target.value) || 4000 }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Timeout (seconds)</label>
                <Input
                  type="number"
                  value={testData.timeoutSeconds}
                  onChange={(e) => setTestData(prev => ({ ...prev, timeoutSeconds: parseInt(e.target.value) || 30 }))}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Current Agent ID</label>
              <Input
                value={testData.agentId}
                onChange={(e) => setTestData(prev => ({ ...prev, agentId: e.target.value }))}
                placeholder="Agent ID for get/update/delete operations"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button 
                onClick={testCreateAgent} 
                size="sm"
                disabled={agents.ui?.isCreating}
              >
                {agents.ui?.isCreating ? 'Creating...' : 'Create Agent'}
              </Button>
              <Button 
                onClick={testListAgents} 
                size="sm" 
                variant="outline"
                disabled={agents.ui.isLoading}
              >
                {agents.ui.isLoading ? 'Loading...' : 'List Agents'}
              </Button>
              <Button 
                onClick={testGetAgent} 
                size="sm"
                disabled={agents.ui.isLoading}
              >
                Get Agent
              </Button>
              <Button 
                onClick={testUpdateAgent} 
                size="sm"
                disabled={agents.ui.isUpdating}
              >
                {agents.ui.isUpdating ? 'Updating...' : 'Update Agent'}
              </Button>
              <Button 
                onClick={testDeployAgent} 
                size="sm"
                disabled={agents.ui.isDeploying}
              >
                {agents.ui.isDeploying ? 'Deploying...' : 'Deploy Agent'}
              </Button>
              <Button 
                onClick={testGetAgentVersions} 
                size="sm"
                disabled={agents.ui.isLoading}
              >
                Get Versions
              </Button>
              <Button 
                onClick={testSearchAgents} 
                size="sm"
                disabled={agents.ui.isLoading}
              >
                Search Agents
              </Button>
              <Button 
                onClick={testDeleteAgent} 
                size="sm" 
                variant="destructive"
                disabled={agents.ui.isDeleting}
              >
                {agents.ui.isDeleting ? 'Deleting...' : 'Delete Agent'}
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
              <strong>Agent Name:</strong> {testData.name}
            </div>
            <div>
              <strong>Display Name:</strong> {testData.displayName}
            </div>
            <div>
              <strong>Agent Type:</strong> {testData.agentType}
            </div>
            <div>
              <strong>Current Agent ID:</strong> {testData.agentId || 'None'}
            </div>
            <div>
              <strong>Max Context:</strong> {testData.maxContextLength}
            </div>
            <div>
              <strong>Timeout:</strong> {testData.timeoutSeconds}s
            </div>
            <div>
              <strong>Store Loading:</strong> {agents.ui.isLoading ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Store Creating:</strong> {agents.ui.isCreating ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Store Error:</strong> {agents.error.current || '✅ None'}
            </div>
            <div>
              <strong>Agents Count:</strong> {agents.agents?.length ?? 0}
            </div>
            <div>
              <strong>Versions Count:</strong> {agents.agentVersions?.length ?? 0}
            </div>
            <div>
              <strong>Current Agent:</strong> {agents.currentAgent?.display_name || 'None'}
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <strong>System Prompt:</strong> {testData.systemPrompt.substring(0, 100)}{testData.systemPrompt.length > 100 ? '...' : ''}
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <strong>Enabled Tools:</strong> {testData.enabled_tools.join(', ')}
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <strong>Capabilities:</strong> {testData.capabilities.join(', ')}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}