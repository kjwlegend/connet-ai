'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/store'

export default function AuthTestPage() {
  const auth = useAuth()
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    email: 'test@example.com',
    password: 'testpassword123',
    fullName: 'Test User',
    token: '',
    refreshToken: '',
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testLogin = async () => {
    try {
      addLog('Testing login with authSlice...')
      await auth.loginWithCredentials(testData.email, testData.password, true)
      addLog(`Login success: ${auth.auth.user?.email}, token: ${auth.auth.token?.substring(0, 20)}...`)
      setTestData(prev => ({ ...prev, token: auth.auth.token || '', refreshToken: auth.auth.refreshToken || '' }))
    } catch (error: any) {
      addLog(`Login failed: ${error.message}`)
    }
  }

  const testRegister = async () => {
    try {
      addLog('Testing register with authSlice...')
      const result = await auth.registerWithCredentials({
        email: testData.email,
        password: testData.password,
        full_name: testData.fullName
      })
      addLog(`Register success: ${result.user.email}`)
    } catch (error: any) {
      addLog(`Register failed: ${error.message}`)
    }
  }

  const testGetCurrentUser = async () => {
    try {
      addLog('Testing get current user with authSlice...')
      await auth.getCurrentUser()
      addLog(`Get current user success: ${auth.auth.user?.email} (${auth.auth.user?.full_name})`)
    } catch (error: any) {
      addLog(`Get current user failed: ${error.message}`)
    }
  }

  const testRefreshToken = async () => {
    try {
      addLog('Testing refresh token with authSlice...')
      if (!auth.auth.refreshToken) {
        addLog('No refresh token available. Login first.')
        return
      }
      const success = await auth.refreshAuthToken()
      if (success) {
        addLog(`Refresh token success: new token ${auth.auth.token?.substring(0, 20)}...`)
        setTestData(prev => ({ ...prev, token: auth.auth.token || '', refreshToken: auth.auth.refreshToken || '' }))
      } else {
        addLog('Refresh token failed')
      }
    } catch (error: any) {
      addLog(`Refresh token failed: ${error.message}`)
    }
  }

  const testVerifyToken = async () => {
    try {
      addLog('Testing verify token with authSlice...')
      if (!auth.auth.token) {
        addLog('No token available. Login first.')
        return
      }
      const isValid = await auth.validateToken()
      addLog(`Verify token success: valid=${isValid}`)
    } catch (error: any) {
      addLog(`Verify token failed: ${error.message}`)
    }
  }

  const testPasswordReset = async () => {
    try {
      addLog('Testing password reset (direct AuthService call)...')
      // Note: Password reset doesn't require authentication, so direct call is fine
      const { AuthService } = await import('@/services/api')
      const result = await AuthService.requestPasswordReset({ email: testData.email })
      addLog(`Password reset success: ${result.message}`)
    } catch (error: any) {
      addLog(`Password reset failed: ${error.message}`)
    }
  }

  const testVerifyEmail = async () => {
    try {
      addLog('Testing verify email (direct AuthService call)...')
      if (!testData.token) {
        addLog('No token provided. Enter a verification token first.')
        return
      }
      // Note: Email verification doesn't require auth headers, so direct call is fine
      const { AuthService } = await import('@/services/api')
      const result = await AuthService.verifyEmail(testData.token, testData.email)
      addLog(`Verify email success: ${result.message}`)
    } catch (error: any) {
      addLog(`Verify email failed: ${error.message}`)
    }
  }

  const testGetOAuthUrl = async () => {
    try {
      addLog('Testing get OAuth URL with authSlice...')
      const result = await auth.getOAuthUrl('google', 'http://localhost:3000/auth/callback')
      addLog(`Get OAuth URL success: ${result.url}`)
    } catch (error: any) {
      addLog(`Get OAuth URL failed: ${error.message}`)
    }
  }

  const testLogout = async () => {
    try {
      addLog('Testing logout with authSlice...')
      await auth.logout()
      addLog('Logout success')
      setTestData(prev => ({ ...prev, token: '', refreshToken: '' }))
    } catch (error: any) {
      addLog(`Logout failed: ${error.message}`)
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">Auth API Test Page</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <Input
                value={testData.email}
                onChange={(e) => setTestData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="Enter email"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <Input
                type="password"
                value={testData.password}
                onChange={(e) => setTestData(prev => ({ ...prev, password: e.target.value }))}
                placeholder="Enter password"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Full Name</label>
              <Input
                value={testData.fullName}
                onChange={(e) => setTestData(prev => ({ ...prev, fullName: e.target.value }))}
                placeholder="Enter full name for registration"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Token (for verify)</label>
              <Input
                value={testData.token}
                onChange={(e) => setTestData(prev => ({ ...prev, token: e.target.value }))}
                placeholder="Enter token to verify"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button onClick={testLogin} size="sm">Login</Button>
              <Button onClick={testRegister} size="sm" variant="outline">Register</Button>
              <Button onClick={testGetCurrentUser} size="sm">Get User</Button>
              <Button onClick={testRefreshToken} size="sm">Refresh Token</Button>
              <Button onClick={testVerifyToken} size="sm">Verify Token</Button>
              <Button onClick={testPasswordReset} size="sm">Password Reset</Button>
              <Button onClick={testVerifyEmail} size="sm">Verify Email</Button>
              <Button onClick={testGetOAuthUrl} size="sm">OAuth URL</Button>
              <Button onClick={testLogout} size="sm">Logout</Button>
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-sm">
            <div>
              <strong>Test Email:</strong> {testData.email}
            </div>
            <div>
              <strong>Authenticated:</strong> {auth.auth.isAuthenticated ? '✅ Yes' : '❌ No'}
            </div>
            <div>
              <strong>Current User:</strong> {auth.auth.user?.email || 'None'}
            </div>
            <div>
              <strong>User Name:</strong> {auth.auth.user?.full_name || 'None'}
            </div>
            <div>
              <strong>Has Token:</strong> {auth.auth.token ? '✅ Yes' : '❌ No'}
            </div>
            <div>
              <strong>Has Refresh Token:</strong> {auth.auth.refreshToken ? '✅ Yes' : '❌ No'}
            </div>
            <div>
              <strong>Loading:</strong> {auth.ui.isLoading ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Initializing:</strong> {auth.ui.isInitializing ? '⏳ Yes' : '✅ No'}
            </div>
            <div>
              <strong>Current Error:</strong> {auth.error.current || '✅ None'}
            </div>
            <div>
              <strong>Error History:</strong> {auth.error.history.length} errors
            </div>
            <div>
              <strong>Session Started:</strong> {auth.auth.sessionStarted ? new Date(auth.auth.sessionStarted).toLocaleTimeString() : 'None'}
            </div>
            <div>
              <strong>Last Activity:</strong> {auth.auth.lastActivity ? new Date(auth.auth.lastActivity).toLocaleTimeString() : 'None'}
            </div>
            <div className="md:col-span-2">
              <strong>Token Preview:</strong> {auth.auth.token ? `${auth.auth.token.substring(0, 30)}...` : 'None'}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}