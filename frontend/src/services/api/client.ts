/**
 * Enhanced API Client with authentication, caching, and error handling
 */

import { ApiResponse, ApiError, ServiceConfig } from "../types";

export interface RouteConfig {
  // Map service patterns to routing strategy
  // 'direct' = call BFF directly, 'proxy' = use Next.js API routes
  serviceRoutes: Record<string, "direct" | "proxy">;
  // Next.js API route prefix (for proxy mode)
  nextApiPrefix: string;
  // Direct BFF base URL (for direct mode)
  bffBaseUrl: string;
}

class ApiClient {
  private config: ServiceConfig;
  private routeConfig: RouteConfig;
  private cache = new Map<string, any>();
  private getAuthToken: (() => string | null) | null = null;
  private interceptors: {
    request: Array<(config: RequestInit) => RequestInit | Promise<RequestInit>>;
    response: Array<(response: Response) => Response | Promise<Response>>;
  } = {
    request: [],
    response: [],
  };

  constructor(
    config: Partial<ServiceConfig> = {},
    routeConfig?: Partial<RouteConfig>
  ) {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
      timeout: 10000,
      retries: 3,
      retryDelay: 1000,
      ...config,
    };

    // Default route configuration
    this.routeConfig = {
      serviceRoutes: {
        "/api/v1/auth": "direct", // Auth directly to BFF
        "/api/v1/ai": "direct", // AI services directly to BFF
        "/api/v1/chat": "direct", // Chat directly to BFF
        "/api/webhooks": "proxy", // Webhooks through Next.js
        "/api/uploads": "proxy", // File uploads through Next.js
        "/api/oauth/callback": "proxy", // OAuth callbacks through Next.js
      },
      nextApiPrefix: "/api",
      bffBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
      ...routeConfig,
    };

