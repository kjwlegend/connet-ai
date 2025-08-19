'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import useStore from '@/store'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
  redirectTo?: string
  authenticatedRedirectTo?: string
}

export function AuthGuard({
  children,
  requireAuth = true,
  redirectTo = '/login',
  authenticatedRedirectTo,
}: AuthGuardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, isLoading, initializeAuth } = useStore()

  useEffect(() => {
    // Initialize auth on component mount
    initializeAuth()
  }, [initializeAuth])

  useEffect(() => {
    console.log('AuthGuard effect:', {
      isLoading,
      requireAuth,
      isAuthenticated,
      pathname,
    })
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        // Add current path as redirect parameter
        const redirectUrl = `${redirectTo}?redirect=${encodeURIComponent(
          pathname
        )}`
        console.log('AuthGuard: Redirecting to login:', redirectUrl)
        router.push(redirectUrl)
      } else if (!requireAuth && isAuthenticated) {
        const targetUrl = authenticatedRedirectTo || '/'
        console.log(
          'AuthGuard: User authenticated on auth page, redirecting to:',
          targetUrl
        )
        try {
          // Try Next.js router first
          router.push(targetUrl)
          console.log('AuthGuard: router.push called successfully')

          // Fallback to window.location as backup
          setTimeout(() => {
            if (window.location.pathname !== targetUrl.split('?')[0]) {
              console.log('AuthGuard: Fallback to window.location.href')
              window.location.href = targetUrl
            }
          }, 500)
        } catch (error) {
          console.error('AuthGuard: router.push failed:', error)
          // Force redirect with window.location
          window.location.href = targetUrl
        }
      }
    }
  }, [
    isAuthenticated,
    isLoading,
    requireAuth,
    redirectTo,
    authenticatedRedirectTo,
    router,
    pathname,
  ])

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // If requireAuth is true and user is not authenticated, don't render children
  if (requireAuth && !isAuthenticated) {
    return null
  }

  // If requireAuth is false and user is authenticated, don't render children
  if (!requireAuth && isAuthenticated) {
    return null
  }

  return <>{children}</>
}

// Higher-order component for protecting pages
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  options: { requireAuth?: boolean; redirectTo?: string } = {}
) {
  return function AuthGuardedComponent(props: P) {
    return (
      <AuthGuard {...options}>
        <Component {...props} />
      </AuthGuard>
    )
  }
}

// Hook for checking auth status in components
export function useAuthGuard() {
  const { isAuthenticated, isLoading, user } = useStore()

  return {
    isAuthenticated,
    isLoading,
    user,
    requireAuth: (redirectTo = '/login') => {
      const router = useRouter()

      useEffect(() => {
        if (!isLoading && !isAuthenticated) {
          router.push(redirectTo)
        }
      }, [isAuthenticated, isLoading, redirectTo, router])
    },
  }
}
