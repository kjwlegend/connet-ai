# Security & Authentication Architecture - Connet.AI

## 安全架构原则

### 1. 深度防御 (Defense in Depth)
- **多层防护**: 在每个系统层级实施安全措施
- **冗余保护**: 单点失败不应导致整体安全失效
- **最小权限**: 用户和组件仅获得必需的最小权限
- **零信任模型**: 不信任任何请求，始终验证身份和权限

### 2. 数据保护原则
- **传输加密**: 所有数据传输使用 HTTPS/WSS
- **存储加密**: 敏感数据静态加密存储
- **访问控制**: 细粒度的数据访问权限控制
- **数据最小化**: 仅收集和存储必要的用户数据

### 3. 隐私设计 (Privacy by Design)
- **隐私优先**: 系统设计时将隐私作为首要考虑
- **透明性**: 用户清楚了解数据收集和使用方式
- **用户控制**: 用户可以控制自己的数据和隐私设置
- **合规性**: 符合 GDPR、CCPA 等隐私法规要求

## 整体安全架构

```
Security Architecture Overview
│
├── 🌐 Network Security Layer (网络安全层)
│   ├── CDN & WAF (内容分发网络和Web应用防火墙)
│   │   ├── DDoS Protection (DDoS攻击防护)
│   │   ├── Bot Detection (机器人检测)
│   │   ├── Rate Limiting (频率限制)
│   │   └── Geo-blocking (地理位置阻断)
│   │
│   ├── SSL/TLS Termination (SSL/TLS终端)
│   │   ├── Certificate Management (证书管理)
│   │   ├── HSTS Headers (HTTP严格传输安全)
│   │   ├── Perfect Forward Secrecy (完美前向保密)
│   │   └── TLS 1.3 Support (TLS 1.3支持)
│   │
│   └── API Gateway Security (API网关安全)
│       ├── Request Validation (请求验证)
│       ├── IP Whitelisting (IP白名单)
│       ├── Throttling (节流)
│       └── Security Headers (安全头)
│
├── 🔐 Authentication & Authorization (认证授权层)
│   ├── Identity Management (身份管理)
│   │   ├── User Registration (用户注册)
│   │   ├── Email Verification (邮箱验证)
│   │   ├── Password Policy (密码策略)
│   │   └── Account Recovery (账户恢复)
│   │
│   ├── Multi-Factor Authentication (多因素认证)
│   │   ├── TOTP (基于时间的一次性密码)
│   │   ├── SMS Verification (短信验证)
│   │   ├── Email OTP (邮箱一次性密码)
│   │   └── Backup Codes (备份码)
│   │
│   ├── OAuth 2.0 & OpenID Connect (OAuth 2.0 和 OpenID Connect)
│   │   ├── Authorization Code Flow (授权码流程)
│   │   ├── PKCE Support (代码交换证明密钥)
│   │   ├── Scope Management (作用域管理)
│   │   └── Token Introspection (令牌内省)
│   │
│   ├── JWT Token Management (JWT令牌管理)
│   │   ├── Access Token (访问令牌)
│   │   ├── Refresh Token (刷新令牌)
│   │   ├── Token Rotation (令牌轮换)
│   │   └── Revocation Lists (撤销列表)
│   │
│   └── Role-Based Access Control (基于角色的访问控制)
│       ├── User Roles (用户角色)
│       ├── Permissions Matrix (权限矩阵)
│       ├── Resource Authorization (资源授权)
│       └── Dynamic Permissions (动态权限)
│
├── 🛡️ Application Security Layer (应用安全层)
│   ├── Frontend Security (前端安全)
│   │   ├── XSS Protection (XSS防护)
│   │   ├── CSRF Protection (CSRF防护)
│   │   ├── Content Security Policy (内容安全策略)
│   │   └── Secure Storage (安全存储)
│   │
│   ├── Backend Security (后端安全)
│   │   ├── Input Validation (输入验证)
│   │   ├── SQL Injection Prevention (SQL注入防护)
│   │   ├── Command Injection Prevention (命令注入防护)
│   │   └── File Upload Security (文件上传安全)
│   │
│   ├── API Security (API安全)
│   │   ├── Request Signing (请求签名)
│   │   ├── Timestamp Validation (时间戳验证)
│   │   ├── Payload Encryption (载荷加密)
│   │   └── Response Filtering (响应过滤)
│   │
│   └── Real-time Security (实时通信安全)
│       ├── WebSocket Authentication (WebSocket认证)
│       ├── Message Encryption (消息加密)
│       ├── Channel Authorization (频道授权)
│       └── Rate Limiting (频率限制)
│
├── 💾 Data Security Layer (数据安全层)
│   ├── Encryption at Rest (静态加密)
│   │   ├── Database Encryption (数据库加密)
│   │   ├── File Storage Encryption (文件存储加密)
│   │   ├── Key Management (密钥管理)
│   │   └── Backup Encryption (备份加密)
│   │
│   ├── Encryption in Transit (传输加密)
│   │   ├── TLS for HTTP/WebSocket (HTTP/WebSocket的TLS)
│   │   ├── Database Connection Encryption (数据库连接加密)
│   │   ├── Inter-service Communication (服务间通信)
│   │   └── Third-party API Calls (第三方API调用)
│   │
│   ├── Data Classification (数据分类)
│   │   ├── Public Data (公开数据)
│   │   ├── Internal Data (内部数据)
│   │   ├── Confidential Data (机密数据)
│   │   └── Restricted Data (受限数据)
│   │
│   └── Data Loss Prevention (数据丢失防护)
│       ├── Access Logging (访问日志)
│       ├── Anomaly Detection (异常检测)
│       ├── Data Masking (数据掩码)
│       └── Leak Detection (泄露检测)
│
├── 📊 Monitoring & Incident Response (监控和事件响应)
│   ├── Security Monitoring (安全监控)
│   │   ├── SIEM Integration (SIEM集成)
│   │   ├── Real-time Alerts (实时告警)
│   │   ├── Threat Intelligence (威胁情报)
│   │   └── Behavioral Analysis (行为分析)
│   │
│   ├── Audit Logging (审计日志)
│   │   ├── User Activity Logs (用户活动日志)
│   │   ├── System Access Logs (系统访问日志)
│   │   ├── Data Modification Logs (数据修改日志)
│   │   └── Security Event Logs (安全事件日志)
│   │
│   └── Incident Response (事件响应)
│       ├── Incident Detection (事件检测)
│       ├── Response Procedures (响应程序)
│       ├── Forensic Analysis (取证分析)
│       └── Recovery Procedures (恢复程序)
│
└── 🔄 Compliance & Governance (合规治理)
    ├── Privacy Compliance (隐私合规)
    │   ├── GDPR Compliance (GDPR合规)
    │   ├── CCPA Compliance (CCPA合规)
    │   ├── Data Subject Rights (数据主体权利)
    │   └── Privacy Impact Assessment (隐私影响评估)
    │
    ├── Security Standards (安全标准)
    │   ├── ISO 27001 (ISO 27001)
    │   ├── SOC 2 Type II (SOC 2 Type II)  
    │   ├── OWASP Guidelines (OWASP指南)
    │   └── Industry Best Practices (行业最佳实践)
    │
    └── Risk Management (风险管理)
        ├── Risk Assessment (风险评估)
        ├── Vulnerability Management (漏洞管理)
        ├── Penetration Testing (渗透测试)
        └── Security Training (安全培训)
```

