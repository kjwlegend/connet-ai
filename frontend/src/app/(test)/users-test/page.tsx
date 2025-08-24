'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export default function UsersTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    // User list filters
    searchQuery: '',
    limit: 20,
    skip: 0,
    sortBy: 'created_at',
    sortOrder: 'desc',
    
    // User management
    userId: '',
    fullName: 'Test User Updated',
    username: 'testuser_updated',
    email: 'testuser@example.com',
    
    // Profile data
    bio: 'This is a test user bio updated via API',
    location: 'Test City, Test Country',
    website: 'https://testuser.example.com',
    avatarUrl: '',
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testListUsers = async () => {
    try {
      addLog('Testing list users...')
      
      const params = new URLSearchParams({
        page: '1',
        size: testData.limit.toString(),
        ...(testData.searchQuery && { search: testData.searchQuery })
      })

      const response = await fetch(`/api/v1/users/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Users listed: ${JSON.stringify(data, null, 2)}`)
        
        // Auto-populate user ID from first user for testing
        if (data.items && data.items.length > 0) {
          setTestData(prev => ({ ...prev, userId: data.items[0].id }))
        }
      } else {
        const error = await response.text()
        addLog(`List users failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`List users error: ${error.message}`)
    }
  }

  const testGetUser = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing get user details...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User details retrieved: ${JSON.stringify(data, null, 2)}`)
        
        // Populate form fields with retrieved data
        setTestData(prev => ({
          ...prev,
          fullName: data.full_name || prev.fullName,
          username: data.username || prev.username,
          email: data.email || prev.email,
        }))
      } else {
        const error = await response.text()
        addLog(`Get user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get user error: ${error.message}`)
    }
  }

  const testUpdateUser = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing update user...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          full_name: testData.fullName,
          username: testData.username,
          bio: testData.bio,
          location: testData.location,
          website: testData.website,
          ...(testData.avatarUrl && { avatar_url: testData.avatarUrl })
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User updated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Update user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Update user error: ${error.message}`)
    }
  }

  const testGetUserProfile = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing get user profile...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}/profile`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User profile retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get user profile failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get user profile error: ${error.message}`)
    }
  }

  const testGetUserStats = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing get user statistics...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User stats retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get user stats failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get user stats error: ${error.message}`)
    }
  }

  const testDeactivateUser = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing deactivate user...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}/deactivate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          reason: 'API test deactivation',
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User deactivated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Deactivate user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Deactivate user error: ${error.message}`)
    }
  }

  const testReactivateUser = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing reactivate user...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}/reactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`User reactivated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Reactivate user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Reactivate user error: ${error.message}`)
    }
  }

  const testDeleteUser = async () => {
    try {
      if (!testData.userId) {
        addLog('Error: No user ID provided')
        return
      }

      addLog('Testing delete user (DANGER)...')
      
      const response = await fetch(`/api/v1/users/${testData.userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        addLog(`User deleted successfully`)
        setTestData(prev => ({ ...prev, userId: '' }))
      } else {
        const error = await response.text()
        addLog(`Delete user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Delete user error: ${error.message}`)
    }
  }

  const testGetCurrentUser = async () => {
    try {
      addLog('Testing get current user profile...')
      
      const response = await fetch('/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Current user profile: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get current user failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get current user error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">User Management API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Search & List</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Search Query</label>
                <Input
                  value={testData.searchQuery}
                  onChange={(e) => setTestData(prev => ({ ...prev, searchQuery: e.target.value }))}
                  placeholder="Search by name or email"
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

              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testListUsers} variant="default">
                  List Users
                </Button>
                <Button onClick={testGetCurrentUser} variant="outline">
                  Get Current User
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">User ID</label>
                <Input
                  value={testData.userId}
                  onChange={(e) => setTestData(prev => ({ ...prev, userId: e.target.value }))}
                  placeholder="Enter user ID for management operations"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Full Name</label>
                <Input
                  value={testData.fullName}
                  onChange={(e) => setTestData(prev => ({ ...prev, fullName: e.target.value }))}
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Username</label>
                <Input
                  value={testData.username}
                  onChange={(e) => setTestData(prev => ({ ...prev, username: e.target.value }))}
                  placeholder="Enter username"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Email</label>
                <Input
                  value={testData.email}
                  onChange={(e) => setTestData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter email"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Bio</label>
                <Input
                  value={testData.bio}
                  onChange={(e) => setTestData(prev => ({ ...prev, bio: e.target.value }))}
                  placeholder="Enter bio"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Location</label>
                  <Input
                    value={testData.location}
                    onChange={(e) => setTestData(prev => ({ ...prev, location: e.target.value }))}
                    placeholder="Enter location"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Website</label>
                  <Input
                    value={testData.website}
                    onChange={(e) => setTestData(prev => ({ ...prev, website: e.target.value }))}
                    placeholder="Enter website URL"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Avatar URL</label>
                <Input
                  value={testData.avatarUrl}
                  onChange={(e) => setTestData(prev => ({ ...prev, avatarUrl: e.target.value }))}
                  placeholder="Enter avatar image URL"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>User Operations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testGetUser} className="w-full" variant="default">
                Get User Details
              </Button>
              
              <Button onClick={testUpdateUser} className="w-full" variant="outline">
                Update User
              </Button>
              
              <Button onClick={testGetUserProfile} className="w-full" variant="outline">
                Get User Profile
              </Button>
              
              <Button onClick={testGetUserStats} className="w-full" variant="outline">
                Get User Statistics
              </Button>
              
              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testDeactivateUser} variant="destructive">
                  Deactivate User
                </Button>
                <Button onClick={testReactivateUser} variant="outline">
                  Reactivate User
                </Button>
              </div>
              
              <Button 
                onClick={testDeleteUser} 
                className="w-full" 
                variant="destructive"
                disabled={!testData.userId}
              >
                🗑️ Delete User (DANGER)
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="secondary">
                Clear Logs
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>User Management Test Results</CardTitle>
            <p className="text-sm text-gray-500">
              Tests user CRUD operations, profile management, and user statistics
            </p>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No test results yet</p>
                  <p className="text-xs mt-2">
                    Start with "List Users" to see available users and get a User ID
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