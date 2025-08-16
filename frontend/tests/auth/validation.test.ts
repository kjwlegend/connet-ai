/**
 * Authentication form validation tests
 */

import { FormValidator, validateLoginForm, validateRegisterForm } from '@/lib/utils/validation';

describe('Authentication Validation', () => {
  describe('Email Validation', () => {
    it('should validate correct email addresses', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org',
        'firstname.lastname@company.io'
      ];

      validEmails.forEach(email => {
        const result = FormValidator.validateEmail(email);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should reject invalid email addresses', () => {
      const invalidEmails = [
        '',
        'invalid-email',
        '@example.com',
        'user@',
        'user@domain.',
        'user name@example.com'
      ];

      invalidEmails.forEach(email => {
        const result = FormValidator.validateEmail(email);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });
  });

  describe('Password Validation', () => {
    it('should validate passwords with minimum length', () => {
      const validPasswords = [
        'password123',
        'securePassword!',
        'My$ecureP@ssw0rd',
        '12345678'
      ];

      validPasswords.forEach(password => {
        const result = FormValidator.validatePassword(password);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should reject short passwords', () => {
      const shortPasswords = [
        '123',
        'short',
        '1234567'
      ];

      shortPasswords.forEach(password => {
        const result = FormValidator.validatePassword(password);
        expect(result.isValid).toBe(false);
        expect(result.error).toBe('auth.validation.passwordMinLength');
      });
      
      // Test empty password separately
      const emptyResult = FormValidator.validatePassword('');
      expect(emptyResult.isValid).toBe(false);
      expect(emptyResult.error).toBe('auth.validation.passwordRequired');
    });
  });

  describe('Username Validation', () => {
    it('should validate correct usernames', () => {
      const validUsernames = [
        'testuser',
        'user123',
        'user_name',
        'user.name',
        'user-name',
        'test123_user.name'
      ];

      validUsernames.forEach(username => {
        const result = FormValidator.validateUsername(username);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should reject invalid usernames', () => {
      const invalidUsernames = [
        '',
        'ab', // too short
        'a'.repeat(51), // too long
        'user name', // spaces
        'user@name', // invalid characters
        'user#name', // invalid characters
      ];

      invalidUsernames.forEach(username => {
        const result = FormValidator.validateUsername(username);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });
  });

  describe('Invite Code Validation', () => {
    it('should validate correct invite codes', () => {
      const validCodes = [
        'ABCD1234',
        'TEST123',
        'INVITE2024',
        'ABC123'
      ];

      validCodes.forEach(code => {
        const result = FormValidator.validateInviteCode(code);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should accept empty invite codes (optional)', () => {
      const result = FormValidator.validateInviteCode('');
      expect(result.isValid).toBe(true);
    });

    it('should reject invalid invite codes', () => {
      const invalidCodes = [
        'abc', // too short
        'a'.repeat(21), // too long
        'code with spaces',
        'code-with-dash',
        'code.with.dots'
      ];

      invalidCodes.forEach(code => {
        const result = FormValidator.validateInviteCode(code);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });
  });

  describe('Full Name Validation', () => {
    it('should validate correct full names', () => {
      const validNames = [
        'John Doe',
        'Jane Smith-Johnson',
        'María García',
        '李小明'
      ];

      validNames.forEach(name => {
        const result = FormValidator.validateFullName(name);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('should accept empty full names (optional)', () => {
      const result = FormValidator.validateFullName('');
      expect(result.isValid).toBe(true);
    });

    it('should reject names that are too short', () => {
      const result = FormValidator.validateFullName('a');
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('auth.validation.nameMinLength');
    });
  });

  describe('Login Form Validation', () => {
    it('should validate complete login form', () => {
      const formData = {
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false
      };

      const validation = validateLoginForm(formData);
      expect(validation.email.isValid).toBe(true);
      expect(validation.password.isValid).toBe(true);
    });

    it('should reject login form with invalid data', () => {
      const formData = {
        email: 'invalid-email',
        password: '123',
        rememberMe: false
      };

      const validation = validateLoginForm(formData);
      expect(validation.email.isValid).toBe(false);
      expect(validation.password.isValid).toBe(false);
    });
  });

  describe('Register Form Validation', () => {
    it('should validate complete registration form', () => {
      const formData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'password123',
        username: 'testuser',
        invited_by_code: 'INVITE123',
        agreeToTerms: true
      };

      const validation = validateRegisterForm(formData);
      expect(validation.full_name.isValid).toBe(true);
      expect(validation.email.isValid).toBe(true);
      expect(validation.password.isValid).toBe(true);
      expect(validation.confirmPassword.isValid).toBe(true);
      expect(validation.username.isValid).toBe(true);
      expect(validation.invited_by_code.isValid).toBe(true);
    });

    it('should reject registration with mismatched passwords', () => {
      const formData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'different123',
        username: 'testuser',
        invited_by_code: '',
        agreeToTerms: true
      };

      const validation = validateRegisterForm(formData);
      expect(validation.confirmPassword.isValid).toBe(false);
      expect(validation.confirmPassword.error).toBe('auth.validation.passwordsNotMatch');
    });

    it('should validate registration with minimal required fields', () => {
      const formData = {
        full_name: '',
        email: 'test@example.com',
        password: 'password123',
        confirmPassword: 'password123',
        username: 'testuser',
        invited_by_code: '',
        agreeToTerms: true
      };

      const validation = validateRegisterForm(formData);
      expect(validation.full_name.isValid).toBe(true); // optional
      expect(validation.email.isValid).toBe(true);
      expect(validation.password.isValid).toBe(true);
      expect(validation.confirmPassword.isValid).toBe(true);
      expect(validation.username.isValid).toBe(true);
      expect(validation.invited_by_code.isValid).toBe(true); // optional
    });
  });
});