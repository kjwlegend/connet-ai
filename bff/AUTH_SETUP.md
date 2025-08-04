# Authentication Setup Guide

本指南将帮助你设置和使用 Connet.AI BFF 服务的登录注册功能。

## 🚀 快速开始

### 1. 环境配置

首先复制环境变量示例文件：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入以下必需的环境变量：

```bash
# Supabase 配置
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"

# 数据库配置
DATABASE_URL="postgresql://postgres:password@localhost:5432/connet_ai"

# 安全配置
SECRET_KEY="your-super-secret-key-here"  # 生成: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行设置脚本

```bash
python scripts/setup_auth.py
```

这个脚本会：
- ✅ 验证环境变量
- ✅ 测试 Supabase 连接
- ✅ 测试数据库连接
- ✅ 设置数据库模式（可选）
- ✅ 测试认证服务

### 4. 启动服务

```bash
python -m uvicorn app.main:app --reload
```

服务将在 `http://localhost:8000` 启动。

## 📚 API 接口

### 用户注册

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "username": "johndoe"  // 可选
}
```

**响应:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 用户登录

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**响应:**
```json
{
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-token-here",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe",
    "is_active": true
  }
}
```

### 刷新令牌

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh-token-here"
}
```

### 获取当前用户信息

```bash
GET /api/v1/auth/me
Authorization: Bearer jwt-token-here
```

### 密码重置

```bash
POST /api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### 邮箱验证

```bash
POST /api/v1/auth/verify-email?token=verification-token&email=user@example.com
```

### 登出

```bash
POST /api/v1/auth/logout
Authorization: Bearer jwt-token-here
```

## 🏗️ 架构说明

### 认证流程设计

1. **双重认证系统**: 支持 Supabase Auth 和本地 JWT 令牌
2. **用户数据同步**: Supabase Auth 用户数据同步到本地 PostgreSQL
3. **灵活的认证提供商**: 支持多种认证方式（本地、Supabase、OAuth）

### 数据库模型

用户表支持以下字段：
- `id`: UUID 主键（可使用 Supabase 用户 ID）
- `email`: 邮箱地址
- `full_name`: 全名
- `username`: 用户名（可选）
- `password_hash`: 本地密码哈希（OAuth 用户可为空）
- `auth_provider`: 认证提供商（local、supabase 等）
- `external_id`: 外部提供商用户 ID
- `is_active`: 账户状态
- `metadata`: 额外元数据

### 令牌验证

中间件支持两种令牌验证方式：
1. **本地 JWT**: 由 BFF 服务签发的 JWT 令牌
2. **Supabase 令牌**: Supabase Auth 签发的令牌

## 🔧 配置选项

### JWT 配置

```bash
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Supabase 配置

```bash
SUPABASE_URL="https://project.supabase.co"
SUPABASE_ANON_KEY="anon-key"
SUPABASE_SERVICE_ROLE_KEY="service-role-key"
```

## 🧪 测试

### 使用 FastAPI 文档界面

访问 `http://localhost:8000/docs` 来测试 API 接口。

### 使用 curl 测试

```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpassword123",
       "full_name": "Test User"
     }'

# 登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpassword123"
     }'
```

## 🛠️ 故障排除

### 常见问题

1. **Supabase 连接失败**
   - 检查 `SUPABASE_URL` 和密钥是否正确
   - 确保 Supabase 项目已启用认证功能

2. **数据库连接失败**
   - 检查 `DATABASE_URL` 格式是否正确
   - 确保 PostgreSQL 服务已启动

3. **令牌验证失败**
   - 检查 `SECRET_KEY` 是否设置
   - 确保令牌没有过期

### 日志调试

设置日志级别为 DEBUG：

```bash
LOG_LEVEL="DEBUG"
```

### 数据库重置

如果需要重置数据库：

```bash
python scripts/init_database.py
```

## 🔒 安全注意事项

1. **生产环境**:
   - 使用强密码作为 `SECRET_KEY`
   - 启用 HTTPS
   - 配置合适的 CORS 策略

2. **Supabase 安全**:
   - 不要在客户端暴露 Service Role Key
   - 配置 Row Level Security (RLS)

3. **令牌管理**:
   - 实现令牌黑名单机制
   - 设置合适的过期时间

## 📈 下一步

1. **实现 OAuth 登录**: Google, GitHub 等
2. **添加多因素认证**: SMS, TOTP 等
3. **用户权限管理**: 角色和权限系统
4. **审计日志**: 登录活动记录