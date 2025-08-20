# Store Architecture Migration Guide

## 🚀 Enhanced Store Architecture Migration

从当前的 `index.ts` 迁移到增强的 `index.new.ts` 架构。

### 📊 **架构对比**

| 特性 | 当前架构 (`index.ts`) | 增强架构 (`index.new.ts`) |
|------|---------------------|--------------------------|
| **性能** | 中等 | 🚀 优秀 (个别选择器) |
| **状态结构** | 平面化 | 🏗️ 分层结构 |
| **错误处理** | 基础 | 📝 详细历史记录 |
| **持久化** | 简单 | 🎯 选择性持久化 |
| **会话管理** | 无 | ⏰ 自动超时管理 |
| **缓存** | 基础 | 🔄 TTL自动清理 |
| **类型安全** | 好 | 💪 更强 |

### 🔧 **新架构特性**

#### **1. 分层状态结构**
```typescript
// ❌ 旧结构 (平面化)
{
  user: User | null,
  isAuthenticated: boolean,
  isLoading: boolean,
  error: string | null,
}

// ✅ 新结构 (分层)
{
  auth: {
    user: User | null,
    token: string | null,
    isAuthenticated: boolean,
    sessionStarted: Date | null,
    lastActivity: Date | null,
  },
  ui: {
    isLoading: boolean,
    isInitializing: boolean, 
    showLoginModal: boolean,
  },
  error: {
    current: string | null,
    history: Array<{
      message: string,
      timestamp: Date,
      action: string,
    }>,
  }
}
```

#### **2. 增强的错误处理**
```typescript
// ✅ 错误历史追踪
setError("Login failed", "loginWithCredentials")

// ✅ 错误历史访问
const errorHistory = auth.error.history
```

#### **3. 自动会话管理**
```typescript
// ✅ 会话超时检查
const isExpired = auth.checkSessionTimeout() // 30分钟超时

// ✅ 自动活动延长
auth.extendSession() // 在用户活动时自动调用
```

#### **4. 性能优化的Hooks**
```typescript
// ✅ 轻量级选择器
const user = useAuthUser()          // 只订阅user变化
const isAuth = useIsAuthenticated() // 只订阅认证状态
const loading = useAuthLoading()    // 只订阅加载状态

// ✅ 完整功能
const auth = useAuth()              // 所有auth功能
```

## 📋 **迁移步骤**

### **Phase 1: 准备迁移**

1. **备份当前store**:
```bash
cp src/store/index.ts src/store/index.backup.ts
```

2. **检查依赖的缺失切片**:
需要确保以下切片存在：
- ✅ `slices/auth/authSlice.ts` (已创建)
- ❓ `slices/ui/preferencesSlice.ts`
- ❓ `slices/ui/layoutSlice.ts` 
- ❓ `slices/ui/notificationSlice.ts`
- ❓ `slices/chat/conversationSlice.ts`
- ❓ `utils/persistence.ts`

### **Phase 2: 创建缺失的切片**

我们需要创建其他必要的切片文件。

### **Phase 3: 切换到新架构**

```bash
# 重命名文件
mv src/store/index.ts src/store/index.old.ts
mv src/store/index.new.ts src/store/index.ts
```

### **Phase 4: 更新组件调用**

#### **认证相关组件更新**

```typescript
// ❌ 旧调用方式
const auth = useAuth()
const { user, isAuthenticated, error } = auth

// ✅ 新调用方式 (更好的性能)
const user = useAuthUser()
const isAuthenticated = useIsAuthenticated()  
const error = useAuthError()

// 或者仍然使用完整的auth对象
const auth = useAuth()
const { auth: { user }, ui: { isLoading }, error: { current } } = auth
```

#### **测试页面更新**

```typescript
// ✅ 新架构下的测试页面调用
const auth = useAuth()

// 访问分层状态
const isAuthenticated = auth.auth.isAuthenticated
const currentUser = auth.auth.user  
const isLoading = auth.ui.isLoading
const currentError = auth.error.current

// 动作调用保持相同
await auth.loginWithCredentials(email, password)
await auth.getCurrentUser()
```

## 🎯 **迁移的好处**

### **1. 性能提升**
- **减少重新渲染**: 精细的选择器只在相关数据变化时触发更新
- **更好的内存管理**: 自动清理过期数据和错误历史

### **2. 更好的用户体验**
- **会话管理**: 自动超时和活动检测
- **错误追踪**: 详细的错误历史便于调试
- **加载状态**: 更精细的加载状态管理

### **3. 开发体验**
- **更好的类型提示**: 分层结构提供更清晰的类型推断
- **更容易调试**: 结构化的状态和错误历史
- **更好的可维护性**: 模块化的切片结构

### **4. 扩展性**
- **选择性持久化**: 不同数据使用不同的存储策略
- **缓存策略**: TTL支持和自动清理
- **插件架构**: 更容易添加新功能

## ⚠️ **注意事项**

1. **状态结构变化**: 需要更新所有访问认证状态的组件
2. **Hook名称**: 新增了专用的轻量级hooks
3. **错误处理**: 错误结构从简单字符串变为对象
4. **会话管理**: 新增了会话超时功能，可能影响用户体验

## 🧪 **测试计划**

1. **功能测试**: 确保所有认证功能正常工作
2. **性能测试**: 验证重新渲染次数减少
3. **会话测试**: 验证30分钟超时和活动延长
4. **错误测试**: 验证错误历史记录功能
5. **持久化测试**: 验证状态正确保存和恢复

## 🚀 **开始迁移**

准备好迁移了吗？我们可以：

1. **现在开始**: 创建缺失的切片文件并执行迁移
2. **分阶段进行**: 先创建切片，然后逐步测试
3. **保持当前**: 继续使用修复后的当前架构

你想要如何进行？