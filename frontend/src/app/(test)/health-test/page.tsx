'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function HealthTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const [detailedHealth, setDetailedHealth] = useState<any>(null)

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testBasicHealth = async () => {
    try {
      addLog('Testing basic health check...')
      
      const response = await fetch('/api/v1/health/')

      if (response.ok) {
        const data = await response.json()
        setHealthStatus(data)
        addLog(`Basic health check success: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Basic health check failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Basic health check error: ${error.message}`)
    }
  }

  const testDetailedHealth = async () => {
    try {
      addLog('Testing detailed health check...')
      
      const response = await fetch('/api/v1/health/detailed')

      if (response.ok) {
        const data = await response.json()
        setDetailedHealth(data)
        addLog(`Detailed health check success: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Detailed health check failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Detailed health check error: ${error.message}`)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'bg-green-500'
      case 'degraded':
        return 'bg-yellow-500'
      case 'unhealthy':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const renderHealthInfo = (data: any) => {
    if (!data) return null

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Status</label>
            <div className="flex items-center space-x-2">
              <Badge className={getStatusColor(data.status)}>
                {data.status}
              </Badge>
            </div>
          </div>

          {data.service && (
            <div>
              <label className="text-sm font-medium text-gray-500">Service</label>
              <p className="text-sm">{data.service}</p>
            </div>
          )}

          {data.version && (
            <div>
              <label className="text-sm font-medium text-gray-500">Version</label>
              <p className="text-sm">{data.version}</p>
            </div>
          )}

          {data.environment && (
            <div>
              <label className="text-sm font-medium text-gray-500">Environment</label>
              <p className="text-sm">{data.environment}</p>
            </div>
          )}

          {data.timestamp && (
            <div>
              <label className="text-sm font-medium text-gray-500">Timestamp</label>
              <p className="text-sm">{new Date(data.timestamp).toLocaleString()}</p>
            </div>
          )}

          {data.uptime && (
            <div>
              <label className="text-sm font-medium text-gray-500">Uptime</label>
              <p className="text-sm">{data.uptime}</p>
            </div>
          )}
        </div>

        {data.checks && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Service Checks</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {Object.entries(data.checks).map(([service, check]: [string, any]) => (
                <div key={service} className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm font-medium">{service}</span>
                  <Badge className={getStatusColor(check.status)}>
                    {check.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.database && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Database</h4>
            <div className="p-2 border rounded space-y-1">
              <div className="flex justify-between">
                <span className="text-xs">Status:</span>
                <Badge className={getStatusColor(data.database.status)}>
                  {data.database.status}
                </Badge>
              </div>
              {data.database.response_time && (
                <div className="flex justify-between">
                  <span className="text-xs">Response Time:</span>
                  <span className="text-xs">{data.database.response_time}ms</span>
                </div>
              )}
            </div>
          </div>
        )}

        {data.redis && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Redis Cache</h4>
            <div className="p-2 border rounded space-y-1">
              <div className="flex justify-between">
                <span className="text-xs">Status:</span>
                <Badge className={getStatusColor(data.redis.status)}>
                  {data.redis.status}
                </Badge>
              </div>
              {data.redis.response_time && (
                <div className="flex justify-between">
                  <span className="text-xs">Response Time:</span>
                  <span className="text-xs">{data.redis.response_time}ms</span>
                </div>
              )}
            </div>
          </div>
        )}

        {data.supabase && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Supabase</h4>
            <div className="p-2 border rounded space-y-1">
              <div className="flex justify-between">
                <span className="text-xs">Status:</span>
                <Badge className={getStatusColor(data.supabase.status)}>
                  {data.supabase.status}
                </Badge>
              </div>
              {data.supabase.response_time && (
                <div className="flex justify-between">
                  <span className="text-xs">Response Time:</span>
                  <span className="text-xs">{data.supabase.response_time}ms</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Health Check API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Health Check Tests</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testBasicHealth} className="w-full" variant="default">
                Basic Health Check
              </Button>
              
              <Button onClick={testDetailedHealth} className="w-full" variant="outline">
                Detailed Health Check
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="secondary">
                Clear Logs
              </Button>
            </CardContent>
          </Card>

          {healthStatus && (
            <Card>
              <CardHeader>
                <CardTitle>Basic Health Status</CardTitle>
              </CardHeader>
              <CardContent>
                {renderHealthInfo(healthStatus)}
              </CardContent>
            </Card>
          )}

          {detailedHealth && (
            <Card>
              <CardHeader>
                <CardTitle>Detailed Health Status</CardTitle>
              </CardHeader>
              <CardContent>
                {renderHealthInfo(detailedHealth)}
              </CardContent>
            </Card>
          )}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Test Results & Logs</CardTitle>
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