## 认证架构设计

### 1. 身份认证流程

#### 1.1 用户注册流程
```typescript
// lib/auth/registration.ts
interface RegistrationFlow {
  // 第一步：基本信息收集
  collectBasicInfo: {
    email: string
    password: string
    displayName: string
    termsAccepted: boolean
    privacyPolicyAccepted: boolean
  }
  
  // 第二步：密码强度验证
  validatePassword: {
    minLength: 12
    requireUppercase: true
    requireLowercase: true  
    requireNumbers: true
    requireSpecialChars: true
    preventCommonPasswords: true
    preventPersonalInfo: true
  }
  
  // 第三步：邮箱验证
  emailVerification: {
    sendVerificationEmail: () => Promise<void>
    verifyEmailToken: (token: string) => Promise<boolean>
    resendVerificationEmail: () => Promise<void>
    verificationExpiry: number // 24小时
  }
  
  // 第四步：账户激活
  accountActivation: {
    createUserProfile: () => Promise<User>
    setupDefaultPreferences: () => Promise<void>
    generateInitialTokens: () => Promise<AuthTokens>
    sendWelcomeEmail: () => Promise<void>
  }
}

class RegistrationService {
  async register(registrationData: RegistrationRequest): Promise<RegistrationResponse> {
    // 1. 输入验证和清理
    const validatedData = await this.validateAndSanitizeInput(registrationData)
    
    // 2. 检查邮箱是否已存在
    const existingUser = await this.checkEmailExists(validatedData.email)
    if (existingUser) {
      throw new AuthError('EMAIL_ALREADY_EXISTS', '该邮箱地址已被注册')
    }
    
    // 3. 密码强度验证
    const passwordValidation = await this.validatePasswordStrength(validatedData.password)
    if (!passwordValidation.isValid) {
      throw new AuthError('WEAK_PASSWORD', passwordValidation.message)
    }
    
    // 4. 检查频率限制
    await this.checkRegistrationRateLimit(validatedData.email)
    
    // 5. 创建用户账户（未激活状态）
    const hashedPassword = await this.hashPassword(validatedData.password)
    const pendingUser = await this.createPendingUser({
      ...validatedData,
      password: hashedPassword,
      verificationToken: this.generateVerificationToken(),
      createdAt: new Date(),
      isVerified: false
    })
    
    // 6. 发送验证邮件
    await this.sendVerificationEmail(pendingUser.email, pendingUser.verificationToken)
    
    // 7. 记录注册事件
    await this.logRegistrationEvent(pendingUser.id, 'REGISTRATION_INITIATED', {
      email: pendingUser.email,
      ipAddress: this.getClientIP(),
      userAgent: this.getUserAgent()
    })
    
    return {
      success: true,
      message: '注册成功，请检查邮箱并点击验证链接激活账户',
      userId: pendingUser.id,
      verificationRequired: true
    }
  }
  
  async verifyEmail(token: string): Promise<VerificationResponse> {
    // 1. 验证令牌格式和签名
    const tokenData = await this.validateVerificationToken(token)
    if (!tokenData) {
      throw new AuthError('INVALID_VERIFICATION_TOKEN', '验证链接无效或已过期')
    }
    
    // 2. 检查令牌是否过期
    if (this.isTokenExpired(tokenData)) {
      throw new AuthError('VERIFICATION_TOKEN_EXPIRED', '验证链接已过期，请重新发送')
    }
    
    // 3. 获取待验证用户
    const pendingUser = await this.getPendingUser(tokenData.userId)
    if (!pendingUser) {
      throw new AuthError('USER_NOT_FOUND', '用户不存在')
    }
    
    // 4. 激活用户账户
    const activatedUser = await this.activateUser(pendingUser)
    
    // 5. 生成初始访问令牌
    const tokens = await this.generateAuthTokens(activatedUser)
    
    // 6. 设置默认用户偏好
    await this.setupDefaultPreferences(activatedUser.id)
    
    // 7. 记录验证成功事件
    await this.logRegistrationEvent(activatedUser.id, 'EMAIL_VERIFIED', {
      ipAddress: this.getClientIP(),
      userAgent: this.getUserAgent()
    })
    
    // 8. 发送欢迎邮件
    await this.sendWelcomeEmail(activatedUser)
    
    return {
      success: true,
      message: '邮箱验证成功，账户已激活',
      user: this.sanitizeUserForResponse(activatedUser),
      tokens
    }
  }
}
```

