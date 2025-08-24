/**
 * 路由守卫组件
 * 基于统一的路由配置提供页面访问控制
 */

'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/store'
import { canAccessRoute } from '@/lib/auth/route-config'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

interface RouteGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function RouteGuard({ children, fallback }: RouteGuardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { auth, authUI } = useAuth()

  useEffect(() => {
    // Skip redirect during initialization
    if (authUI.isInitializing) return

    const accessCheck = canAccessRoute(pathname, auth.isAuthenticated)
    
    if (accessCheck.shouldRedirect && accessCheck.redirectTo) {
      const redirectUrl = new URL(accessCheck.redirectTo, window.location.origin)
      
      // Add redirect parameter for login routes
      if (!auth.isAuthenticated && accessCheck.redirectTo.includes('/login')) {
        redirectUrl.searchParams.set('redirect', pathname)
      }
      
      console.log('RouteGuard: Redirecting to', redirectUrl.toString())
      router.push(redirectUrl.pathname + redirectUrl.search)
    }
  }, [auth.isAuthenticated, authUI.isInitializing, pathname, router])

  // Show loading during initialization
  if (authUI.isInitializing) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner />
        </div>
      )
    )
  }

  // Check access permission
  const accessCheck = canAccessRoute(pathname, auth.isAuthenticated)
  
  if (!accessCheck.canAccess) {
    // Don't render children if access is denied
    return null
  }

  return <>{children}</>
}

/**
 * Layout守卫 - 用于保护整个layout
 */
export function LayoutGuard({ children }: { children: React.ReactNode }) {
  return (
    <RouteGuard
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <div className="flex flex-col items-center space-y-4">
            <LoadingSpinner />
            <p className="text-sm text-muted-foreground">Loading...</p>
          </div>
        </div>
      }
    >
      {children}
    </RouteGuard>
  )
}

/**
 * 页面守卫 - 用于保护特定页面
 */
export function PageGuard({ 
  children, 
  requireAuth = true,
  fallback
}: { 
  children: React.ReactNode
  requireAuth?: boolean
  fallback?: React.ReactNode
}) {
  const { auth, authUI } = useAuth()
  
  if (authUI.isInitializing) {
    return fallback || <LoadingSpinner />
  }
  
  if (requireAuth && !auth.isAuthenticated) {
    return null
  }
  
  if (!requireAuth && auth.isAuthenticated) {
    return null
  }
  
  return <>{children}</>
}

/**
 * HOC for protecting components
 */
export function withRouteGuard<P extends object>(
  Component: React.ComponentType<P>
) {
  return function GuardedComponent(props: P) {
    return (
      <RouteGuard>
        <Component {...props} />
      </RouteGuard>
    )
  }
}

/**
 * Hook for checking route access
 */
export function useRouteGuard() {
  const pathname = usePathname()
  const { auth, authUI } = useAuth()
  
  const accessCheck = canAccessRoute(pathname, auth.isAuthenticated)
  
  return {
    canAccess: accessCheck.canAccess,
    shouldRedirect: accessCheck.shouldRedirect,
    redirectTo: accessCheck.redirectTo,
    isLoading: authUI.isInitializing,
    isAuthenticated: auth.isAuthenticated,
    user: auth.user,
  }
}