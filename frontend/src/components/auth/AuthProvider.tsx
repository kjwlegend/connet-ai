'use client'

import { useEffect } from 'react'
import { useAuthSession } from '@/hooks/business/auth'
import { useAuth } from '@/store/index'
import { apiClient } from '@/services/api/client'

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { initializeAuth } = useAuthSession()
  const { auth } = useAuth()

  useEffect(() => {
    // Set up API client token getter to use current store state
    apiClient.setAuthTokenGetter(() => {
      return auth.token
    })

    // Initialize authentication on app startup
    initializeAuth()
  }, [initializeAuth, auth.token])

  return <>{children}</>
}
