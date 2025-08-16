export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: string) => boolean
}

export interface ValidationResult {
  isValid: boolean
  error?: string
}

export class FormValidator {
  static validateEmail(email: string): ValidationResult {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    
    if (!email.trim()) {
      return { isValid: false, error: 'auth.validation.emailRequired' }
    }
    
    if (!emailRegex.test(email)) {
      return { isValid: false, error: 'auth.validation.emailInvalid' }
    }
    
    return { isValid: true }
  }

  static validatePassword(password: string): ValidationResult {
    if (!password) {
      return { isValid: false, error: 'auth.validation.passwordRequired' }
    }
    
    if (password.length < 8) {
      return { isValid: false, error: 'auth.validation.passwordMinLength' }
    }
    
    return { isValid: true }
  }

  static validateConfirmPassword(password: string, confirmPassword: string): ValidationResult {
    if (!confirmPassword) {
      return { isValid: false, error: 'auth.validation.passwordRequired' }
    }
    
    if (password !== confirmPassword) {
      return { isValid: false, error: 'auth.validation.passwordsNotMatch' }
    }
    
    return { isValid: true }
  }

  static validateFullName(full_name: string): ValidationResult {
    // Full name is optional, so return valid if empty
    if (!full_name || !full_name.trim()) {
      return { isValid: true }
    }
    
    if (full_name.trim().length < 2) {
      return { isValid: false, error: 'auth.validation.nameMinLength' }
    }
    
    return { isValid: true }
  }

  static validateUsername(username: string): ValidationResult {
    if (!username || !username.trim()) {
      return { isValid: false, error: 'auth.validation.usernameRequired' }
    }
    
    if (username.length < 3 || username.length > 50) {
      return { isValid: false, error: 'auth.validation.usernameLength' }
    }
    
    const usernameRegex = /^[a-zA-Z0-9._-]+$/
    if (!usernameRegex.test(username)) {
      return { isValid: false, error: 'auth.validation.usernameInvalid' }
    }
    
    return { isValid: true }
  }

  static validateInviteCode(code: string): ValidationResult {
    if (!code || !code.trim()) {
      return { isValid: true } // Invite code is optional
    }
    
    // More flexible invite code format - allow various alphanumeric patterns
    if (code.length < 4 || code.length > 20) {
      return { isValid: false, error: 'auth.validation.inviteCodeLength' }
    }
    
    const inviteCodeRegex = /^[A-Z0-9]+$/
    if (!inviteCodeRegex.test(code)) {
      return { isValid: false, error: 'auth.validation.inviteCodeInvalid' }
    }
    
    return { isValid: true }
  }

  static validateField(value: string, rules: ValidationRule): ValidationResult {
    if (rules.required && !value.trim()) {
      return { isValid: false, error: 'Field is required' }
    }
    
    if (rules.minLength && value.length < rules.minLength) {
      return { isValid: false, error: `Minimum length is ${rules.minLength}` }
    }
    
    if (rules.maxLength && value.length > rules.maxLength) {
      return { isValid: false, error: `Maximum length is ${rules.maxLength}` }
    }
    
    if (rules.pattern && !rules.pattern.test(value)) {
      return { isValid: false, error: 'Invalid format' }
    }
    
    if (rules.custom && !rules.custom(value)) {
      return { isValid: false, error: 'Validation failed' }
    }
    
    return { isValid: true }
  }
}

export interface LoginFormData {
  email: string
  password: string
  rememberMe: boolean
}

export interface RegisterFormData {
  full_name: string
  email: string
  password: string
  confirmPassword: string
  username?: string
  invited_by_code?: string
  agreeToTerms: boolean
}

export function validateLoginForm(data: LoginFormData): Record<string, ValidationResult> {
  return {
    email: FormValidator.validateEmail(data.email),
    password: FormValidator.validatePassword(data.password),
  }
}

export function validateRegisterForm(data: RegisterFormData): Record<string, ValidationResult> {
  return {
    full_name: FormValidator.validateFullName(data.full_name),
    email: FormValidator.validateEmail(data.email),
    password: FormValidator.validatePassword(data.password),
    confirmPassword: FormValidator.validateConfirmPassword(data.password, data.confirmPassword),
    username: FormValidator.validateUsername(data.username || ''),
    invited_by_code: FormValidator.validateInviteCode(data.invited_by_code || ''),
  }
}