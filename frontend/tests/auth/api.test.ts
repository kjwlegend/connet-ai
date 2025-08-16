/**
 * Authentication API integration tests
 */

import { AuthAPI } from '@/services/api/auth';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

describe('Authentication API', () => {
  describe('Login', () => {
    it('should login with valid credentials', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'password123'
      };

      const response = await AuthAPI.login(loginData);

      expect(response.user.email).toBe('test@example.com');
      expect(response.user.full_name).toBe('Test User');
      expect(response.user.username).toBe('testuser');
      expect(response.user.is_active).toBe(true);
      expect(response.user.is_verified).toBe(true);
      expect(response.user.permissions).toContain('read');
      expect(response.user.permissions).toContain('write');
      expect(response.user.roles).toContain('user');
      expect(response.message).toBe('Login successful');
    });

    it('should reject invalid credentials', async () => {
      const loginData = {
        email: 'wrong@example.com',
        password: 'wrongpassword'
      };

      await expect(AuthAPI.login(loginData)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('Registration', () => {
    it('should register new user with complete data', async () => {
      const registerData = {
        email: 'newuser@example.com',
        password: 'password123',
        full_name: 'New User',
        username: 'newuser',
        invited_by_code: 'INVITE123',
        registration_source: 'web',
        registration_channel: 'invite',
        utm_source: 'google',
        utm_medium: 'cpc',
        utm_campaign: 'signup'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('newuser@example.com');
      expect(response.user.full_name).toBe('New User');
      expect(response.user.username).toBe('newuser');
      expect(response.user.is_active).toBe(true);
      expect(response.user.is_verified).toBe(false); // New users start unverified
      expect(response.message).toBe('Registration successful');
    });

    it('should register with minimal required data', async () => {
      const registerData = {
        email: 'minimal@example.com',
        password: 'password123',
        full_name: 'Minimal User'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('minimal@example.com');
      expect(response.user.full_name).toBe('Minimal User');
      expect(response.message).toBe('Registration successful');
    });

    it('should reject registration with existing email', async () => {
      const registerData = {
        email: 'existing@example.com',
        password: 'password123',
        full_name: 'Existing User'
      };

      await expect(AuthAPI.register(registerData)).rejects.toThrow('Email already exists');
    });

    it('should handle UTM tracking parameters', async () => {
      const registerData = {
        email: 'tracked@example.com',
        password: 'password123',
        full_name: 'Tracked User',
        username: 'trackeduser',
        registration_source: 'web',
        registration_channel: 'organic',
        utm_source: 'facebook',
        utm_medium: 'social',
        utm_campaign: 'launch2024'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('tracked@example.com');
      expect(response.message).toBe('Registration successful');
    });

    it('should handle invitation code registration', async () => {
      const registerData = {
        email: 'invited@example.com',
        password: 'password123',
        full_name: 'Invited User',
        username: 'inviteduser',
        invited_by_code: 'FRIEND123',
        registration_source: 'web',
        registration_channel: 'invite'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('invited@example.com');
      expect(response.message).toBe('Registration successful');
    });
  });

  describe('User Info', () => {
    it('should get current user info', async () => {
      const user = await AuthAPI.getCurrentUser();

      expect(user.id).toBe('1');
      expect(user.email).toBe('test@example.com');
      expect(user.full_name).toBe('Test User');
      expect(user.username).toBe('testuser');
      expect(user.is_active).toBe(true);
      expect(user.is_verified).toBe(true);
      expect(user.permissions).toEqual(['read', 'write']);
      expect(user.roles).toEqual(['user']);
    });
  });

  describe('Logout', () => {
    it('should logout successfully', async () => {
      const response = await AuthAPI.logout();

      expect(response.message).toBe('Logout successful');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      // Mock a network error
      server.use(
        http.post('/api/auth/login', () => {
          return HttpResponse.error();
        })
      );

      const loginData = {
        email: 'test@example.com',
        password: 'password123'
      };

      await expect(AuthAPI.login(loginData)).rejects.toThrow();
    });

    it('should handle server errors', async () => {
      // Mock a server error
      server.use(
        http.post('/api/auth/login', () => {
          return HttpResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
          );
        })
      );

      const loginData = {
        email: 'test@example.com',
        password: 'password123'
      };

      await expect(AuthAPI.login(loginData)).rejects.toThrow();
    });

    it('should handle validation errors', async () => {
      // Mock validation error
      server.use(
        http.post('/api/auth/register', () => {
          return HttpResponse.json(
            { error: 'Email format is invalid' },
            { status: 422 }
          );
        })
      );

      const registerData = {
        email: 'invalid-email',
        password: 'password123',
        full_name: 'Test User'
      };

      await expect(AuthAPI.register(registerData)).rejects.toThrow();
    });
  });

  describe('Registration Edge Cases', () => {
    it('should handle registration without optional fields', async () => {
      const registerData = {
        email: 'simple@example.com',
        password: 'password123',
        full_name: 'Simple User'
        // No username, invitation code, or UTM parameters
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('simple@example.com');
      expect(response.user.full_name).toBe('Simple User');
      expect(response.message).toBe('Registration successful');
    });

    it('should handle username fallback for full_name', async () => {
      const registerData = {
        email: 'fallback@example.com',
        password: 'password123',
        full_name: '', // Empty full_name
        username: 'fallbackuser'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('fallback@example.com');
      expect(response.user.username).toBe('fallbackuser');
      expect(response.message).toBe('Registration successful');
    });

    it('should handle long invitation codes', async () => {
      const registerData = {
        email: 'longcode@example.com',
        password: 'password123',
        full_name: 'Long Code User',
        username: 'longcodeuser',
        invited_by_code: 'VERYLONGINVITATIONCODE123'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('longcode@example.com');
      expect(response.message).toBe('Registration successful');
    });

    it('should handle special characters in UTM parameters', async () => {
      const registerData = {
        email: 'special@example.com',
        password: 'password123',
        full_name: 'Special User',
        utm_source: 'email newsletter',
        utm_medium: 'special+campaign',
        utm_campaign: 'test&verify'
      };

      const response = await AuthAPI.register(registerData);

      expect(response.user.email).toBe('special@example.com');
      expect(response.message).toBe('Registration successful');
    });
  });
});