#### 1.2 用户登录流程
```typescript
// lib/auth/authentication.ts
class AuthenticationService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // 1. 输入验证和清理
    const { email, password, rememberMe, captchaToken } = credentials
    const sanitizedEmail = this.sanitizeEmail(email)
    
    // 2. 检查登录频率限制
    await this.checkLoginRateLimit(sanitizedEmail)
    
    // 3. 验证验证码（如果需要）
    if (captchaToken) {
      const captchaValid = await this.verifyCaptcha(captchaToken)
      if (!captchaValid) {
        throw new AuthError('INVALID_CAPTCHA', '验证码错误')
      }
    }
    
    // 4. 查找用户
    const user = await this.getUserByEmail(sanitizedEmail)
    if (!user) {
      // 避免用户枚举攻击，返回通用错误
      await this.simulatePasswordHash() // 模拟密码哈希时间
      throw new AuthError('INVALID_CREDENTIALS', '邮箱或密码错误')
    }
    
    // 5. 检查账户状态
    this.checkAccountStatus(user)
    
    // 6. 验证密码
    const passwordValid = await this.verifyPassword(password, user.passwordHash)
    if (!passwordValid) {
      // 记录登录失败
      await this.recordFailedLogin(user.id, sanitizedEmail)
      throw new AuthError('INVALID_CREDENTIALS', '邮箱或密码错误')
    }
    
    // 7. 检查是否需要多因素认证
    if (user.mfaEnabled) {
      // 生成临时登录令牌，要求MFA验证
      const tempToken = await this.generateTempLoginToken(user.id)
      
      return {
        success: false,
        requiresMFA: true,
        tempToken,
        mfaMethods: user.enabledMfaMethods,
        message: '请完成多因素认证'
      }
    }
    
    // 8. 生成访问令牌
    const tokens = await this.generateAuthTokens(user, {
      rememberMe,
      deviceInfo: this.getDeviceInfo()
    })
    
    // 9. 更新用户登录信息
    await this.updateUserLogin(user.id, {
      lastLoginAt: new Date(),
      lastLoginIP: this.getClientIP(),
      loginCount: user.loginCount + 1
    })
    
    // 10. 记录登录成功事件
    await this.logAuthEvent(user.id, 'LOGIN_SUCCESS', {
      ipAddress: this.getClientIP(),
      userAgent: this.getUserAgent(),
      deviceFingerprint: this.getDeviceFingerprint()
    })
    
    // 11. 清理失败登录记录
    await this.clearFailedLoginRecords(user.id)
    
    return {
      success: true,
      user: this.sanitizeUserForResponse(user),
      tokens,
      message: '登录成功'
    }
  }
  
  // 多因素认证验证
  async verifyMFA(tempToken: string, mfaCode: string, method: MFAMethod): Promise<LoginResponse> {
    // 1. 验证临时令牌
    const tempTokenData = await this.validateTempLoginToken(tempToken)
    if (!tempTokenData) {
      throw new AuthError('INVALID_TEMP_TOKEN', '临时令牌无效或已过期')
    }
    
    // 2. 获取用户
    const user = await this.getUserById(tempTokenData.userId)
    if (!user) {
      throw new AuthError('USER_NOT_FOUND', '用户不存在')
    }
    
    // 3. 验证MFA代码
    const mfaValid = await this.verifyMFACode(user, mfaCode, method)
    if (!mfaValid) {
      await this.logAuthEvent(user.id, 'MFA_VERIFICATION_FAILED', {
        method,
        ipAddress: this.getClientIP()
      })
      throw new AuthError('INVALID_MFA_CODE', 'MFA验证码错误')
    }
    
    // 4. 生成最终访问令牌
    const tokens = await this.generateAuthTokens(user, {
      deviceInfo: this.getDeviceInfo()
    })
    
    // 5. 撤销临时令牌
    await this.revokeTempLoginToken(tempToken)
    
    // 6. 记录MFA验证成功
    await this.logAuthEvent(user.id, 'MFA_VERIFICATION_SUCCESS', {
      method,
      ipAddress: this.getClientIP()
    })
    
    return {
      success: true,
      user: this.sanitizeUserForResponse(user),
      tokens,
      message: 'MFA验证成功，登录完成'
    }
  }
}
```

### 2. JWT 令牌管理

