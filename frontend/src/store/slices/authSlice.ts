import { StateCreator } from "zustand";
import { StoreState } from "../types";
import { StorageUtil } from "@/lib/utils/storage";
import { STORAGE_KEYS } from "@/lib/config/constants";
import {
  AuthAPI,
  OAuthUrlRequest,
  OAuthCallbackRequest,
} from "@/services/api/auth";
import { apiClient } from "@/services/api";
import { RegisterRequest } from "@/types/api";
import { RegisterResponse } from "@/services/api/auth";
import type { APIError } from "@/services/api";

// Runtime-safe API error guard (interfaces don't exist at runtime)
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

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (userData: User, token: string, refreshToken?: string) => void;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void;
  initializeAuth: () => Promise<void>;
  loginWithCredentials: (
    email: string,
    password: string,
    rememberMe?: boolean
  ) => Promise<void>;
  registerWithCredentials: (data: RegisterRequest) => Promise<RegisterResponse>;
  validateToken: () => Promise<boolean>;
  refreshAuthToken: () => Promise<boolean>;
  getCurrentUser: () => Promise<void>;
  getOAuthUrl: (
    provider: "google" | "github",
    redirectUri: string
  ) => Promise<{ url: string; state: string }>;
  handleOAuthCallback: (
    provider: "google" | "github",
    code: string,
    state: string,
    redirectUri: string
  ) => Promise<void>;
  loginWithOAuth: (provider: "google" | "github") => Promise<void>;
}

export type AuthSlice = AuthState & AuthActions;

