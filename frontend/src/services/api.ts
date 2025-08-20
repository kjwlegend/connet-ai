import axios, { AxiosInstance, AxiosResponse, AxiosError } from "axios";
import type {
  ApiResponse,
  PaginatedResponse,
  User,
  ChatRoom,
  Message,
  Agent,
  CreateChatroomForm,
} from "@/types";

// Standardized API error shape used across the app
export interface APIError {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle common errors
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  }

  private handleUnauthorized() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      window.location.href = "/auth/login";
    }
  }

  // Generic request method
  private async request<T>(
    method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH",
    url: string,
    data?: any,
    params?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.request({
        method,
        url,
        data,
        params,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const data = error.response.data as any;
        const apiError: APIError = {
          message: data?.error?.message || data?.message || "Request failed",
          code: data?.error?.code || String(error.response.status),
          status: error.response.status,
          details: data,
        };
        throw apiError;
      }
      const networkError: APIError = {
        message: "Network error occurred",
        code: "NETWORK_ERROR",
      };
      throw networkError;
    }
  }

  // Authentication API
  async login(
    email: string,
    password: string
  ): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request("POST", "/api/v1/auth/login", { email, password });
  }

  async register(
    email: string,
    password: string,
    name: string
  ): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request("POST", "/api/v1/auth/register", {
      email,
      password,
      name,
    });
  }

  async logout(): Promise<ApiResponse<void>> {
    const result = await this.request<void>("POST", "/api/v1/auth/logout");
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
    return result;
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return this.request("POST", "/api/v1/auth/refresh");
  }

  async getProfile(): Promise<ApiResponse<User>> {
    return this.request("GET", "/api/v1/auth/profile");
  }

  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    return this.request("PUT", "/api/v1/auth/profile", data);
  }

  // Chatroom API
  async getChatrooms(
    page = 1,
    limit = 20
  ): Promise<ApiResponse<PaginatedResponse<ChatRoom>>> {
    return this.request("GET", "/api/v1/chatrooms", null, { page, limit });
  }

  async getChatroom(id: string): Promise<ApiResponse<ChatRoom>> {
    return this.request("GET", `/api/v1/chatrooms/${id}`);
  }

  async createChatroom(
    data: CreateChatroomForm
  ): Promise<ApiResponse<ChatRoom>> {
    return this.request("POST", "/api/v1/chatrooms", data);
  }

  async updateChatroom(
    id: string,
    data: Partial<ChatRoom>
  ): Promise<ApiResponse<ChatRoom>> {
    return this.request("PUT", `/api/v1/chatrooms/${id}`, data);
  }

  async deleteChatroom(id: string): Promise<ApiResponse<void>> {
    return this.request("DELETE", `/api/v1/chatrooms/${id}`);
  }

  async joinChatroom(id: string): Promise<ApiResponse<ChatRoom>> {
    return this.request("POST", `/api/v1/chatrooms/${id}/join`);
  }

  async leaveChatroom(id: string): Promise<ApiResponse<void>> {
    return this.request("POST", `/api/v1/chatrooms/${id}/leave`);
  }

  // Message API
  async getMessages(
    chatroomId: string,
    page = 1,
    limit = 50,
    before?: string
  ): Promise<ApiResponse<PaginatedResponse<Message>>> {
    return this.request(
      "GET",
      `/api/v1/chatrooms/${chatroomId}/messages`,
      null,
      {
        page,
        limit,
        before,
      }
    );
  }

  async sendMessage(
    chatroomId: string,
    content: string,
    mentions: string[] = []
  ): Promise<ApiResponse<Message>> {
    return this.request("POST", `/api/v1/chatrooms/${chatroomId}/messages`, {
      content,
      mentions,
    });
  }

  async updateMessage(
    chatroomId: string,
    messageId: string,
    content: string
  ): Promise<ApiResponse<Message>> {
    return this.request(
      "PUT",
      `/api/v1/chatrooms/${chatroomId}/messages/${messageId}`,
      {
        content,
      }
    );
  }

  async deleteMessage(
    chatroomId: string,
    messageId: string
  ): Promise<ApiResponse<void>> {
    return this.request(
      "DELETE",
      `/api/v1/chatrooms/${chatroomId}/messages/${messageId}`
    );
  }

  // Agent API
  async getAgents(specialty?: string): Promise<ApiResponse<Agent[]>> {
    return this.request("GET", "/api/v1/agents", null, { specialty });
  }

  async getAgent(id: string): Promise<ApiResponse<Agent>> {
    return this.request("GET", `/api/v1/agents/${id}`);
  }

  async searchAgents(query: string, limit = 10): Promise<ApiResponse<Agent[]>> {
    return this.request("GET", "/api/v1/agents/search", null, { query, limit });
  }

  async mentionAgent(
    chatroomId: string,
    agentId: string,
    context?: string
  ): Promise<ApiResponse<void>> {
    return this.request(
      "POST",
      `/api/v1/chatrooms/${chatroomId}/agents/${agentId}/mention`,
      {
        context,
      }
    );
  }

  async addAgentToChatroom(
    chatroomId: string,
    agentId: string
  ): Promise<ApiResponse<ChatRoom>> {
    return this.request(
      "POST",
      `/api/v1/chatrooms/${chatroomId}/agents/${agentId}`
    );
  }

  async removeAgentFromChatroom(
    chatroomId: string,
    agentId: string
  ): Promise<ApiResponse<void>> {
    return this.request(
      "DELETE",
      `/api/v1/chatrooms/${chatroomId}/agents/${agentId}`
    );
  }

  async getAgentStatus(
    agentId: string
  ): Promise<ApiResponse<{ status: string; lastActive: Date }>> {
    return this.request("GET", `/api/v1/agents/${agentId}/status`);
  }

  async requestAgentCollaboration(
    chatroomId: string,
    agentIds: string[],
    task: string,
    priority: "low" | "medium" | "high" = "medium"
  ): Promise<ApiResponse<void>> {
    return this.request(
      "POST",
      `/api/v1/chatrooms/${chatroomId}/collaboration`,
      {
        agentIds,
        task,
        priority,
      }
    );
  }

  // User management (for admins)
  async getUsers(
    page = 1,
    limit = 20
  ): Promise<ApiResponse<PaginatedResponse<User>>> {
    return this.request("GET", "/api/v1/users", null, { page, limit });
  }

  async getUser(id: string): Promise<ApiResponse<User>> {
    return this.request("GET", `/api/v1/users/${id}`);
  }

  async updateUser(
    id: string,
    data: Partial<User>
  ): Promise<ApiResponse<User>> {
    return this.request("PUT", `/api/v1/users/${id}`, data);
  }

  async deleteUser(id: string): Promise<ApiResponse<void>> {
    return this.request("DELETE", `/api/v1/users/${id}`);
  }

  // Analytics and monitoring
  async getChatroomAnalytics(chatroomId: string): Promise<
    ApiResponse<{
      messageCount: number;
      participantCount: number;
      avgResponseTime: number;
      agentUtilization: Record<string, number>;
    }>
  > {
    return this.request("GET", `/api/v1/chatrooms/${chatroomId}/analytics`);
  }

  async getSystemHealth(): Promise<
    ApiResponse<{
      status: "healthy" | "degraded" | "down";
      uptime: number;
      activeConnections: number;
      queueSize: number;
    }>
  > {
    return this.request("GET", "/api/v1/health");
  }

  // File upload (if needed)
  async uploadFile(
    file: File,
    chatroomId?: string
  ): Promise<
    ApiResponse<{
      url: string;
      filename: string;
      size: number;
    }>
  > {
    const formData = new FormData();
    formData.append("file", file);
    if (chatroomId) {
      formData.append("chatroomId", chatroomId);
    }

    return this.request("POST", "/api/v1/upload", formData);
  }
}

// Export singleton instance
export const apiClient = new ApiService();
