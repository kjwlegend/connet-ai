/**
 * 路由访问权限配置
 * 统一管理页面的访问权限规则
 */

export type RouteAccessType = 'public' | 'protected' | 'auth-only' | 'guest-only'

export interface RouteConfig {
  pattern: string
  access: RouteAccessType
  redirectTo?: string
  roles?: string[] // 未来扩展：基于角色的访问控制
  permissions?: string[] // 未来扩展：基于权限的访问控制
}

/**
 * 路由访问配置
 * 按优先级排序，匹配时使用第一个匹配的规则
 */
export const ROUTE_CONFIG: RouteConfig[] = [
  // Test routes - 开发环境下可访问
  {
    pattern: '/(test)',
    access: 'public',
  },

  // Auth routes - 只允许未登录用户访问
  {
    pattern: '/login',
    access: 'guest-only',
    redirectTo: '/chat',
  },
  {
    pattern: '/register',
    access: 'guest-only', 
    redirectTo: '/chat',
  },
  {
    pattern: '/forgot-password',
    access: 'guest-only',
    redirectTo: '/chat',
  },
  {
    pattern: '/auth/callback',
    access: 'public', // OAuth回调需要公开访问
  },

  // Homepage versions - 公开访问
  {
    pattern: '/homepage',
    access: 'public',
  },

  // API routes - 公开（由API自己处理认证）
  {
    pattern: '/api',
    access: 'public',
  },

  // Main application routes - 需要认证
  {
    pattern: '/chat',
    access: 'protected',
    redirectTo: '/login',
  },
  {
    pattern: '/contacts',
    access: 'protected',
    redirectTo: '/login',
  },
  {
    pattern: '/files',
    access: 'protected',
    redirectTo: '/login',
  },
  {
    pattern: '/social',
    access: 'protected', 
    redirectTo: '/login',
  },
  {
    pattern: '/plugins',
    access: 'protected',
    redirectTo: '/login',
  },
  {
    pattern: '/settings',
    access: 'protected',
    redirectTo: '/login',
  },

  // Root path - 根据认证状态重定向
  {
    pattern: '/',
    access: 'public', // 特殊处理：在代理层中根据认证状态重定向
  },

  // Default - 其他路由默认需要保护
  {
    pattern: '*',
    access: 'protected',
    redirectTo: '/login',
  },
]

/**
 * 获取路径的访问配置
 */
export function getRouteConfig(pathname: string): RouteConfig {
  for (const config of ROUTE_CONFIG) {
    if (matchRoute(pathname, config.pattern)) {
      return config
    }
  }
  
  // 默认返回保护路由
  return {
    pattern: '*',
    access: 'protected',
    redirectTo: '/login',
  }
}

/**
 * 检查路径是否匹配模式
 */
function matchRoute(pathname: string, pattern: string): boolean {
  if (pattern === '*') return true
  if (pattern === pathname) return true
  
  // 处理括号路由 (auth) -> /login, /register etc.
  if (pattern.includes('(') && pattern.includes(')')) {
    const basePattern = pattern.replace(/\([^)]*\)/g, '')
    return pathname.startsWith(basePattern)
  }
  
  // 处理前缀匹配
  return pathname.startsWith(pattern)
}

/**
 * 检查用户是否有权访问指定路由
 */
export function canAccessRoute(
  pathname: string,
  isAuthenticated: boolean,
  userRoles?: string[],
  userPermissions?: string[]
): {
  canAccess: boolean
  shouldRedirect: boolean
  redirectTo?: string
} {
  const config = getRouteConfig(pathname)
  
  switch (config.access) {
    case 'public':
      return { canAccess: true, shouldRedirect: false }
      
    case 'guest-only':
      if (isAuthenticated) {
        return {
          canAccess: false,
          shouldRedirect: true,
          redirectTo: config.redirectTo || '/chat',
        }
      }
      return { canAccess: true, shouldRedirect: false }
      
    case 'protected':
      if (!isAuthenticated) {
        return {
          canAccess: false,
          shouldRedirect: true,
          redirectTo: config.redirectTo || '/login',
        }
      }
      // TODO: 检查角色和权限
      return { canAccess: true, shouldRedirect: false }
      
    case 'auth-only':
      // 需要特定认证状态，暂时按保护路由处理
      if (!isAuthenticated) {
        return {
          canAccess: false,
          shouldRedirect: true,
          redirectTo: config.redirectTo || '/login',
        }
      }
      return { canAccess: true, shouldRedirect: false }
      
    default:
      return { canAccess: false, shouldRedirect: true, redirectTo: '/login' }
  }
}

/**
 * 获取保护路由列表（用于代理层）
 */
export function getProtectedRoutes(): string[] {
  return ROUTE_CONFIG
    .filter(config => config.access === 'protected')
    .map(config => config.pattern)
    .filter(pattern => pattern !== '*' && !pattern.includes('('))
}

/**
 * 获取公开路由列表
 */
export function getPublicRoutes(): string[] {
  return ROUTE_CONFIG
    .filter(config => config.access === 'public')
    .map(config => config.pattern)
    .filter(pattern => pattern !== '*' && !pattern.includes('('))
}

/**
 * 获取访客专用路由列表（未登录用户专用）
 */
export function getGuestOnlyRoutes(): string[] {
  return ROUTE_CONFIG
    .filter(config => config.access === 'guest-only')
    .map(config => config.pattern)
}