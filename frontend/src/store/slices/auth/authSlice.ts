/**
 * Enhanced Auth Slice for New Store Architecture
 * Features:
 * - Proper persistence with selective storage
 * - Better error handling
 * - Optimized performance
 * - Type-safe operations
 */

import { StateCreator } from "zustand";
import { StorageUtil } from "@/lib/utils/storage";
import { STORAGE_KEYS } from "@/lib/config/constants";
import {
  AuthService,
  apiClient,
  type OAuthUrlRequest,
  type OAuthCallbackRequest,
  type RegisterRequest,
  type RegisterResponse,
  type APIError
} from "@/services/api";

// Runtime-safe API error guard
const isAPIError = (e: unknown): e is APIError =>
  typeof e === "object" && e !== null && "message" in e;

export interface User {
  id: string;
  email: string;
  full_name: string;
  username?: string;
  is_active: boolean;
  invitation_code?: string;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
  permissions: string[];
  roles: string[];
  avatar?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: "light" | "dark" | "system";
  language: "en" | "zh";
  notifications: {
    email: boolean;
    push: boolean;
    mentions: boolean;
  };
}

// Enhanced auth state with better structure
export interface AuthState {
  // Core auth data
  auth: {
    user: User | null;
    token: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    sessionStarted: Date | null;
    lastActivity: Date | null;
  };
  
  // UI state
  ui: {
    isLoading: boolean;
    isInitializing: boolean;
    showLoginModal: boolean;
  };
  
  // Error state
  error: {
    current: string | null;
    history: Array<{
      message: string;
      timestamp: Date;
      action: string;
    }>;
  };
}

export interface AuthActions {
  // Core actions
  login: (userData: User, token: string, refreshToken?: string) => void;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
  
  // UI actions  
  setLoading: (loading: boolean) => void;
  setInitializing: (initializing: boolean) => void;
  toggleLoginModal: (show?: boolean) => void;
  
  // Error actions
  setError: (error: string | null, action?: string) => void;
  clearError: () => void;
  clearErrorHistory: () => void;
  
  // Preferences
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void;
  
  // Auth operations
  initializeAuth: () => Promise<void>;
  loginWithCredentials: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  registerWithCredentials: (data: RegisterRequest) => Promise<RegisterResponse>;
  validateToken: () => Promise<boolean>;
  refreshAuthToken: () => Promise<boolean>;
  getCurrentUser: () => Promise<void>;
  
  // OAuth operations
  getOAuthUrl: (provider: "google" | "github", redirectUri: string) => Promise<{ url: string; state: string }>;
  handleOAuthCallback: (provider: "google" | "github", code: string, state: string, redirectUri: string) => Promise<{ isNewUser: boolean }>;
  loginWithOAuth: (provider: "google" | "github") => Promise<void>;
  
  // Password reset operations
  requestPasswordReset: (email: string) => Promise<void>;
  
  // Session management
  extendSession: () => void;
  checkSessionTimeout: () => boolean;
  resetSession: () => void;
}

export type AuthSlice = AuthState & AuthActions;

// Initial state
const initialAuthState: AuthState = {
  auth: {
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    sessionStarted: null,
    lastActivity: null,
  },
  ui: {
    isLoading: false,
    isInitializing: false,
    showLoginModal: false,
  },
  error: {
    current: null,
    history: [],
  },
};

