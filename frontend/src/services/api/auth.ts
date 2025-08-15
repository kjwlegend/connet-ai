import { apiClient } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface VerifyTokenRequest {
  token: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface RegisterResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  created_at: string;
}

export interface VerifyTokenResponse {
  valid: boolean;
  user?: User;
}

export interface MessageResponse {
  message: string;
}

export interface OAuthUrlRequest {
  provider: "google" | "github";
  redirect_uri: string;
  state?: string;
}

export interface OAuthUrlResponse {
  url: string;
  state: string;
}

export interface OAuthCallbackRequest {
  provider: "google" | "github";
  code: string;
  state?: string;
  redirect_uri: string;
}

export interface OAuthLoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  is_new_user: boolean;
}

export class AuthAPI {
  private static client = apiClient;

  /**
   * 用户注册
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.client.post<RegisterResponse>(
      "/auth/register",
      data
    );
    return response.data;
  }

  /**
   * 用户登录
   */
  static async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>("/auth/login", data);
    return response.data;
  }

  /**
   * 刷新访问令牌
   */
  static async refreshToken(
    data: RefreshTokenRequest
  ): Promise<RefreshTokenResponse> {
    const response = await this.client.post<RefreshTokenResponse>(
      "/auth/refresh",
      data
    );
    return response.data;
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>("/auth/me");
    return response.data;
  }

  /**
   * 用户登出
   */
  static async logout(): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      "/auth/logout",
      {}
    );
    return response.data;
  }

  /**
   * 密码重置请求
   */
  static async requestPasswordReset(
    data: PasswordResetRequest
  ): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      "/auth/password-reset",
      data
    );
    return response.data;
  }

  /**
   * 验证邮箱
   */
  static async verifyEmail(
    token: string,
    email: string
  ): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      `/auth/verify-email?token=${encodeURIComponent(
        token
      )}&email=${encodeURIComponent(email)}`,
      {}
    );
    return response.data;
  }

  /**
   * 验证令牌
   */
  static async verifyToken(
    data: VerifyTokenRequest
  ): Promise<VerifyTokenResponse> {
    const response = await this.client.post<VerifyTokenResponse>(
      "/auth/verify",
      data
    );
    return response.data;
  }

  /**
   * 获取 OAuth 授权 URL
   */
  static async getOAuthUrl(data: OAuthUrlRequest): Promise<OAuthUrlResponse> {
    const response = await this.client.get<OAuthUrlResponse>(
      "/auth/oauth/url",
      {
        params: data,
      }
    );
    return response.data;
  }

  /**
   * OAuth 回调处理
   */
  static async oauthCallback(
    data: OAuthCallbackRequest
  ): Promise<OAuthLoginResponse> {
    const response = await this.client.post<OAuthLoginResponse>(
      "/auth/oauth/callback",
      data
    );
    return response.data;
  }
}

// Export the class
export { AuthAPI as default };
