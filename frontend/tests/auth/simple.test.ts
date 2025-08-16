/**
 * Simple authentication test to verify basic functionality
 */

import { FormValidator } from '@/lib/utils/validation';
import { getRegistrationTracking } from '@/lib/utils/url';

describe('Simple Authentication Tests', () => {
  it('should validate email correctly', () => {
    const validEmail = FormValidator.validateEmail('test@example.com');
    expect(validEmail.isValid).toBe(true);

    const invalidEmail = FormValidator.validateEmail('invalid-email');
    expect(invalidEmail.isValid).toBe(false);
  });

  it('should validate password correctly', () => {
    const validPassword = FormValidator.validatePassword('password123');
    expect(validPassword.isValid).toBe(true);

    const invalidPassword = FormValidator.validatePassword('123');
    expect(invalidPassword.isValid).toBe(false);
  });

  it('should validate username correctly', () => {
    const validUsername = FormValidator.validateUsername('testuser');
    expect(validUsername.isValid).toBe(true);

    const invalidUsername = FormValidator.validateUsername('ab');
    expect(invalidUsername.isValid).toBe(false);
  });

  it('should handle invitation codes correctly', () => {
    const validInviteCode = FormValidator.validateInviteCode('INVITE123');
    expect(validInviteCode.isValid).toBe(true);

    const emptyInviteCode = FormValidator.validateInviteCode('');
    expect(emptyInviteCode.isValid).toBe(true); // Optional

    const invalidInviteCode = FormValidator.validateInviteCode('abc');
    expect(invalidInviteCode.isValid).toBe(false);
  });

  it('should generate registration tracking data', () => {
    // Mock window.location for this test
    Object.defineProperty(window, 'location', {
      value: {
        search: '?invite=TEST123&utm_source=google&utm_medium=cpc',
      },
      writable: true,
    });

    const tracking = getRegistrationTracking();
    expect(tracking.invited_by_code).toBe('TEST123');
    expect(tracking.registration_source).toBe('web');
    expect(tracking.registration_channel).toBe('invite');
    expect(tracking.utm_source).toBe('google');
    expect(tracking.utm_medium).toBe('cpc');
  });

  it('should handle organic registration tracking', () => {
    // Mock window.location with no params
    Object.defineProperty(window, 'location', {
      value: {
        search: '',
      },
      writable: true,
    });

    const tracking = getRegistrationTracking();
    expect(tracking.invited_by_code).toBeUndefined();
    expect(tracking.registration_source).toBe('web');
    expect(tracking.registration_channel).toBe('organic');
    expect(tracking.utm_source).toBeUndefined();
  });
});