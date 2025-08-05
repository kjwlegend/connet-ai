"use client";

import { useEffect } from "react";
import useStore from "@/store";

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { initializeAuth, login, isAuthenticated } = useStore();

  useEffect(() => {
    // Initialize authentication on app startup
    initializeAuth().then(() => {
      // TEMPORARY: Auto-login with mock admin user for development
      // Remove this when authentication is ready for production
      const { isAuthenticated: currentAuth } = useStore.getState();
      if (!currentAuth) {
        console.log('🔧 Development Mode: Auto-authenticating with mock admin user');
        const mockAdminUser = {
          id: 'admin-backdoor-001',
          email: 'admin@kjwlabs.com',
          full_name: 'System Administrator',
          username: 'admin',
          is_active: true,
          invitation_code: 'ADMIN1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_login_at: new Date().toISOString(),
          permissions: ['admin', 'user'],
          roles: ['admin'],
        };
        login(mockAdminUser, 'admin-mock-token', 'admin-mock-refresh-token');
      }
    });
  }, [initializeAuth, login]);

  return <>{children}</>;
}
