import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define protected and public routes
const protectedRoutes = [
  '/dashboard',
  '/chat',
  '/contacts',
  '/files',
  '/timeline',
  '/plugins',
  '/settings',
]
const authRoutes = ['/login', '/register']
const publicRoutes = ['/']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies or headers
  const token =
    request.cookies.get('auth_token')?.value ||
    request.headers.get('authorization')?.replace('Bearer ', '')

  const isAuthenticated = !!token && token !== 'undefined'

  // Check if the current path is protected
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route))
  const isPublicRoute = publicRoutes.includes(pathname)

  // Redirect unauthenticated users trying to access protected routes
  if (isProtectedRoute && !isAuthenticated) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Redirect authenticated users away from auth pages
  // if (isAuthRoute && isAuthenticated) {
  //   const dashboardUrl = new URL('/dashboard', request.url)
  //   return NextResponse.redirect(dashboardUrl)
  // }

  // Allow authenticated users to access home page, redirect unauthenticated to login
  if (pathname === '/' && !isAuthenticated) {
    return NextResponse.redirect(new URL('/login', request.url))
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
