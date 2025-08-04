# 可调用 API 接口文档

本文档列出了当前已完成且可以进行前端对接的 API 接口。

## 📋 接口状态说明

- ✅ **已完成** - 接口已实现并测试，可以对接
- 🚧 **开发中** - 接口正在开发，请勿对接
- 📝 **计划中** - 接口尚未开始开发

## 🔐 认证相关接口

### Base URL
```
http://localhost:8000/api/v1
```

### 认证方式
```
Authorization: Bearer <access_token>
```

---

## ✅ 用户注册

**接口地址**: `POST /auth/register`

**状态**: ✅ 已完成

**请求参数**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "张三",
  "username": "zhangsan",  // 可选
  
  // 邀请系统 (可选)
  "invited_by_code": "ABC123",
  
  // 注册追踪 (可选，用于数据分析)
  "registration_source": "web",      // web, mobile, api
  "registration_channel": "invite",  // organic, invite, social, campaign
  
  // UTM 参数 (可选，用于营销追踪)
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "summer_2024"
}
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "张三",
  "username": "zhangsan",
  "is_active": true,
  "invitation_code": "XYZ789",  // 用户的专属邀请码
  "created_at": "2024-08-04T10:30:00Z",
  "updated_at": "2024-08-04T10:30:00Z",
  "last_login_at": null,
  "permissions": [],
  "roles": []
}
```

**错误响应**:
```json
{
  "detail": "User with this email already exists"
}
```

```json
{
  "detail": "Invalid invitation code"
}
```

**前端集成要点**:
- **必填字段**: `email`, `password`, `full_name`
- **可选字段**: `username`, `invited_by_code`, 注册追踪和 UTM 参数
- 密码至少 8 位字符，邮箱格式验证，用户名 3-50 字符
- 邀请码验证：如提供邀请码，系统会验证其有效性
- 注册成功后用户获得专属邀请码 `invitation_code`
- 支持营销追踪：可传入 UTM 参数用于数据分析
- 注册成功后可直接跳转登录页

---

## ✅ 用户登录

**接口地址**: `POST /auth/login`

**状态**: ✅ 已完成

**请求参数**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "张三",
    "username": "zhangsan",
    "is_active": true,
    "created_at": "2024-08-04T10:30:00Z",
    "updated_at": "2024-08-04T10:30:00Z",
    "last_login_at": "2024-08-04T12:00:00Z",
    "permissions": [],
    "roles": []
  }
}
```

**错误响应**:
```json
{
  "detail": "Invalid email or password"
}
```

**前端集成要点**:
- 登录成功后保存 `access_token` 和 `refresh_token`
- `access_token` 有效期 30 分钟
- `refresh_token` 有效期 7 天
- 需要在请求头中携带 token: `Authorization: Bearer <access_token>`

---

## ✅ 刷新访问令牌

**接口地址**: `POST /auth/refresh`

**状态**: ✅ 已完成

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "张三",
    "username": "zhangsan",
    "is_active": true,
    "invitation_code": "XYZ789"
  }
}
```

**前端集成要点**:
- 当 `access_token` 过期时自动调用此接口
- 同时更新 `access_token` 和 `refresh_token`
- 如果 `refresh_token` 也过期，需要重新登录

---

## ✅ 获取当前用户信息

**接口地址**: `GET /auth/me`

**状态**: ✅ 已完成

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "张三",
  "username": "zhangsan",
  "is_active": true,
  "invitation_code": "XYZ789",
  "created_at": "2024-08-04T10:30:00Z",
  "updated_at": "2024-08-04T10:30:00Z",
  "last_login_at": "2024-08-04T12:00:00Z",
  "permissions": [],
  "roles": []
}
```

**前端集成要点**:
- 用于获取用户个人信息
- 可用于验证登录状态
- 需要携带有效的 `access_token`

---

## ✅ 用户登出

**接口地址**: `POST /auth/logout`

**状态**: ✅ 已完成

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "message": "Logged out successfully"
}
```

**前端集成要点**:
- 登出后清除本地存储的 token
- 重定向到登录页面

---

## ✅ 密码重置请求

**接口地址**: `POST /auth/password-reset`

**状态**: ✅ 已完成

**请求参数**:
```json
{
  "email": "user@example.com"
}
```

**响应示例**:
```json
{
  "message": "Password reset email sent successfully"
}
```

**前端集成要点**:
- 用户输入邮箱后发送重置邮件
- 邮件中包含重置链接
- 重置链接会重定向到前端重置密码页面

---

## ✅ 邮箱验证

**接口地址**: `POST /auth/verify-email`

**状态**: ✅ 已完成

**请求参数** (Query Parameters):
```
?token=verification_token&email=user@example.com
```

**响应示例**:
```json
{
  "message": "Email verified successfully"
}
```

**前端集成要点**:
- 用户点击邮件中的验证链接时调用
- 验证成功后用户账户被激活

---

## ✅ 令牌验证

**接口地址**: `POST /auth/verify`

**状态**: ✅ 已完成

**请求参数**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "valid": true,
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "exp": 1691155200,
    "iat": 1691153400,
    "type": "access",
    "scopes": []
  }
}
```

**前端集成要点**:
- 用于验证 token 是否有效
- 可在路由守卫中使用