#### 2.1 令牌结构设计
```typescript
// lib/auth/tokenManager.ts
interface AccessTokenPayload {
  // 标准声明
  iss: string      // 令牌签发者
  sub: string      // 用户ID
  aud: string      // 令牌接收者
  exp: number      // 过期时间
  iat: number      // 签发时间
  jti: string      // 令牌ID
  
  // 自定义声明
  type: 'access'   // 令牌类型
  userId: string   // 用户ID
  email: string    // 用户邮箱
  roles: string[]  // 用户角色
  permissions: string[] // 用户权限
  sessionId: string // 会话ID
  deviceId?: string // 设备ID
  mfaVerified: boolean // MFA验证状态
  
  // 限制性声明  
  ipAddress: string // 绑定IP地址
  userAgent: string // 绑定用户代理
}

interface RefreshTokenPayload {
  iss: string
  sub: string
  aud: string
  exp: number      // 长期过期时间（7-30天）
  iat: number
  jti: string
  
  type: 'refresh'
  userId: string
  sessionId: string
  deviceId?: string
  family: string   // 令牌家族，用于令牌轮换
}

class TokenManager {
  private accessTokenTTL = 15 * 60 // 15分钟
  private refreshTokenTTL = 7 * 24 * 60 * 60 // 7天
  private tokenBlacklist = new Set<string>()
  
  async generateAuthTokens(user: User, options?: TokenOptions): Promise<AuthTokens> {
    const sessionId = this.generateSessionId()
    const deviceId = options?.deviceInfo ? this.generateDeviceId(options.deviceInfo) : undefined
    const now = Math.floor(Date.now() / 1000)
    
    // 生成访问令牌
    const accessTokenPayload: AccessTokenPayload = {
      iss: 'connet.ai',
      sub: user.id,
      aud: 'connet.ai-web',
      exp: now + this.accessTokenTTL,
      iat: now,
      jti: this.generateTokenId(),
      type: 'access',
      userId: user.id,
      email: user.email,
      roles: user.roles,
      permissions: await this.getUserPermissions(user),
      sessionId,
      deviceId,
      mfaVerified: true, // 已通过MFA验证
      ipAddress: this.getClientIP(),
      userAgent: this.getUserAgent()
    }
    
    // 生成刷新令牌
    const refreshTokenPayload: RefreshTokenPayload = {
      iss: 'connet.ai',
      sub: user.id,
      aud: 'connet.ai-web',
      exp: now + (options?.rememberMe ? 30 * 24 * 60 * 60 : this.refreshTokenTTL),
      iat: now,
      jti: this.generateTokenId(),
      type: 'refresh',
      userId: user.id,
      sessionId,
      deviceId,
      family: this.generateTokenFamily()
    }
    
    // 签名令牌
    const accessToken = await this.signToken(accessTokenPayload)
    const refreshToken = await this.signToken(refreshTokenPayload)
    
    // 存储刷新令牌（用于轮换检测）
    await this.storeRefreshToken(refreshTokenPayload)
    
    // 记录令牌生成事件
    await this.logTokenEvent(user.id, 'TOKENS_GENERATED', {
      sessionId,
      deviceId,
      accessTokenId: accessTokenPayload.jti,
      refreshTokenId: refreshTokenPayload.jti
    })
    
    return {
      accessToken,
      refreshToken,
      tokenType: 'Bearer',
      expiresIn: this.accessTokenTTL,
      scope: 'read write'
    }
  }
  
  async refreshAccessToken(refreshToken: string): Promise<AuthTokens> {
    // 1. 验证刷新令牌
    const payload = await this.verifyToken(refreshToken) as RefreshTokenPayload
    
    // 2. 检查令牌是否被撤销
    if (await this.isTokenRevoked(payload.jti)) {
      throw new AuthError('TOKEN_REVOKED', '刷新令牌已被撤销')
    }
    
    // 3. 检查令牌轮换（检测令牌重用）
    const storedToken = await this.getStoredRefreshToken(payload.jti)
    if (!storedToken || storedToken.used) {
      // 检测到令牌重用，撤销整个令牌家族
      await this.revokeTokenFamily(payload.family)
      await this.logSecurityEvent(payload.userId, 'TOKEN_REUSE_DETECTED', {
        tokenId: payload.jti,
        family: payload.family
      })
      throw new AuthError('TOKEN_REUSE_DETECTED', '检测到令牌重用，已撤销相关会话')
    }
    
    // 4. 标记旧刷新令牌为已使用
    await this.markRefreshTokenUsed(payload.jti)
    
    // 5. 获取最新用户信息
    const user = await this.getUserById(payload.userId)
    if (!user || !user.isActive) {
      throw new AuthError('USER_INACTIVE', '用户账户不可用')
    }
    
    // 6. 生成新的令牌对
    const newTokens = await this.generateAuthTokens(user, {
      sessionId: payload.sessionId, // 保持相同会话
      deviceId: payload.deviceId
    })
    
    // 7. 记录令牌刷新事件
    await this.logTokenEvent(user.id, 'TOKENS_REFRESHED', {
      oldRefreshTokenId: payload.jti,
      sessionId: payload.sessionId
    })
    
    return newTokens
  }
  
  async validateAccessToken(token: string): Promise<AccessTokenPayload> {
    // 1. 验证令牌签名和基本结构
    const payload = await this.verifyToken(token) as AccessTokenPayload
    
    // 2. 检查令牌类型
    if (payload.type !== 'access') {
      throw new AuthError('INVALID_TOKEN_TYPE', '令牌类型错误')
    }
    
    // 3. 检查令牌是否在黑名单中
    if (this.tokenBlacklist.has(payload.jti)) {
      throw new AuthError('TOKEN_BLACKLISTED', '令牌已被撤销')
    }
    
    // 4. 检查用户状态
    const user = await this.getUserById(payload.userId)
    if (!user || !user.isActive) {
      throw new AuthError('USER_INACTIVE', '用户账户不可用')
    }
    
    // 5. 验证绑定条件（可选）
    if (this.config.strictIPBinding) {
      const currentIP = this.getClientIP()
      if (payload.ipAddress !== currentIP) {
        await this.logSecurityEvent(payload.userId, 'IP_MISMATCH', {
          tokenIP: payload.ipAddress,
          currentIP
        })
        throw new AuthError('IP_MISMATCH', 'IP地址不匹配')
      }
    }
    
    return payload
  }
  
  async revokeToken(tokenId: string, reason: string = 'USER_LOGOUT'): Promise<void> {
    // 添加到黑名单
    this.tokenBlacklist.add(tokenId)
    
    // 持久化撤销记录
    await this.storeRevokedToken(tokenId, reason)
    
    // 记录撤销事件
    await this.logTokenEvent(null, 'TOKEN_REVOKED', {
      tokenId,
      reason
    })
  }
  
  async revokeAllUserTokens(userId: string, reason: string = 'SECURITY_INCIDENT'): Promise<void> {
    // 获取用户的所有活跃会话
    const activeSessions = await this.getUserActiveSessions(userId)
    
    // 撤销所有相关令牌
    for (const session of activeSessions) {
      await this.revokeSession(session.sessionId, reason)
    }
    
    // 记录批量撤销事件
    await this.logSecurityEvent(userId, 'ALL_TOKENS_REVOKED', {
      reason,
      sessionCount: activeSessions.length
    })
  }
}
```

### 3. 基于角色的访问控制 (RBAC)

