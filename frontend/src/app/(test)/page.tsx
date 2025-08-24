'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const testPages = [
  {
    path: '/agent-test',
    name: 'Agent Test',
    description: 'Test AI agent management APIs including creation, deployment, and version management',
    endpoints: ['POST /agents', 'GET /agents', 'PUT /agents/{id}', 'DELETE /agents/{id}'],
    status: 'ready',
    color: 'bg-green-500'
  },
  {
    path: '/auth-test',
    name: 'Authentication Test', 
    description: 'Test user authentication, registration, and session management',
    endpoints: ['POST /auth/register', 'POST /auth/login', 'POST /auth/refresh'],
    status: 'ready',
    color: 'bg-green-500'
  },
  {
    path: '/contacts-test',
    name: 'Contacts Test',
    description: 'Test contact/agent relationship management and social features',
    endpoints: ['GET /contacts', 'POST /contacts', 'PUT /contacts/{id}', 'DELETE /contacts/{id}'],
    status: 'ready', 
    color: 'bg-green-500'
  },
  {
    path: '/chat-test',
    name: 'AI Chat Test',
    description: 'Test AI chat functionality, memory management, and conversation summaries',
    endpoints: ['POST /chat', 'POST /chat/memory', 'GET /chat/memory', 'GET /chat/summary'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/conversations-test',
    name: 'Conversations Test',
    description: 'Test conversation management, participants, pinning, and export functionality',
    endpoints: ['GET /conversations', 'POST /conversations', 'PATCH /conversations/{id}'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/health-test',
    name: 'Health Check Test',
    description: 'Test system health monitoring and service status endpoints',
    endpoints: ['GET /health', 'GET /health/detailed'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/langgraph-test',
    name: 'LangGraph Test',
    description: 'Test multi-agent workflows, @mention parsing, and conversation orchestration',
    endpoints: ['POST /langgraph/conversations', 'POST /langgraph/.../messages'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/settings-test', 
    name: 'Settings Test',
    description: 'Test user settings, LLM configuration, prompt library, and subscription management',
    endpoints: ['GET /settings/subscription', 'PUT /settings/llm', 'POST /settings/prompts'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/timeline-test',
    name: 'Timeline Test', 
    description: 'Test social timeline features including posts, comments, and likes',
    endpoints: ['GET /timeline/posts', 'POST /timeline/posts', 'POST /.../comments'],
    status: 'new',
    color: 'bg-blue-500'
  },
  {
    path: '/users-test',
    name: 'Users Test',
    description: 'Test user management, profile updates, and user statistics',
    endpoints: ['GET /users', 'GET /users/{id}', 'PUT /users/{id}', 'DELETE /users/{id}'],
    status: 'new',
    color: 'bg-blue-500'
  }
]

export default function TestIndexPage() {
  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">API Integration Test Suite</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Demo test pages for all BFF API endpoints. Use these pages to test frontend-backend integration 
          before implementing actual features.
        </p>
        
        <div className="flex justify-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Existing Pages</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>New Pages</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {testPages.map((page) => (
          <Card key={page.path} className="hover:shadow-lg transition-shadow">
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{page.name}</CardTitle>
                <Badge 
                  className={`${page.color} text-white`}
                  variant="secondary"
                >
                  {page.status}
                </Badge>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {page.description}
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">API Endpoints:</h4>
                <div className="space-y-1">
                  {page.endpoints.map((endpoint, index) => (
                    <div key={index} className="text-xs font-mono bg-gray-100 dark:bg-gray-800 p-1 rounded">
                      {endpoint}
                    </div>
                  ))}
                </div>
              </div>
              
              <Link href={page.path}>
                <Button className="w-full" variant="outline">
                  Open Test Page
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Testing Instructions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div>
            <h3 className="font-medium mb-2">Prerequisites:</h3>
            <ul className="space-y-1 text-gray-600">
              <li>• Backend BFF service running on localhost:8000</li>
              <li>• Valid authentication token (use Auth Test first)</li>
              <li>• Database and Redis services available</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium mb-2">Testing Flow:</h3>
            <ol className="space-y-1 text-gray-600">
              <li>1. Start with Health Check to verify backend</li>
              <li>2. Test Authentication to get auth token</li>
              <li>3. Test other endpoints in any order</li>
              <li>4. Monitor logs in browser console</li>
            </ol>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>Note:</strong> These are demo pages for testing API connectivity. 
            The actual UI implementation will be different and integrated with the main application.
          </p>
        </div>
      </div>
    </div>
  )
}