    // Add default interceptors
    this.addRequestInterceptor(this.addAuthHeader.bind(this));
    this.addResponseInterceptor(this.handleResponseErrors.bind(this));
  }

  // Set function to get auth token
  setAuthTokenGetter(getter: () => string | null) {
    this.getAuthToken = getter;
  }

  // Update route configuration
  updateRouteConfig(routeConfig: Partial<RouteConfig>) {
    this.routeConfig = { ...this.routeConfig, ...routeConfig };
  }

  // Resolve endpoint URL based on routing strategy
  private resolveEndpointUrl(endpoint: string): string {
    // Find matching route pattern
    const matchingPattern = Object.keys(this.routeConfig.serviceRoutes).find(
      (pattern) => endpoint.startsWith(pattern)
    );

    const routingStrategy = matchingPattern
      ? this.routeConfig.serviceRoutes[matchingPattern]
      : "direct"; // Default to direct

    if (routingStrategy === "proxy") {
      // Use Next.js API routes
      return `${this.routeConfig.nextApiPrefix}${endpoint}`;
    } else {
      // Use direct BFF URL
      return `${this.routeConfig.bffBaseUrl}${endpoint}`;
    }
  }

  addRequestInterceptor(
    interceptor: (config: RequestInit) => RequestInit | Promise<RequestInit>
  ) {
    this.interceptors.request.push(interceptor);
  }

  addResponseInterceptor(
    interceptor: (response: Response) => Response | Promise<Response>
  ) {
    this.interceptors.response.push(interceptor);
  }

  private async addAuthHeader(config: RequestInit): Promise<RequestInit> {
    // Get token from auth token getter first, then fallback to persisted store
    let token = null;

    if (this.getAuthToken) {
      token = this.getAuthToken();
    }

    // If no token from getter or getter not set, fallback to persisted store data
    if (!token && typeof window !== "undefined") {
      try {
        // Try to get from categorized storage system
        const storageCategories = ['permanent', 'cache', 'session', 'temporary'];
        let persistedStore = null;
        
        // Search through storage categories
        for (const category of storageCategories) {
          const categoryKey = `${category}:connet-ai-store`;
          const data = localStorage.getItem(categoryKey);
          if (data) {
            persistedStore = data;
            break;
          }
        }
        
        // Fallback to direct key (legacy or non-categorized)
        if (!persistedStore) {
          persistedStore = localStorage.getItem("connet-ai-store");
        }

        if (persistedStore) {
          const storeData = JSON.parse(persistedStore);
          // Handle both nested state structure and direct auth structure
          if (storeData?.state?.auth?.token) {
            token = storeData.state.auth.token;
          } else if (storeData?.auth?.token) {
            token = storeData.auth.token;
          }
        }

        // Legacy fallback for old token storage
        if (!token) {
          token = localStorage.getItem("auth_token");
        }
      } catch (error) {
        console.warn("Failed to parse persisted store data:", error);
        // Fallback to legacy token storage
        token = localStorage.getItem("auth_token");
      }
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(config.headers as Record<string, string>),
    };

    // Add Authorization header if token exists
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return {
      ...config,
      headers,
    };
  }

  private async handleResponseErrors(response: Response): Promise<Response> {
    if (!response.ok) {
      const error: ApiError = {
        code: response.status.toString(),
        message: response.statusText,
        timestamp: new Date().toISOString(),
      };

      try {
        const errorData = await response.json();
        // Handle FastAPI error format: {"detail": "error message"}
        if (errorData.detail) {
          error.message = errorData.detail;
        } else if (errorData.message) {
          error.message = errorData.message;
        } else if (typeof errorData === "string") {
          error.message = errorData;
        }
        error.details = errorData.details || errorData;
      } catch {
        // Response is not JSON, use default error
      }

      throw error;
    }
    return response;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<ApiResponse<T>> {
    const url = this.resolveEndpointUrl(endpoint);

    try {
      // Apply request interceptors
      let config = { ...options };
      for (const interceptor of this.interceptors.request) {
        config = await interceptor(config);
      }

      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        this.config.timeout
      );

      const requestConfig: RequestInit = {
        ...config,
        credentials: config.credentials ?? 'include',
        signal: controller.signal,
      };

      let response = await fetch(url, requestConfig);

      clearTimeout(timeoutId);

      // Apply response interceptors
      for (const interceptor of this.interceptors.response) {
        response = await interceptor(response);
      }

      const data = await response.json();

      return {
        data,
        success: true,
        message: "Request successful",
      };
    } catch (error) {
      // Handle network errors and retries
      if (retryCount < this.config.retries && this.shouldRetry(error)) {
        await this.delay(this.config.retryDelay * Math.pow(2, retryCount));
        return this.request<T>(endpoint, options, retryCount + 1);
      }

      // Re-throw API errors
      if (error instanceof Error && "code" in error) {
        throw error;
      }

      // Handle other errors
      throw {
        code: "NETWORK_ERROR",
        message:
          error instanceof Error ? error.message : "Network request failed",
        timestamp: new Date().toISOString(),
      } as ApiError;
    }
  }

  private shouldRetry(error: any): boolean {
    if (error?.name === "AbortError") return false; // Don't retry timeouts
    if (error?.code === "401" || error?.code === "403") return false; // Don't retry auth errors
    return true;
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // HTTP Methods
  async get<T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    const url = params
      ? `${endpoint}?${new URLSearchParams(params).toString()}`
      : endpoint;
    return this.request<T>(url, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // Cache methods
  getCacheKey(endpoint: string, params?: any): string {
    return params ? `${endpoint}:${JSON.stringify(params)}` : endpoint;
  }

  getFromCache<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  setCache<T>(key: string, data: T, ttl = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  clearCache(pattern?: string): void {
    if (pattern) {
      const regex = new RegExp(pattern);
      for (const [key] of this.cache.entries()) {
        if (regex.test(key)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();

// Export types
export type { ApiClient, RouteConfig };
export { ApiClient as ApiClientClass };