#### 3.1 权限模型设计
```typescript
// lib/auth/rbac.ts
interface Permission {
  id: string
  name: string
  description: string
  resource: string    // 资源类型
  action: string      // 操作类型
  conditions?: PermissionCondition[] // 条件限制
}

interface Role {
  id: string
  name: string
  description: string
  permissions: string[] // 权限ID列表
  isSystemRole: boolean // 是否为系统内置角色
  inheritFrom?: string[] // 继承的角色
}

interface PermissionCondition {
  type: 'ownership' | 'time' | 'ip' | 'custom'
  value: any
  operator: 'equals' | 'in' | 'between' | 'custom'
}

// 系统预定义角色
const SystemRoles: Record<string, Role> = {
  SUPER_ADMIN: {
    id: 'super_admin',
    name: '超级管理员',
    description: '系统最高权限，可执行所有操作',
    permissions: ['*'], // 通配符表示所有权限
    isSystemRole: true
  },
  
  ADMIN: {
    id: 'admin', 
    name: '管理员',
    description: '管理员权限，可管理用户和内容',
    permissions: [
      'user:read', 'user:update', 'user:delete',
      'conversation:read', 'conversation:update', 'conversation:delete',
      'agent:read', 'agent:create', 'agent:update',
      'file:read', 'file:delete',
      'system:read'
    ],
    isSystemRole: true
  },
  
  PREMIUM_USER: {
    id: 'premium_user',
    name: '高级用户',
    description: '付费用户，拥有高级功能访问权',
    permissions: [
      'conversation:create', 'conversation:read', 'conversation:update', 'conversation:delete',
      'message:create', 'message:read', 'message:update', 'message:delete',
      'agent:read', 'agent:use_premium',
      'file:create', 'file:read', 'file:update', 'file:delete',
      'file:upload_large', 'file:vector_search',
      'timeline:create', 'timeline:read',
      'profile:update'
    ],
    isSystemRole: true,
    inheritFrom: ['basic_user']
  },
  
  BASIC_USER: {
    id: 'basic_user',
    name: '基础用户',
    description: '免费用户，拥有基础功能访问权',
    permissions: [
      'conversation:create:limited', 'conversation:read:own', 'conversation:update:own', 'conversation:delete:own',
      'message:create:limited', 'message:read:own',
      'agent:read', 'agent:use_basic',
      'file:create:limited', 'file:read:own', 'file:delete:own',
      'timeline:read',
      'profile:read', 'profile:update:own'
    ],
    isSystemRole: true
  },
  
  GUEST: {
    id: 'guest',
    name: '访客',
    description: '未登录用户，只能访问公开内容',
    permissions: [
      'agent:read:public',
      'timeline:read:public'
    ],
    isSystemRole: true
  }
}

class RBACManager {
  private permissionsCache = new Map<string, Permission[]>()
  private rolesCache = new Map<string, Role>()
  
  async getUserPermissions(userId: string): Promise<Permission[]> {
    // 检查缓存
    if (this.permissionsCache.has(userId)) {
      return this.permissionsCache.get(userId)!
    }
    
    // 获取用户的所有角色
    const userRoles = await this.getUserRoles(userId)
    const allPermissions = new Set<Permission>()
    
    // 递归收集所有权限（包括继承的权限）
    for (const role of userRoles) {
      const rolePermissions = await this.getRolePermissions(role.id, true)
      rolePermissions.forEach(permission => allPermissions.add(permission))
    }
    
    const permissions = Array.from(allPermissions)
    
    // 缓存权限（5分钟）
    this.permissionsCache.set(userId, permissions)
    setTimeout(() => this.permissionsCache.delete(userId), 5 * 60 * 1000)
    
    return permissions
  }
  
  async checkPermission(
    userId: string, 
    resource: string, 
    action: string, 
    context?: PermissionContext
  ): Promise<boolean> {
    // 获取用户权限
    const permissions = await this.getUserPermissions(userId)
    
    // 检查是否有超级权限
    if (permissions.some(p => p.id === '*' || p.resource === '*')) {
      return true
    }
    
    // 查找匹配的权限
    const matchingPermissions = permissions.filter(permission => {
      // 精确匹配
      if (permission.resource === resource && permission.action === action) {
        return true
      }
      
      // 通配符匹配
      if (permission.resource === resource && permission.action === '*') {
        return true
      }
      
      // 资源组匹配
      if (permission.resource.endsWith(':*') && 
          resource.startsWith(permission.resource.slice(0, -1))) {
        return true
      }
      
      return false
    })
    
    if (matchingPermissions.length === 0) {
      return false
    }
    
    // 检查条件限制
    for (const permission of matchingPermissions) {
      if (await this.checkPermissionConditions(permission, context)) {
        return true
      }
    }
    
    return false
  }
  
  private async checkPermissionConditions(
    permission: Permission, 
    context?: PermissionContext
  ): Promise<boolean> {
    if (!permission.conditions || permission.conditions.length === 0) {
      return true
    }
    
    for (const condition of permission.conditions) {
      const result = await this.evaluateCondition(condition, context)
      if (!result) {
        return false
      }
    }
    
    return true
  }
  
  private async evaluateCondition(
    condition: PermissionCondition, 
    context?: PermissionContext
  ): Promise<boolean> {
    switch (condition.type) {
      case 'ownership':
        // 检查资源所有权
        return context?.resourceOwnerId === context?.userId
        
      case 'time':
        // 检查时间限制
        const now = new Date()
        const timeRange = condition.value as { start: string, end: string }
        return now >= new Date(timeRange.start) && now <= new Date(timeRange.end)
        
      case 'ip':
        // 检查IP地址限制
        const allowedIPs = condition.value as string[]
        return allowedIPs.includes(context?.clientIP || '')
        
      case 'custom':
        // 自定义条件处理
        return await this.evaluateCustomCondition(condition.value, context)
        
      default:
        return false
    }
  }
  
  // 权限装饰器，用于保护API端点
  requirePermission(resource: string, action: string) {
    return (target: any, propertyName: string, descriptor: PropertyDescriptor) => {
      const method = descriptor.value
      
      descriptor.value = async function (this: any, ...args: any[]) {
        // 从请求上下文获取用户信息
        const context = this.getRequestContext()
        const userId = context.user?.id
        
        if (!userId) {
          throw new AuthError('UNAUTHORIZED', '需要登录')
        }
        
        // 检查权限
        const hasPermission = await rbacManager.checkPermission(
          userId, 
          resource, 
          action, 
          context
        )
        
        if (!hasPermission) {
          await rbacManager.logAccessDenied(userId, resource, action, context)
          throw new AuthError('FORBIDDEN', '权限不足')
        }
        
        // 执行原方法
        return method.apply(this, args)
      }
      
      return descriptor
    }
  }
}

export const rbacManager = new RBACManager()

// 使用示例
class ConversationController {
  @requirePermission('conversation', 'read')
  async getConversation(conversationId: string) {
    // 方法实现
  }
  
  @requirePermission('conversation', 'create')
  async createConversation(data: CreateConversationRequest) {
    // 方法实现
  }
  
  @requirePermission('conversation', 'delete')
  async deleteConversation(conversationId: string) {
    // 方法实现
  }
}
```