---

## 📋 邀请系统说明

### 邀请码机制

每个注册用户都会获得一个唯一的 6 位邀请码（格式：3个字母+3个数字，如 `ABC123`），用于邀请其他用户注册。

### 邀请流程

1. **用户 A 注册**：系统自动生成邀请码 `ABC123`
2. **用户 A 分享邀请码**：将邀请码 `ABC123` 分享给朋友
3. **用户 B 注册**：使用邀请码 `ABC123` 注册，在 `invited_by_code` 字段传入
4. **系统验证**：验证邀请码有效性，建立邀请关系
5. **用户 B 获得邀请码**：注册成功后获得自己的邀请码 `XYZ789`

### 前端实现建议

```javascript
// 注册表单示例
const registerData = {
  email: "user@example.com",
  password: "securepassword123",
  full_name: "张三",
  username: "zhangsan",
  
  // 从 URL 参数获取邀请码
  invited_by_code: getUrlParam('invite'), // 如: ?invite=ABC123
  
  // 注册来源追踪
  registration_source: "web",
  registration_channel: getUrlParam('invite') ? "invite" : "organic",
  
  // UTM 参数（如果存在）
  utm_source: getUrlParam('utm_source'),
  utm_medium: getUrlParam('utm_medium'),
  utm_campaign: getUrlParam('utm_campaign')
};
```

### 营销追踪参数

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `registration_source` | 注册来源 | `web`, `mobile`, `api` |
| `registration_channel` | 注册渠道 | `organic`, `invite`, `social`, `campaign` |
| `utm_source` | 流量来源 | `google`, `facebook`, `email` |
| `utm_medium` | 流量媒介 | `cpc`, `social`, `email` |
| `utm_campaign` | 活动名称 | `summer_2024`, `launch_promo` |

---

## 🚧 开发中的接口

目前没有正在开发中的接口。

---

## 📝 计划中的接口

### 用户管理
- `GET /users` - 获取用户列表
- `GET /users/{user_id}` - 获取用户详情
- `PUT /users/{user_id}` - 更新用户信息
- `DELETE /users/{user_id}` - 删除用户
- `GET /auth/invitation-codes/{code}/validate` - 验证邀请码是否有效

### AI 代理管理
- `GET /agents` - 获取 AI 代理列表
- `POST /agents` - 创建 AI 代理
- `GET /agents/{agent_id}` - 获取代理详情
- `PUT /agents/{agent_id}` - 更新代理信息
- `DELETE /agents/{agent_id}` - 删除代理

### 对话管理
- `GET /conversations` - 获取对话列表
- `POST /conversations` - 创建对话
- `GET /conversations/{conversation_id}` - 获取对话详情
- `POST /conversations/{conversation_id}/messages` - 发送消息

### 文件管理
- `POST /files/upload` - 文件上传
- `GET /files` - 获取文件列表
- `GET /files/{file_id}` - 下载文件
- `DELETE /files/{file_id}` - 删除文件

---

## 📊 接口开发进度

| 模块 | 进度 | 已完成接口数 | 总计划接口数 |
|------|------|-------------|-------------|
| 认证系统 | ✅ 100% | 8/8 | 8 |
| 用户管理 | 📝 0% | 0/5 | 5 |
| AI 代理管理 | 📝 0% | 0/5 | 5 |
| 对话管理 | 📝 0% | 0/4 | 4 |
| 文件管理 | 📝 0% | 0/4 | 4 |

**总体进度**: 8/26 (31%)

---

## 🛠️ 前端对接准备

### 环境要求
- BFF 服务运行在: `http://localhost:8000`
- API 文档地址: `http://localhost:8000/docs`

### 通用错误处理

所有接口可能返回的通用错误：

**401 Unauthorized**:
```json
{
  "detail": "Authentication required" 
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

### 前端实现建议

1. **Token 管理**:
   - 使用 localStorage 或 sessionStorage 存储 token
   - 实现自动 token 刷新机制
   - 在 axios/fetch 拦截器中自动添加 Authorization header

2. **错误处理**:
   - 统一处理 401 错误，自动跳转登录页
   - 统一处理 422 验证错误，显示表单错误信息
   - 统一处理 500 错误，显示友好提示

3. **API 封装**:
   ```typescript
   // 示例 API 封装
   class AuthAPI {
     static async register(data: RegisterRequest) {
       return await api.post('/auth/register', data);
     }
     
     static async login(data: LoginRequest) {
       return await api.post('/auth/login', data);
     }
     
     static async getCurrentUser() {
       return await api.get('/auth/me');
     }
   }
   ```

4. **类型定义**:
   ```typescript
   interface User {
     id: string;
     email: string;
     full_name: string;
     username?: string;
     is_active: boolean;
     created_at: string;
     updated_at: string;
     last_login_at?: string;
     permissions: string[];
     roles: string[];
   }
   
   interface LoginResponse {
     access_token: string;
     refresh_token: string;
     token_type: string;
     expires_in: number;
     user: User;
   }
   ```

---

## 📞 联系方式

如有接口相关问题，请联系后端团队：
- 接口文档更新时间: 2024-08-04
- 下次更新计划: 待用户管理模块完成后更新