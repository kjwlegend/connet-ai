/**
 * Mock Service Worker server for testing API endpoints
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Mock API endpoints
export const handlers = [
  // Auth endpoints
  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as any;
    const { email, password } = body;

    if (email === 'test@example.com' && password === 'password123') {
      return HttpResponse.json({
        user: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          username: 'testuser',
          is_active: true,
          is_verified: true,
          permissions: ['read', 'write'],
          roles: ['user'],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        message: 'Login successful'
      });
    }

    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post('/api/auth/register', async ({ request }) => {
    const body = await request.json() as any;
    const { email, password, full_name, username } = body;

    if (email === 'existing@example.com') {
      return HttpResponse.json(
        { error: 'Email already exists' },
        { status: 400 }
      );
    }

    return HttpResponse.json({
      user: {
        id: '2',
        email,
        full_name: full_name || username,
        username,
        is_active: true,
        is_verified: false,
        permissions: ['read'],
        roles: ['user'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      message: 'Registration successful'
    });
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json({ message: 'Logout successful' });
  }),

  http.get('/api/auth/me', () => {
    return HttpResponse.json({
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User',
      username: 'testuser',
      is_active: true,
      is_verified: true,
      permissions: ['read', 'write'],
      roles: ['user'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }),
];

export const server = setupServer(...handlers);