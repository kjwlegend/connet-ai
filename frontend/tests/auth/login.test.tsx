/**
 * Login component integration tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';
import LoginPage from '@/app/(auth)/login/page';

// Type assertion for mocked function
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

// Mock the store
const mockStore = {
  loginWithCredentials: jest.fn(),
  isLoading: false,
  error: null,
};

jest.mock('@/store', () => ({
  __esModule: true,
  default: () => mockStore,
}));

// Mock i18n
jest.mock('@/lib/i18n/client', () => ({
  useTranslations: () => (key: string) => key,
}));

// Mock OAuth components
jest.mock('@/components/auth/OAuthButton', () => ({
  OAuthButtonsGroup: ({ variant, disabled }: any) => (
    <div data-testid="oauth-buttons" data-variant={variant} data-disabled={disabled}>
      OAuth Buttons
    </div>
  ),
}));

const mockPush = jest.fn();
// Router is already mocked in setup.ts, just get the mock function
const mockRouter = {
  push: mockPush,
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
};

// Update the existing mock
mockUseRouter.mockReturnValue(mockRouter);

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockStore.loginWithCredentials.mockReset();
    mockStore.isLoading = false;
    mockStore.error = null;
  });

  it('should render login form with all required fields', () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/auth.login.emailLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.login.passwordLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.login.rememberMe/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /auth.login.loginButton/ })).toBeInTheDocument();
  });

  it('should display OAuth buttons', () => {
    render(<LoginPage />);

    const oauthButtons = screen.getByTestId('oauth-buttons');
    expect(oauthButtons).toBeInTheDocument();
    expect(oauthButtons).toHaveAttribute('data-variant', 'login');
  });

  it('should validate email field on blur', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    
    await user.type(emailInput, 'invalid-email');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('auth.validation.emailInvalid')).toBeInTheDocument();
    });
  });

  it('should validate password field on blur', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    const passwordInput = screen.getByLabelText(/auth.login.passwordLabel/);
    
    await user.type(passwordInput, '123');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('auth.validation.passwordMinLength')).toBeInTheDocument();
    });
  });

  it('should clear field errors when user starts typing', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    
    // First trigger an error
    await user.type(emailInput, 'invalid');
    await user.tab();
    
    await waitFor(() => {
      expect(screen.getByText('auth.validation.emailInvalid')).toBeInTheDocument();
    });

    // Then start typing to clear the error
    await user.type(emailInput, '@example.com');
    
    await waitFor(() => {
      expect(screen.queryByText('auth.validation.emailInvalid')).not.toBeInTheDocument();
    });
  });

  it('should submit form with valid credentials', async () => {
    const user = userEvent.setup();
    mockStore.loginWithCredentials.mockResolvedValue(undefined);
    
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.login.passwordLabel/);
    const submitButton = screen.getByRole('button', { name: /auth.login.loginButton/ });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.loginWithCredentials).toHaveBeenCalledWith(
        'test@example.com',
        'password123',
        false
      );
    });

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('should submit form with remember me option', async () => {
    const user = userEvent.setup();
    mockStore.loginWithCredentials.mockResolvedValue(undefined);
    
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.login.passwordLabel/);
    const rememberMeCheckbox = screen.getByLabelText(/auth.login.rememberMe/);
    const submitButton = screen.getByRole('button', { name: /auth.login.loginButton/ });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(rememberMeCheckbox);
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.loginWithCredentials).toHaveBeenCalledWith(
        'test@example.com',
        'password123',
        true
      );
    });
  });

  it('should not submit form with validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    const submitButton = screen.getByRole('button', { name: /auth.login.loginButton/ });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('auth.validation.emailRequired')).toBeInTheDocument();
      expect(screen.getByText('auth.validation.passwordRequired')).toBeInTheDocument();
    });

    expect(mockStore.loginWithCredentials).not.toHaveBeenCalled();
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should display loading state during login', () => {
    mockStore.isLoading = true;
    render(<LoginPage />);

    const submitButton = screen.getByRole('button', { name: /Signing in.../ });
    expect(submitButton).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument(); // Loading spinner
  });

  it('should display error message from store', () => {
    mockStore.error = 'Invalid credentials';
    render(<LoginPage />);

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
  });

  it('should disable form fields during loading', () => {
    mockStore.isLoading = true;
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.login.passwordLabel/);
    const rememberMeCheckbox = screen.getByLabelText(/auth.login.rememberMe/);
    const submitButton = screen.getByRole('button');

    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(rememberMeCheckbox).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  it('should handle login error gracefully', async () => {
    const user = userEvent.setup();
    mockStore.loginWithCredentials.mockRejectedValue(new Error('Login failed'));
    
    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/auth.login.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.login.passwordLabel/);
    const submitButton = screen.getByRole('button', { name: /auth.login.loginButton/ });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.loginWithCredentials).toHaveBeenCalled();
    });

    // Should not navigate on error
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should have link to registration page', () => {
    render(<LoginPage />);

    const registerLink = screen.getByText('auth.register.signIn').closest('a');
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('should have link to forgot password page', () => {
    render(<LoginPage />);

    const forgotPasswordLink = screen.getByText('auth.login.forgotPassword').closest('a');
    expect(forgotPasswordLink).toHaveAttribute('href', '/forgot-password');
  });
});