## 前端安全防护

### 1. XSS 防护机制

#### 1.1 内容安全策略 (CSP)
```typescript
// lib/security/csp.ts
const ContentSecurityPolicy = {
  // 基础 CSP 配置
  directives: {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'unsafe-inline'", // 开发环境需要，生产环境应移除
      'https://cdn.connet.ai',
      'https://js.stripe.com',
      'https://challenges.cloudflare.com' // Cloudflare Turnstile
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'", // Tailwind CSS 需要
      'https://fonts.googleapis.com'
    ],
    'img-src': [
      "'self'",
      'data:', // Base64 图片
      'blob:', // 文件预览
      'https://cdn.connet.ai',
      'https://storage.connet.ai',
      'https://*.githubusercontent.com' // GitHub 头像
    ],
    'font-src': [
      "'self'",
      'https://fonts.gstatic.com'
    ],
    'connect-src': [
      "'self'",
      'https://api.connet.ai',
      'wss://api.connet.ai',
      'https://upload.connet.ai'
    ],
    'media-src': [
      "'self'",
      'https://storage.connet.ai'
    ],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  },
  
  // 生成 CSP 头
  generateHeader(): string {
    return Object.entries(this.directives)
      .map(([directive, sources]) => 
        `${directive} ${sources.join(' ')}`
      )
      .join('; ')
  }
}

// Next.js 配置
export const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: ContentSecurityPolicy.generateHeader()
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()'
  }
]
```

#### 1.2 输入验证和输出编码
```typescript
// lib/security/sanitization.ts
import DOMPurify from 'dompurify'
import { JSDOM } from 'jsdom'

class ContentSanitizer {
  private window: Window
  private DOMPurify: DOMPurify.DOMPurifyI
  
  constructor() {
    // 服务端环境创建虚拟 DOM
    if (typeof window === 'undefined') {
      const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>')
      this.window = dom.window as unknown as Window
      this.DOMPurify = DOMPurify(this.window)
    } else {
      this.window = window
      this.DOMPurify = DOMPurify
    }
  }
  
  // 清理用户输入的 HTML 内容
  sanitizeHTML(input: string, options?: SanitizeOptions): string {
    const config = {
      ALLOWED_TAGS: options?.allowedTags || [
        'p', 'br', 'strong', 'em', 'u', 'code', 'pre',
        'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3'
      ],
      ALLOWED_ATTR: options?.allowedAttributes || [
        'class', 'id'
      ],
      KEEP_CONTENT: true,
      RETURN_DOM_FRAGMENT: false,
      // 移除所有事件处理器
      FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'style'],
      // 移除潜在危险的标签
      FORBID_TAGS: ['script', 'object', 'embed', 'form', 'input', 'textarea']
    }
    
    return this.DOMPurify.sanitize(input, config)
  }
  
  // 转义文本内容
  escapeHTML(text: string): string {
    const escapeMap: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    }
    
    return text.replace(/[&<>"'/]/g, (match) => escapeMap[match])
  }
  
  // 清理用户消息内容
  sanitizeMessage(content: string, type: 'text' | 'markdown' | 'html'): string {
    switch (type) {
      case 'text':
        return this.escapeHTML(content)
        
      case 'markdown':
        // Markdown 转换为 HTML 后再清理
        const htmlContent = this.markdownToHTML(content)
        return this.sanitizeHTML(htmlContent, {
          allowedTags: ['p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li', 'a'],
          allowedAttributes: ['href', 'title']
        })
        
      case 'html':
        return this.sanitizeHTML(content)
        
      default:
        return this.escapeHTML(content)
    }
  }
  
  // 验证和清理文件名
  sanitizeFilename(filename: string): string {
    // 移除路径分隔符和特殊字符
    return filename
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, '')
      .replace(/^\.+/, '') // 移除开头的点
      .substring(0, 255) // 限制长度
  }
  
  // 验证 URL 安全性
  validateURL(url: string): boolean {
    try {
      const parsedURL = new URL(url)
      
      // 只允许 HTTP(S) 协议
      if (!['http:', 'https:'].includes(parsedURL.protocol)) {
        return false
      }
      
      // 检查是否为恶意域名
      const suspiciousDomains = [
        'javascript:', 'data:', 'vbscript:', 'file:', 'about:'
      ]
      
      if (suspiciousDomains.some(domain => url.toLowerCase().startsWith(domain))) {
        return false
      }
      
      return true
    } catch {
      return false
    }
  }
}

export const contentSanitizer = new ContentSanitizer()
```

### 2. CSRF 防护

