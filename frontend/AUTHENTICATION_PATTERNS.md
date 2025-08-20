# Authentication Patterns & Best Practices

## ✅ **Correct Usage Pattern**

### **1. Use AuthSlice for All Authentication Operations**

```tsx
import { useAuth } from '@/store'

function MyComponent() {
  const auth = useAuth()
  
  // ✅ Login
  const handleLogin = async () => {
    await auth.loginWithCredentials(email, password, rememberMe)
  }
  
  // ✅ Register  
  const handleRegister = async () => {
    await auth.registerWithCredentials({ email, password, full_name })
  }
  
  // ✅ Get current user (with proper Bearer token)
  const handleGetUser = async () => {
    await auth.getCurrentUser()
  }
  
  // ✅ Logout
  const handleLogout = async () => {
    await auth.logout()
  }
  
  // ✅ Token operations
  const isValid = await auth.validateToken()
  const refreshed = await auth.refreshAuthToken()
  
  // ✅ OAuth
  const oauthUrl = await auth.getOAuthUrl('google', redirectUri)
}
```

### **2. Token Injection is Automatic**

The authSlice properly sets up the API client with token injection:

```typescript
// In authSlice - token is automatically injected into API calls
apiClient.setAuthTokenGetter(() => {
  return get().token; // Gets current token from store
});
```

### **3. Direct AuthService Calls (Only for Public Endpoints)**

```tsx
// ❌ Don't do this for protected endpoints
await AuthService.getCurrentUser() // No Bearer token!

// ✅ Only for public endpoints 
await AuthService.requestPasswordReset({ email })
await AuthService.verifyEmail(token, email)
```

## 🚫 **Incorrect Patterns to Avoid**

### **1. Direct API Service Calls (Bypasses Token Injection)**
```tsx
// ❌ Wrong - bypasses auth store token injection
import { AuthService } from '@/services/api'
await AuthService.getCurrentUser() // No Bearer token in header!
```

### **2. Multiple Authentication Implementations**
```tsx
// ❌ Wrong - creates duplicate/conflicting logic
const useAuth = () => {
  // Custom auth logic that conflicts with authSlice
}
```

## 🔧 **Token Flow**

1. **Login**: `authSlice.loginWithCredentials()` 
   - Calls `AuthService.login()`
   - Stores token in localStorage + cookies
   - Sets up `apiClient.setAuthTokenGetter()`

2. **Protected API Calls**: `authSlice.getCurrentUser()`
   - Calls `AuthService.getCurrentUser()`
   - `apiClient` automatically adds `Authorization: Bearer {token}` 
   - Token comes from current auth state

3. **Token Refresh**: `authSlice.refreshAuthToken()`
   - Uses stored refresh token
   - Updates auth state with new tokens
   - `apiClient` automatically uses new token

## 🎯 **Authentication Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Components    │───▶│   AuthSlice      │───▶│  AuthService    │
│                 │    │                  │    │                 │
│ - Login Forms   │    │ - State Mgmt     │    │ - API Calls     │
│ - User Profile  │    │ - Token Storage  │    │ - Request/Resp  │
│ - Protected UI  │    │ - API Client     │    │ - Error Handling│
└─────────────────┘    │   Setup          │    └─────────────────┘
                       └──────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   localStorage   │    │   API Client    │
                       │   + cookies      │    │                 │
                       └──────────────────┘    │ - Auto Headers  │
                                              │ - Token Inject  │
                                              │ - Error Handle  │
                                              └─────────────────┘
```

## 🧪 **Testing**

The test page (`/test`) demonstrates proper usage:

- ✅ All protected endpoints use `auth.methodName()`
- ✅ Bearer tokens are automatically injected
- ✅ State is properly managed
- ✅ Public endpoints use direct `AuthService` calls
- ✅ Register functionality included

## 🔑 **Key Takeaways**

1. **Single Source of Truth**: Use `authSlice` for all auth operations
2. **Automatic Token Injection**: Let the system handle Bearer tokens  
3. **Proper State Management**: Auth state drives UI and API calls
4. **Public vs Protected**: Know which endpoints need authentication
5. **No Direct Service Calls**: Always go through the auth store for protected endpoints