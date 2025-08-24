# 认证与页面访问权限管理

## 概述

本项目使用双重保护机制来管理页面访问权限：
1. **Middleware级别保护**：服务器端拦截，基于cookie/header中的token
2. **组件级别保护**：客户端守卫，基于实时store状态

## 路由配置系统

### 1. 路由配置文件 (`route-config.ts`)

统一管理所有页面的访问权限规则：

```typescript
export type RouteAccessType = 'public' | 'protected' | 'auth-only' | 'guest-only'

// 使用示例
const config = getRouteConfig('/chat') // { access: 'protected', redirectTo: '/login' }
const check = canAccessRoute('/login', true) // { canAccess: false, shouldRedirect: true, redirectTo: '/chat' }
```

**访问类型说明**:
- `public`: 公开访问，无需认证
- `protected`: 需要认证，未登录用户重定向到登录页
- `guest-only`: 只允许未登录用户，已登录用户重定向到应用主页  
- `auth-only`: 需要特定认证状态（预留扩展）

### 2. 路由匹配规则

按优先级顺序匹配，支持：
- 精确匹配：`/login`
- 前缀匹配：`/chat` 匹配 `/chat/123`
- 分组路由：`/(auth)` 匹配 `/login`, `/register`
- 通配符：`*` 作为默认规则

## 组件保护系统

### 1. RouteGuard 组件

主要的路由守卫组件：

```tsx
import { RouteGuard } from '@/components/auth/RouteGuard'

// 基础用法
<RouteGuard>
  <YourComponent />
</RouteGuard>

// 自定义加载状态
<RouteGuard fallback={<CustomLoader />}>
  <YourComponent />
</RouteGuard>
```

### 2. LayoutGuard 组件

用于保护整个布局：

```tsx
import { LayoutGuard } from '@/components/auth/RouteGuard'

export default function ChatLayout() {
  return (
    <LayoutGuard>
      <AppLayout>
        {/* 布局内容 */}
      </AppLayout>
    </LayoutGuard>
  )
}
```

### 3. PageGuard 组件

用于页面级别的精确控制：

```tsx
import { PageGuard } from '@/components/auth/RouteGuard'

// 需要认证的页面
<PageGuard requireAuth={true}>
  <ProtectedContent />
</PageGuard>

// 只允许未登录用户的页面（如登录页）
<PageGuard requireAuth={false}>
  <LoginForm />
</PageGuard>
```

### 4. withRouteGuard HOC

高阶组件形式的保护：

```tsx
import { withRouteGuard } from '@/components/auth/RouteGuard'

const ProtectedComponent = withRouteGuard(YourComponent)
```

### 5. useRouteGuard Hook

获取当前路由的访问状态：

```tsx
import { useRouteGuard } from '@/components/auth/RouteGuard'

function MyComponent() {
  const { canAccess, shouldRedirect, isLoading } = useRouteGuard()
  
  if (isLoading) return <Spinner />
  if (!canAccess) return <AccessDenied />
  
  return <Content />
}
```

## Middleware 配置

### Token 获取策略

Middleware按以下顺序查找token：

1. 分类存储cookie：`permanent:connet-ai-store`, `cache:connet-ai-store` 等
2. 直接存储cookie：`connet-ai-store`
3. 传统token cookie：`auth_token`
4. Authorization header：`Bearer <token>`

### 重定向逻辑

- **未认证用户访问保护页面**：重定向到 `/login?redirect=<current-path>`
- **已认证用户访问认证专用页面**：重定向到 `/chat`
- **根路径访问**：根据认证状态重定向到 `/chat` 或 `/login`

## 页面分类与配置

### 当前页面分类

**公开页面**:
- `/homepage/*` - 产品展示页面
- `/(test)/*` - 开发测试页面
- `/api/*` - API路由
- `/auth/callback` - OAuth回调

**认证保护页面**:
- `/chat/*` - 聊天功能
- `/contacts/*` - 联系人管理
- `/files/*` - 文件管理
- `/social/*` - 社交时间线
- `/plugins/*` - 插件市场
- `/settings/*` - 用户设置

**访客专用页面**:
- `/login` - 登录页面
- `/register` - 注册页面
- `/forgot-password` - 找回密码

### Layout 保护状态

所有需要认证的layout已配置`LayoutGuard`：

```typescript
// ✅ 已保护的 layouts
- /chat/layout.tsx
- /contacts/layout.tsx
- /files/layout.tsx
- /plugins/layout.tsx
- /settings/layout.tsx
- /social/layout.tsx

// ✅ 访客保护的 layouts  
- /(auth)/layout.tsx
```

## 最佳实践

### 1. 新增保护页面

```tsx
// 1. 在 route-config.ts 中配置路由
{
  pattern: '/new-feature',
  access: 'protected',
  redirectTo: '/login'
}

// 2. 在 layout.tsx 中添加 LayoutGuard
import { LayoutGuard } from '@/components/auth/RouteGuard'

export default function NewFeatureLayout() {
  return (
    <LayoutGuard>
      <AppLayout>
        {/* 内容 */}
      </AppLayout>
    </LayoutGuard>
  )
}
```

### 2. 条件渲染保护内容

```tsx
import { useRouteGuard } from '@/components/auth/RouteGuard'

function ConditionalContent() {
  const { isAuthenticated, isLoading } = useRouteGuard()
  
  if (isLoading) return <Spinner />
  
  return (
    <div>
      <PublicContent />
      {isAuthenticated && <PrivateContent />}
    </div>
  )
}
```

### 3. 错误处理

```tsx
<RouteGuard
  fallback={
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Spinner />
        <p>Checking permissions...</p>
      </div>
    </div>
  }
>
  <YourContent />
</RouteGuard>
```

## 调试与监控

### 开发环境调试

在控制台查看路由保护日志：
```
RouteGuard: Redirecting to /login?redirect=/chat
AuthGuard effect: { isLoading: false, requireAuth: true, isAuthenticated: false, pathname: '/chat' }
```

### 测试访问权限

1. 访问 `/(test)/auth-test` 页面测试认证流程
2. 尝试未登录访问保护页面，应重定向到登录页
3. 登录后访问认证专用页面，应重定向到应用主页

## 未来扩展

### 基于角色的访问控制 (RBAC)

```typescript
// 预留的扩展接口
interface RouteConfig {
  pattern: string
  access: RouteAccessType
  roles?: string[] // ['admin', 'user']
  permissions?: string[] // ['read:posts', 'write:posts']
}

// 使用示例
{
  pattern: '/admin',
  access: 'protected',
  roles: ['admin'],
  permissions: ['manage:users']
}
```

### 动态权限检查

```typescript
const accessCheck = canAccessRoute(
  '/admin/users', 
  true, 
  ['admin'], // 用户角色
  ['manage:users'] // 用户权限
)
```