const createAuthSlice: StateCreator<AuthSlice, [], [], AuthSlice> = (set, get) => {
  // Set up API client auth token getter (only on client side)
  if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
    apiClient.setAuthTokenGetter(() => {
      return get().auth.token;
    });
  }

  return {
    ...initialAuthState,

    // Core actions
    login: (userData, token, refreshToken) => {
      const now = new Date();
      
      // Store tokens
      StorageUtil.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
      if (refreshToken) {
        StorageUtil.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
      }

      // Store in cookies for middleware access
      if (typeof document !== "undefined") {
        document.cookie = `auth_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; secure; samesite=strict`;
        if (refreshToken) {
          document.cookie = `auth_refresh_token=${refreshToken}; path=/; max-age=${60 * 60 * 24 * 30}; secure; samesite=strict`;
        }
      }

      set(state => ({
        auth: {
          ...state.auth,
          user: userData,
          token,
          refreshToken,
          isAuthenticated: true,
          sessionStarted: now,
          lastActivity: now,
        },
        ui: {
          ...state.ui,
          isLoading: false,
          showLoginModal: false,
        },
        error: {
          ...state.error,
          current: null,
        },
      }));

      // Ensure API client has the new token immediately
      if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
        apiClient.setAuthTokenGetter(() => get().auth.token);
      }
    },

    logout: async () => {
      const { auth } = get();

      try {
        // Call logout API if we have a token
        if (auth.token) {
          await AuthService.logout();
        }
      } catch (error) {
        console.error("Logout API call failed:", error);
        // Continue with local logout even if API call fails
      } finally {
        // Always clean up local state
        StorageUtil.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        StorageUtil.removeItem(STORAGE_KEYS.REFRESH_TOKEN);

        // Clear cookies
        if (typeof document !== "undefined") {
          document.cookie = "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
          document.cookie = "auth_refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        }

        set(state => ({
          auth: {
            ...initialAuthState.auth,
          },
          ui: {
            ...state.ui,
            isLoading: false,
          },
          error: {
            ...state.error,
            current: null,
          },
        }));
      }
    },

    setUser: (user) => {
      set(state => ({
        auth: {
          ...state.auth,
          user,
          lastActivity: new Date(),
        }
      }));
    },

    // UI actions
    setLoading: (isLoading) => {
      set(state => ({
        ui: {
          ...state.ui,
          isLoading,
        }
      }));
    },

    setInitializing: (isInitializing) => {
      set(state => ({
        ui: {
          ...state.ui,
          isInitializing,
        }
      }));
    },

    toggleLoginModal: (show) => {
      set(state => ({
        ui: {
          ...state.ui,
          showLoginModal: show !== undefined ? show : !state.ui.showLoginModal,
        }
      }));
    },

    // Error actions
    setError: (error, action = 'unknown') => {
      set(state => ({
        error: {
          current: error,
          history: error ? [
            ...state.error.history.slice(-4), // Keep last 5 errors
            {
              message: error,
              timestamp: new Date(),
              action,
            }
          ] : state.error.history,
        },
        ui: {
          ...state.ui,
          isLoading: false,
        }
      }));
    },

    clearError: () => {
      set(state => ({
        error: {
          ...state.error,
          current: null,
        }
      }));
    },

    clearErrorHistory: () => {
      set(state => ({
        error: {
          ...state.error,
          history: [],
        }
      }));
    },

    updateUserPreferences: (preferences) => {
      const { auth } = get();
      if (auth.user) {
        const updatedUser = {
          ...auth.user,
          preferences: {
            ...auth.user.preferences,
            ...preferences,
          },
        };
        get().setUser(updatedUser);
      }
    },

    // Session management
    extendSession: () => {
      set(state => ({
        auth: {
          ...state.auth,
          lastActivity: new Date(),
        }
      }));
    },

    checkSessionTimeout: () => {
      const { auth } = get();
      if (!auth.lastActivity) return false;
      
      const timeout = 30 * 60 * 1000; // 30 minutes
      return Date.now() - auth.lastActivity.getTime() > timeout;
    },

    resetSession: () => {
      set(state => ({
        auth: {
          ...state.auth,
          sessionStarted: new Date(),
          lastActivity: new Date(),
        }
      }));
    },

    // Auth operations (same as before but with enhanced error handling)
    initializeAuth: async () => {
      const { setError, setInitializing } = get();
      
      setInitializing(true);
      
      const token = StorageUtil.getItem<string>(STORAGE_KEYS.AUTH_TOKEN);
      const refreshToken = StorageUtil.getItem<string>(STORAGE_KEYS.REFRESH_TOKEN);

      if (token) {
        // Set cookies to sync with middleware
        if (typeof document !== "undefined") {
          document.cookie = `auth_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; secure; samesite=strict`;
          if (refreshToken) {
            document.cookie = `auth_refresh_token=${refreshToken}; path=/; max-age=${60 * 60 * 24 * 30}; secure; samesite=strict`;
          }
        }

        set(state => ({
          auth: {
            ...state.auth,
            token,
            refreshToken,
            isAuthenticated: true,
          },
          ui: {
            ...state.ui,
            isLoading: true,
          }
        }));

        // Ensure API client has the token from localStorage
        if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
          apiClient.setAuthTokenGetter(() => get().auth.token);
        }

        try {
          // Try to get current user to validate the token
          await get().getCurrentUser();
        } catch (error) {
          // Token is invalid, try to refresh
          const refreshSuccess = await get().refreshAuthToken();
          if (!refreshSuccess) {
            // Refresh failed, logout
            await get().logout();
          }
        }
      }
      
      setInitializing(false);
    },

    loginWithCredentials: async (email: string, password: string, rememberMe = false) => {
      const { login, setError, setLoading } = get();

      try {
        setLoading(true);
        setError(null);

        const response = await AuthService.login({ email, password });

        login(
          response.user,
          response.access_token,
          rememberMe ? response.refresh_token : undefined
        );
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Login failed. Please try again.";
        setError(errorMessage, 'loginWithCredentials');
        throw error;
      } finally {
        setLoading(false);
      }
    },

    registerWithCredentials: async (data: RegisterRequest) => {
      const { setError, setLoading } = get();

      try {
        setLoading(true);
        setError(null);

        const registerResponse = await AuthService.register(data);

        // Don't auto-login after registration since email verification is required
        return registerResponse;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Registration failed. Please try again.";
        setError(errorMessage, 'registerWithCredentials');
        throw error;
      } finally {
        setLoading(false);
      }
    },

    validateToken: async () => {
      const { auth } = get();

      if (!auth.token) {
        return false;
      }

      try {
        const response = await AuthService.verifyToken({ token: auth.token });
        return response.valid;
      } catch (error) {
        return false;
      }
    },

    refreshAuthToken: async () => {
      const { auth, login, logout } = get();

      if (!auth.refreshToken) {
        return false;
      }

      try {
        const response = await AuthService.refreshToken({
          refresh_token: auth.refreshToken,
        });

        login(response.user, response.access_token, response.refresh_token);
        return true;
      } catch (error) {
        // Refresh failed, logout user
        await logout();
        return false;
      }
    },

    getCurrentUser: async () => {
      try {
        const user = await AuthService.getCurrentUser();
        get().setUser(user);
      } catch (error) {
        throw error;
      }
    },

    getOAuthUrl: async (provider: "google" | "github", redirectUri: string) => {
      const { setError } = get();
      
      try {
        setError(null);

        const response = await AuthService.getOAuthUrl({
          provider,
          redirect_uri: redirectUri,
        });

        return {
          url: response.url,
          state: response.state,
        };
      } catch (error) {
        const errorMessage = isAPIError(error) ? error.message : `Failed to get ${provider} OAuth URL`;
        setError(errorMessage, 'getOAuthUrl');
        throw error;
      }
    },

    handleOAuthCallback: async (provider: "google" | "github", code: string, state: string, redirectUri: string) => {
      const { login, setError, setLoading } = get();

      try {
        setLoading(true);
        setError(null);

        const response = await AuthService.oauthCallback({
          provider,
          code,
          state,
          redirect_uri: redirectUri,
        });

        // Login user with OAuth response
        login(response.user, response.access_token, response.refresh_token);

        // Return whether user is new for potential onboarding flow
        return { isNewUser: response.is_new_user || false };
      } catch (error) {
        const errorMessage = isAPIError(error) ? error.message : `${provider} authentication failed`;
        setError(errorMessage, 'handleOAuthCallback');
        throw error;
      } finally {
        setLoading(false);
      }
    },

    loginWithOAuth: async (provider: "google" | "github") => {
      const { setLoading, setError, getOAuthUrl } = get();
      
      try {
        setLoading(true);
        setError(null);

        // Get current URL origin for redirect
        const redirectUri = `${window.location.origin}/auth/callback`;

        // Get OAuth URL
        const { url } = await getOAuthUrl(provider, redirectUri);

        // Redirect to OAuth provider
        window.location.href = url;
      } catch (error) {
        setLoading(false);
        const errorMessage = isAPIError(error) ? error.message : `Failed to initialize ${provider} login`;
        setError(errorMessage, 'loginWithOAuth');
        throw error;
      }
    },

    // Password reset operations
    requestPasswordReset: async (email: string) => {
      const { setError, setLoading } = get();

      try {
        setLoading(true);
        setError(null);

        await AuthService.requestPasswordReset({ email });
      } catch (error) {
        const errorMessage = isAPIError(error) ? error.message : "Failed to send password reset email. Please try again.";
        setError(errorMessage, 'requestPasswordReset');
        throw error;
      } finally {
        setLoading(false);
      }
    },
  };
};

export default createAuthSlice;