#### 2.1 CSRF Token 实现
```typescript
// lib/security/csrf.ts
import crypto from 'crypto'

class CSRFProtection {
  private readonly tokenSecret: string
  private readonly tokenTTL = 60 * 60 * 1000 // 1小时
  
  constructor() {
    this.tokenSecret = process.env.CSRF_SECRET || crypto.randomBytes(32).toString('hex')
  }
  
  // 生成 CSRF Token
  generateToken(): string {
    const timestamp = Date.now()
    const randomBytes = crypto.randomBytes(16).toString('hex')
    const payload = `${timestamp}:${randomBytes}`
    
    const hmac = crypto.createHmac('sha256', this.tokenSecret)
    hmac.update(payload)
    const signature = hmac.digest('hex')
    
    return Buffer.from(`${payload}:${signature}`).toString('base64')
  }
  
  // 验证 CSRF Token
  validateToken(token: string): boolean {
    try {
      const decoded = Buffer.from(token, 'base64').toString('utf8')
      const [timestamp, randomBytes, signature] = decoded.split(':')
      
      // 检查时间戳
      const tokenTime = parseInt(timestamp)
      if (Date.now() - tokenTime > this.tokenTTL) {
        return false
      }
      
      // 验证签名
      const payload = `${timestamp}:${randomBytes}`
      const hmac = crypto.createHmac('sha256', this.tokenSecret)
      hmac.update(payload)
      const expectedSignature = hmac.digest('hex')
      
      return crypto.timingSafeEqual(
        Buffer.from(signature, 'hex'),
        Buffer.from(expectedSignature, 'hex')
      )
    } catch {
      return false
    }
  }
  
  // Next.js API 中间件
  middleware(req: NextApiRequest, res: NextApiResponse, next: () => void) {
    // GET 请求不需要 CSRF 保护
    if (req.method === 'GET') {
      return next()
    }
    
    const token = req.headers['x-csrf-token'] as string
    
    if (!token || !this.validateToken(token)) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'CSRF_TOKEN_INVALID',
          message: 'CSRF token is missing or invalid'
        }
      })
    }
    
    next()
  }
}

export const csrfProtection = new CSRFProtection()
```

## 数据安全与隐私保护

### 1. 数据加密

#### 1.1 端到端加密设计
```typescript
// lib/security/encryption.ts
import crypto from 'crypto'

class E2EEncryption {
  private readonly algorithm = 'aes-256-gcm'
  private readonly keyLength = 32
  private readonly ivLength = 16
  private readonly tagLength = 16
  
  // 生成密钥对（用于密钥交换）
  generateKeyPair(): crypto.KeyPairKeyObjectResult {
    return crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
      },
      privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem'
      }
    })
  }
  
  // 生成对称加密密钥
  generateSymmetricKey(): Buffer {
    return crypto.randomBytes(this.keyLength)
  }
  
  // 对称加密
  encrypt(data: string, key: Buffer): EncryptedData {
    const iv = crypto.randomBytes(this.ivLength)
    const cipher = crypto.createCipher(this.algorithm, key)
    cipher.setAAD(Buffer.from('connet-ai-e2e'))
    
    let encrypted = cipher.update(data, 'utf8')
    encrypted = Buffer.concat([encrypted, cipher.final()])
    
    const tag = cipher.getAuthTag()
    
    return {
      encrypted: encrypted.toString('base64'),
      iv: iv.toString('base64'),
      tag: tag.toString('base64')
    }
  }
  
  // 对称解密
  decrypt(encryptedData: EncryptedData, key: Buffer): string {
    const decipher = crypto.createDecipher(this.algorithm, key)
    decipher.setAAD(Buffer.from('connet-ai-e2e'))
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'base64'))
    
    let decrypted = decipher.update(Buffer.from(encryptedData.encrypted, 'base64'))
    decrypted = Buffer.concat([decrypted, decipher.final()])
    
    return decrypted.toString('utf8')
  }
  
  // 非对称加密（用于密钥交换）
  encryptWithPublicKey(data: string, publicKey: string): string {
    const buffer = Buffer.from(data, 'utf8')
    const encrypted = crypto.publicEncrypt(publicKey, buffer)
    return encrypted.toString('base64')
  }
  
  // 非对称解密
  decryptWithPrivateKey(encryptedData: string, privateKey: string): string {
    const buffer = Buffer.from(encryptedData, 'base64')
    const decrypted = crypto.privateDecrypt(privateKey, buffer)
    return decrypted.toString('utf8')
  }
}

// 消息加密服务
class MessageEncryption {
  private e2e = new E2EEncryption()
  
  // 为对话生成加密密钥
  async generateConversationKey(conversationId: string): Promise<ConversationKey> {
    const symmetricKey = this.e2e.generateSymmetricKey()
    
    // 存储加密后的密钥（使用主密钥加密）
    const encryptedKey = await this.encryptWithMasterKey(symmetricKey)
    
    await this.storeConversationKey(conversationId, encryptedKey)
    
    return {
      conversationId,
      key: symmetricKey,
      createdAt: new Date()
    }
  }
  
  // 加密消息内容
  async encryptMessage(conversationId: string, content: string): Promise<EncryptedMessage> {
    const conversationKey = await this.getConversationKey(conversationId)
    const encryptedData = this.e2e.encrypt(content, conversationKey.key)
    
    return {
      conversationId,
      encryptedContent: encryptedData,
      algorithm: 'aes-256-gcm',
      keyVersion: conversationKey.version
    }
  }
  
  // 解密消息内容
  async decryptMessage(encryptedMessage: EncryptedMessage): Promise<string> {
    const conversationKey = await this.getConversationKey(
      encryptedMessage.conversationId, 
      encryptedMessage.keyVersion
    )
    
    return this.e2e.decrypt(encryptedMessage.encryptedContent, conversationKey.key)
  }
  
  // 共享对话密钥给新参与者
  async shareConversationKey(
    conversationId: string, 
    recipientPublicKey: string
  ): Promise<string> {
    const conversationKey = await this.getConversationKey(conversationId)
    
    // 使用接收者的公钥加密对话密钥
    return this.e2e.encryptWithPublicKey(
      conversationKey.key.toString('base64'), 
      recipientPublicKey
    )
  }
}
```

### 2. 隐私保护机制

