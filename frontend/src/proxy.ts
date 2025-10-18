import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { canAccessRoute } from '@/lib/auth/route-config'

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from various sources (适配新的分类存储系统)
  const getTokenFromStorage = () => {
    // Try categorized storage keys first
    const storageCategories = ['permanent', 'cache', 'session', 'temporary']
    for (const category of storageCategories) {
      const categoryKey = `${category}:connet-ai-store`
      const cookieValue = request.cookies.get(categoryKey)?.value
      if (cookieValue) {
        try {
          const storeData = JSON.parse(cookieValue)
          if (storeData?.auth?.token || storeData?.state?.auth?.token) {
            return storeData.auth?.token || storeData.state.auth.token
          }
        } catch {
          // Continue to next method
        }
      }
    }
    
    // Fallback methods
    return (
      request.cookies.get('auth_token')?.value ||
      request.cookies.get('connet-ai-store')?.value ||
      request.headers.get('authorization')?.replace('Bearer ', '')
    )
  }

  const token = getTokenFromStorage()
  const isAuthenticated = !!token && token !== 'undefined' && token !== 'null'

  // Use route config to determine access
  const accessCheck = canAccessRoute(pathname, isAuthenticated)

  if (accessCheck.shouldRedirect && accessCheck.redirectTo) {
    const redirectUrl = new URL(accessCheck.redirectTo, request.url)
    
    // Add redirect parameter for protected routes
    if (!isAuthenticated && accessCheck.redirectTo.includes('/login')) {
      redirectUrl.searchParams.set('redirect', pathname)
    }
    
    return NextResponse.redirect(redirectUrl)
  }

  // Special handling for root path
  if (pathname === '/') {
    if (isAuthenticated) {
      return NextResponse.redirect(new URL('/chat', request.url))
    } else {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public directory)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
