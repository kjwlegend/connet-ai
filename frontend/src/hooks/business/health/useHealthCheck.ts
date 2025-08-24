/**
 * Health Check Business Hook
 * 处理健康检查相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  service: string
  version: string
  environment: string
  timestamp: string
  uptime?: string
}

interface DetailedHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  service: string
  version: string
  environment: string
  timestamp: string
  uptime?: string
  checks?: {
    [serviceName: string]: {
      status: 'healthy' | 'degraded' | 'unhealthy'
      response_time?: number
      error?: string
      details?: any
    }
  }
  database?: {
    status: 'healthy' | 'degraded' | 'unhealthy'
    response_time?: number
    error?: string
  }
  redis?: {
    status: 'healthy' | 'degraded' | 'unhealthy'
    response_time?: number
    error?: string
  }
  supabase?: {
    status: 'healthy' | 'degraded' | 'unhealthy'
    response_time?: number
    error?: string
  }
}

export const useHealthCheck = () => {
  const getBasicHealth = useCallback(async (): Promise<HealthResponse | null> => {
    try {
      const response = await fetch('/api/v1/health/')

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Basic health check failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      if (data.status !== 'healthy') {
        toast({
          title: "Service status warning",
          description: `Service status is ${data.status}`,
          variant: "destructive",
        })
      }

      return data
    } catch (error: any) {
      console.error('Basic health check failed:', error)
      toast({
        title: "Health check failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getDetailedHealth = useCallback(async (): Promise<DetailedHealthResponse | null> => {
    try {
      const response = await fetch('/api/v1/health/detailed')

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Detailed health check failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      // Check for any degraded services
      const hasIssues = data.status !== 'healthy' || 
                       Object.values(data.checks || {}).some((check: any) => check.status !== 'healthy') ||
                       data.database?.status !== 'healthy' ||
                       data.redis?.status !== 'healthy' ||
                       data.supabase?.status !== 'healthy'

      if (hasIssues) {
        toast({
          title: "Service health issues detected",
          description: "Some services are experiencing issues",
          variant: "destructive",
        })
      }

      return data
    } catch (error: any) {
      console.error('Detailed health check failed:', error)
      toast({
        title: "Detailed health check failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const checkServiceHealth = useCallback(async (
    silent: boolean = true
  ): Promise<boolean> => {
    try {
      const health = await getBasicHealth()
      const isHealthy = health?.status === 'healthy'
      
      if (!silent && !isHealthy) {
        toast({
          title: "Service health check",
          description: `Service is ${health?.status || 'unavailable'}`,
          variant: isHealthy ? "default" : "destructive",
        })
      }

      return isHealthy
    } catch (error: any) {
      if (!silent) {
        toast({
          title: "Service unavailable",
          description: "Unable to check service health",
          variant: "destructive",
        })
      }
      return false
    }
  }, [getBasicHealth])

  return {
    getBasicHealth,
    getDetailedHealth,
    checkServiceHealth,
  }
}