const createAuthSlice: StateCreator<StoreState, [], [], AuthSlice> = (
  set,
  get
) => {
  // Set up API client auth token getter (only on client side)
  if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
    apiClient.setAuthTokenGetter(() => {
      return get().token;
    });
  }

  return {
    // State
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    // Actions
    login: (userData, token, refreshToken) => {
      console.log("login method called with user:", userData.email);

      StorageUtil.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
      if (refreshToken) {
        StorageUtil.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
      }

      // Also store token in cookie for middleware access
      document.cookie = `auth_token=${token}; path=/; max-age=${
        60 * 60 * 24 * 7
      }; secure; samesite=strict`;
      if (refreshToken) {
        document.cookie = `auth_refresh_token=${refreshToken}; path=/; max-age=${
          60 * 60 * 24 * 30
        }; secure; samesite=strict`;
      }

      set({
        user: userData,
        token,
        refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      // Ensure API client has the new token immediately
      if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
        apiClient.setAuthTokenGetter(() => {
          return get().token;
        });
      }

      console.log("login method completed, isAuthenticated:", true);
    },

    logout: async () => {
      const { token } = get();

      try {
        // Call logout API if we have a token
        if (token) {
          await AuthAPI.logout();
        }
      } catch (error) {
        console.error("Logout API call failed:", error);
        // Continue with local logout even if API call fails
      } finally {
        // Always clean up local state
        StorageUtil.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        StorageUtil.removeItem(STORAGE_KEYS.REFRESH_TOKEN);

        // Clear cookies as well
        document.cookie =
          "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        document.cookie =
          "auth_refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      }
    },

    setUser: (user) => {
      set({ user });
    },

    setLoading: (isLoading) => {
      set({ isLoading });
    },

    setError: (error) => {
      set({ error, isLoading: false });
    },

    clearError: () => {
      set({ error: null });
    },

    updateUserPreferences: (preferences) => {
      const { user } = get();
      if (user) {
        const updatedUser = {
          ...user,
          preferences: {
            ...user.preferences,
            ...preferences,
          },
        };
        set({ user: updatedUser });
      }
    },

    initializeAuth: async () => {
      const token = StorageUtil.getItem<string>(STORAGE_KEYS.AUTH_TOKEN);
      const refreshToken = StorageUtil.getItem<string>(
        STORAGE_KEYS.REFRESH_TOKEN
      );

      console.log("token", token, "refreshtoekn", refreshToken);

      if (token) {
        // Set cookies to sync with middleware
        document.cookie = `auth_token=${token}; path=/; max-age=${
          60 * 60 * 24 * 7
        }; secure; samesite=strict`;
        if (refreshToken) {
          document.cookie = `auth_refresh_token=${refreshToken}; path=/; max-age=${
            60 * 60 * 24 * 30
          }; secure; samesite=strict`;
        }

        set({
          token,
          refreshToken,
          isAuthenticated: true,
          isLoading: true,
        });

        // Ensure API client has the token from localStorage
        if (typeof window !== "undefined" && apiClient?.setAuthTokenGetter) {
          apiClient.setAuthTokenGetter(() => {
            return get().token;
          });
        }

        try {
          // Try to get current user to validate the token
          await get().getCurrentUser();
          set({ isLoading: false });
        } catch (error) {
          // Token is invalid, try to refresh
          const refreshSuccess = await get().refreshAuthToken();
          if (!refreshSuccess) {
            // Refresh failed, logout
            await get().logout();
          }
          set({ isLoading: false });
        }
      } else {
        // No token found, set loading to false
        set({ isLoading: false });
      }
    },

    loginWithCredentials: async (
      email: string,
      password: string,
      rememberMe = false
    ) => {
      const { login, setError, setLoading } = get();

      try {
        console.log("loginWithCredentials called with:", email);
        setLoading(true);
        setError(null);

        const response = await AuthAPI.login({ email, password });

        login(
          response.user,
          response.access_token,
          rememberMe ? response.refresh_token : undefined
        );
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Login failed. Please try again.";
        setError(errorMessage);
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

        const registerResponse = await AuthAPI.register(data);

        // Don't auto-login after registration since email verification is required
        // The UI will show the email verification flow instead

        return registerResponse; // Return response for the UI to handle
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Registration failed. Please try again.";
        setError(errorMessage);
        throw error;
      } finally {
        setLoading(false);
      }
    },

    validateToken: async () => {
      const { token } = get();

      if (!token) {
        return false;
      }

      try {
        const response = await AuthAPI.verifyToken({ token });
        return response.valid;
      } catch (error) {
        return false;
      }
    },

    refreshAuthToken: async () => {
      const { refreshToken, login, logout } = get();

      if (!refreshToken) {
        return false;
      }

      try {
        const response = await AuthAPI.refreshToken({
          refresh_token: refreshToken,
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
      const { token } = get();

      try {
        const user = await AuthAPI.getCurrentUser();
        get().setUser(user);
      } catch (error) {
        throw error;
      }
    },

    getOAuthUrl: async (provider: "google" | "github", redirectUri: string) => {
      try {
        get().setError(null);

        const response = await AuthAPI.getOAuthUrl({
          provider,
          redirect_uri: redirectUri,
        });

        return {
          url: response.url,
          state: response.state,
        };
      } catch (error) {
        const errorMessage = isAPIError(error)
          ? error.message
          : `Failed to get ${provider} OAuth URL`;
        get().setError(errorMessage);
        throw error;
      }
    },

    handleOAuthCallback: async (
      provider: "google" | "github",
      code: string,
      state: string,
      redirectUri: string
    ) => {
      const { login, setError, setLoading } = get();

      try {
        setLoading(true);
        setError(null);

        const response = await AuthAPI.oauthCallback({
          provider,
          code,
          state,
          redirect_uri: redirectUri,
        });

        // Login user with OAuth response
        login(response.user, response.access_token, response.refresh_token);

        // Return whether user is new for potential onboarding flow
        return { isNewUser: response.is_new_user };
      } catch (error) {
        const errorMessage = isAPIError(error)
          ? error.message
          : `${provider} authentication failed`;
        setError(errorMessage);
        throw error;
      } finally {
        setLoading(false);
      }
    },

    loginWithOAuth: async (provider: "google" | "github") => {
      try {
        get().setLoading(true);
        get().setError(null);

        // Get current URL origin for redirect
        const redirectUri = `${window.location.origin}/auth/callback`;

        // Get OAuth URL
        const { url } = await get().getOAuthUrl(provider, redirectUri);

        // Redirect to OAuth provider
        window.location.href = url;
      } catch (error) {
        get().setLoading(false);
        const errorMessage = isAPIError(error)
          ? error.message
          : `Failed to initialize ${provider} login`;
        get().setError(errorMessage);
        throw error;
      }
    },
  };
};

export default createAuthSlice;
