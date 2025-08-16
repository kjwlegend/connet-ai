/**
 * Registration component integration tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';
import RegisterPage from '@/app/(auth)/register/page';

// Mock the store
const mockStore = {
  registerWithCredentials: jest.fn(),
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

// Mock URL tracking
jest.mock('@/lib/utils/url', () => ({
  getRegistrationTracking: jest.fn(() => ({
    invited_by_code: undefined,
    registration_source: 'web',
    registration_channel: 'organic',
    utm_source: undefined,
    utm_medium: undefined,
    utm_campaign: undefined,
  })),
}));

const mockPush = jest.fn();
(useRouter as jest.Mock).mockReturnValue({
  push: mockPush,
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
});

describe('Registration Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockStore.registerWithCredentials.mockReset();
    mockStore.isLoading = false;
    mockStore.error = null;
  });

  it('should render registration form with all required fields', () => {
    render(<RegisterPage />);

    expect(screen.getByLabelText(/auth.register.usernameLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.nicknameLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.emailLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.passwordLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.confirmPasswordLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.inviteCodeLabel/)).toBeInTheDocument();
    expect(screen.getByLabelText(/auth.register.agreeTerms/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /auth.register.registerButton/ })).toBeInTheDocument();
  });

  it('should display OAuth buttons', () => {
    render(<RegisterPage />);

    const oauthButtons = screen.getByTestId('oauth-buttons');
    expect(oauthButtons).toBeInTheDocument();
    expect(oauthButtons).toHaveAttribute('data-variant', 'register');
  });

  it('should validate username field (required)', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const submitButton = screen.getByRole('button', { name: /auth.register.registerButton/ });

    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('auth.validation.usernameRequired')).toBeInTheDocument();
    });
  });

  it('should validate email field', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    
    await user.type(emailInput, 'invalid-email');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('auth.validation.emailInvalid')).toBeInTheDocument();
    });
  });

  it('should validate password confirmation', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    
    await user.type(passwordInput, 'password123');
    await user.type(confirmPasswordInput, 'different123');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText('auth.validation.passwordsNotMatch')).toBeInTheDocument();
    });
  });

  it('should validate terms agreement', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    const submitButton = screen.getByRole('button', { name: /auth.register.registerButton/ });

    // Fill in all required fields but don't check terms
    await user.type(usernameInput, 'testuser');
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.type(confirmPasswordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('auth.validation.termsRequired')).toBeInTheDocument();
    });
  });

  it('should submit form with valid data', async () => {
    const user = userEvent.setup();
    mockStore.registerWithCredentials.mockResolvedValue(undefined);
    
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const nicknameInput = screen.getByLabelText(/auth.register.nicknameLabel/);
    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    const inviteCodeInput = screen.getByLabelText(/auth.register.inviteCodeLabel/);
    const termsCheckbox = screen.getByLabelText(/auth.register.agreeTerms/);
    const submitButton = screen.getByRole('button', { name: /auth.register.registerButton/ });

    await user.type(usernameInput, 'testuser');
    await user.type(nicknameInput, 'Test User');
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.type(confirmPasswordInput, 'password123');
    await user.type(inviteCodeInput, 'INVITE123');
    await user.click(termsCheckbox);
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.registerWithCredentials).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        full_name: 'Test User',
        username: 'testuser',
        invited_by_code: 'INVITE123',
        registration_source: 'web',
        registration_channel: 'organic',
        utm_source: undefined,
        utm_medium: undefined,
        utm_campaign: undefined,
      });
    });

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('should submit form with minimal required data', async () => {
    const user = userEvent.setup();
    mockStore.registerWithCredentials.mockResolvedValue(undefined);
    
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    const termsCheckbox = screen.getByLabelText(/auth.register.agreeTerms/);
    const submitButton = screen.getByRole('button', { name: /auth.register.registerButton/ });

    await user.type(usernameInput, 'testuser');
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.type(confirmPasswordInput, 'password123');
    await user.click(termsCheckbox);
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.registerWithCredentials).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        full_name: 'testuser', // Uses username as fallback for full_name
        username: 'testuser',
        invited_by_code: undefined,
        registration_source: 'web',
        registration_channel: 'organic',
        utm_source: undefined,
        utm_medium: undefined,
        utm_campaign: undefined,
      });
    });
  });

  it('should uppercase invitation codes', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const inviteCodeInput = screen.getByLabelText(/auth.register.inviteCodeLabel/) as HTMLInputElement;
    
    await user.type(inviteCodeInput, 'invite123');

    expect(inviteCodeInput.value).toBe('INVITE123');
  });

  it('should auto-fill invitation code from URL tracking', () => {
    // Mock URL tracking to return an invite code
    const mockGetRegistrationTracking = require('@/lib/utils/url').getRegistrationTracking;
    mockGetRegistrationTracking.mockReturnValue({
      invited_by_code: 'URL123',
      registration_source: 'web',
      registration_channel: 'invite',
      utm_source: 'email',
      utm_medium: 'newsletter',
      utm_campaign: 'launch',
    });

    render(<RegisterPage />);

    const inviteCodeInput = screen.getByLabelText(/auth.register.inviteCodeLabel/) as HTMLInputElement;
    expect(inviteCodeInput.value).toBe('URL123');
  });

  it('should display loading state during registration', () => {
    mockStore.isLoading = true;
    render(<RegisterPage />);

    const submitButton = screen.getByRole('button', { name: /Creating account.../ });
    expect(submitButton).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument(); // Loading spinner
  });

  it('should display error message from store', () => {
    mockStore.error = 'Email already exists';
    render(<RegisterPage />);

    expect(screen.getByText('Email already exists')).toBeInTheDocument();
  });

  it('should disable form fields during loading', () => {
    mockStore.isLoading = true;
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    const inviteCodeInput = screen.getByLabelText(/auth.register.inviteCodeLabel/);
    const termsCheckbox = screen.getByLabelText(/auth.register.agreeTerms/);
    const submitButton = screen.getByRole('button');

    expect(usernameInput).toBeDisabled();
    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(confirmPasswordInput).toBeDisabled();
    expect(inviteCodeInput).toBeDisabled();
    expect(termsCheckbox).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  it('should handle registration error gracefully', async () => {
    const user = userEvent.setup();
    mockStore.registerWithCredentials.mockRejectedValue(new Error('Registration failed'));
    
    render(<RegisterPage />);

    const usernameInput = screen.getByLabelText(/auth.register.usernameLabel/);
    const emailInput = screen.getByLabelText(/auth.register.emailLabel/);
    const passwordInput = screen.getByLabelText(/auth.register.passwordLabel/);
    const confirmPasswordInput = screen.getByLabelText(/auth.register.confirmPasswordLabel/);
    const termsCheckbox = screen.getByLabelText(/auth.register.agreeTerms/);
    const submitButton = screen.getByRole('button', { name: /auth.register.registerButton/ });

    await user.type(usernameInput, 'testuser');
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.type(confirmPasswordInput, 'password123');
    await user.click(termsCheckbox);
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockStore.registerWithCredentials).toHaveBeenCalled();
    });

    // Should not navigate on error
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should have link to login page', () => {
    render(<RegisterPage />);

    const loginLink = screen.getByText('auth.register.signIn').closest('a');
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('should limit invitation code to 6 characters', async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const inviteCodeInput = screen.getByLabelText(/auth.register.inviteCodeLabel/) as HTMLInputElement;
    
    await user.type(inviteCodeInput, 'VERYLONGCODE');

    expect(inviteCodeInput.value).toBe('VERYLO'); // Should be truncated to 6 chars
  });
});