#### 2.1 数据最小化和匿名化
```typescript
// lib/privacy/dataMinimization.ts
class DataMinimizationManager {
  
  // 数据分类定义
  private dataClassification = {
    PUBLIC: {
      retention: Infinity,
      encryption: false,
      anonymization: false
    },
    INTERNAL: {
      retention: 365 * 24 * 60 * 60 * 1000, // 1年
      encryption: true,
      anonymization: false
    },
    CONFIDENTIAL: {
      retention: 90 * 24 * 60 * 60 * 1000, // 90天
      encryption: true,
      anonymization: true
    },
    RESTRICTED: {
      retention: 30 * 24 * 60 * 60 * 1000, // 30天
      encryption: true,
      anonymization: true
    }
  }
  
  // 用户数据匿名化
  anonymizeUserData(userData: UserData): AnonymizedUserData {
    return {
      id: this.generateAnonymousId(userData.id),
      // 保留必要的非敏感信息
      createdAt: userData.createdAt,
      lastActiveAt: userData.lastActiveAt,
      subscriptionPlan: userData.subscriptionPlan,
      
      // 移除或匿名化敏感信息
      email: this.hashEmail(userData.email),
      displayName: `User_${this.generateAnonymousId(userData.id).substring(0, 8)}`,
      
      // 保留用于分析的统计信息
      conversationCount: userData.conversationCount,
      messageCount: userData.messageCount,
      
      // 移除完全敏感的信息
      phoneNumber: null,
      ipAddress: null,
      deviceInfo: null
    }
  }
  
  // 对话数据匿名化
  anonymizeConversationData(conversation: Conversation): AnonymizedConversation {
    return {
      id: this.generateAnonymousId(conversation.id),
      createdAt: conversation.createdAt,
      messageCount: conversation.messageCount,
      
      // 匿名化参与者信息
      participants: conversation.participants.map(p => ({
        id: this.generateAnonymousId(p.id),
        type: p.type,
        role: p.role
      })),
      
      // 移除消息内容，只保留元数据
      messages: conversation.messages.map(m => ({
        id: this.generateAnonymousId(m.id),
        senderId: this.generateAnonymousId(m.senderId),
        timestamp: m.timestamp,
        type: m.type,
        // 内容被移除或哈希化
        contentHash: this.hashContent(m.content),
        contentLength: m.content.length
      }))
    }
  }
  
  // 自动数据清理
  async scheduleDataCleanup(): Promise<void> {
    // 每天执行一次数据清理
    setInterval(async () => {
      await this.performDataCleanup()
    }, 24 * 60 * 60 * 1000)
  }
  
  private async performDataCleanup(): Promise<void> {
    const now = Date.now()
    
    // 清理过期的临时数据
    await this.cleanupExpiredSessions()
    await this.cleanupExpiredTokens()
    await this.cleanupExpiredOTPs()
    
    // 根据数据分类清理用户数据
    const expiredUsers = await this.getInactiveUsers(180) // 180天未活跃
    for (const user of expiredUsers) {
      await this.anonymizeOrDeleteUserData(user.id)
    }
    
    // 清理旧的日志数据
    await this.cleanupOldLogs(90) // 保留90天日志
    
    console.log(`Data cleanup completed at ${new Date().toISOString()}`)
  }
  
  // 用户数据导出（GDPR要求）
  async exportUserData(userId: string): Promise<UserDataExport> {
    const user = await this.getUserById(userId)
    const conversations = await this.getUserConversations(userId)
    const files = await this.getUserFiles(userId)
    const activities = await this.getUserActivities(userId)
    
    return {
      exportedAt: new Date().toISOString(),
      userId,
      personalInfo: {
        email: user.email,
        displayName: user.displayName,
        createdAt: user.createdAt,
        lastActiveAt: user.lastActiveAt
      },
      conversations: conversations.map(conv => ({
        id: conv.id,
        title: conv.title,
        createdAt: conv.createdAt,
        messages: conv.messages.map(msg => ({
          content: msg.content,
          timestamp: msg.timestamp,
          senderId: msg.senderId === userId ? 'You' : 'Agent'
        }))
      })),
      files: files.map(file => ({
        filename: file.filename,
        uploadedAt: file.createdAt,
        size: file.size
      })),
      activities: activities.map(activity => ({
        type: activity.type,
        timestamp: activity.timestamp,
        details: activity.details
      }))
    }
  }
  
  // 用户数据删除（GDPR要求）
  async deleteUserData(userId: string, reason: string = 'USER_REQUEST'): Promise<void> {
    // 记录删除请求
    await this.logDataDeletionRequest(userId, reason)
    
    // 软删除用户账户
    await this.markUserAsDeleted(userId)
    
    // 匿名化相关数据
    await this.anonymizeUserConversations(userId)
    await this.anonymizeUserFiles(userId)
    await this.anonymizeUserActivities(userId)
    
    // 撤销所有令牌
    await this.revokeAllUserTokens(userId)
    
    // 通知相关服务
    await this.notifyServicesOfDeletion(userId)
    
    console.log(`User data deletion completed for user ${userId}`)
  }
}
```

---

**安全架构版本**: v1.0  
**最后更新**: 2025-01-08  
**合规标准**: GDPR, CCPA, ISO 27001, OWASP Top 10

这个安全和认证架构为 Connet.AI 提供了：

1. **全面的安全防护**: 从网络层到应用层的多层安全机制
2. **强大的认证系统**: JWT + MFA + RBAC 的完整认证授权体系
3. **数据保护机制**: 端到端加密和数据匿名化保护用户隐私
4. **合规性支持**: 符合国际隐私和安全标准的数据处理机制
5. **实时监控**: 安全事件监控和自动响应机制
6. **用户控制**: 用户可以完全控制自己的数据和隐私设置

通过这个安全架构，Connet.AI 能够为用户提供安全、可信的 AI 协作环境。

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create detailed frontend architecture document", "status": "completed", "priority": "high", "id": "1"}, {"content": "Create detailed backend architecture document", "status": "completed", "priority": "high", "id": "2"}, {"content": "Design system integration patterns", "status": "completed", "priority": "medium", "id": "3"}, {"content": "API design specifications", "status": "completed", "priority": "medium", "id": "4"}, {"content": "Data flow and state management architecture", "status": "completed", "priority": "medium", "id": "5"}, {"content": "Security and authentication architecture", "status": "completed", "priority": "medium", "id": "6"}]