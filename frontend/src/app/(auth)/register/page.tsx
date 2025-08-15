'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { useTranslations } from '@/lib/i18n/client'
import useStore from '@/store'
import {
  RegisterFormData,
  validateRegisterForm,
  ValidationResult,
} from '@/lib/utils/validation'
import { getRegistrationTracking } from '@/lib/utils/url'
import { cn } from '@/lib/utils/cn'
import { LanguageToggle } from '@/components/ui/LanguageToggle'

export default function RegisterPage() {
  const t = useTranslations()
  const router = useRouter()
  const { registerWithCredentials, isLoading, error } = useStore()

  const [formData, setFormData] = useState<RegisterFormData>({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    username: '',
    invited_by_code: '',
    agreeToTerms: false,
  })

  const [fieldErrors, setFieldErrors] = useState<
    Record<string, ValidationResult>
  >({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  // Auto-fill invite code from URL on component mount
  useEffect(() => {
    const trackingInfo = getRegistrationTracking()
    if (trackingInfo.invited_by_code) {
      setFormData((prev) => ({
        ...prev,
        invited_by_code: trackingInfo.invited_by_code || '',
      }))
    }
  }, [])

  const handleInputChange = (
    field: keyof RegisterFormData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))

    // Clear field error when user starts typing
    if (fieldErrors[field] && !fieldErrors[field].isValid) {
      setFieldErrors((prev) => ({ ...prev, [field]: { isValid: true } }))
    }
  }

  const handleBlur = (field: keyof RegisterFormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }))

    // Validate single field on blur
    const validation = validateRegisterForm(formData)
    if (validation[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: validation[field] }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Mark all fields as touched (full_name is optional)
    setTouched({
      email: true,
      password: true,
      confirmPassword: true,
      username: true,
      invited_by_code: true,
    })

    // Validate form
    const validation = validateRegisterForm(formData)
    setFieldErrors(validation)

    // Check terms agreement
    if (!formData.agreeToTerms) {
      setFieldErrors((prev) => ({
        ...prev,
        agreeToTerms: {
          isValid: false,
          error: 'auth.validation.termsRequired',
        },
      }))
      return
    }

    // Check if form is valid
    const isFormValid =
      Object.values(validation).every((result) => result.isValid) &&
      formData.agreeToTerms

    if (!isFormValid) {
      return
    }

    try {
      const trackingInfo = getRegistrationTracking()
      const registerData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || formData.username, // Use username as fallback for nickname
        username: formData.username,
        invited_by_code:
          formData.invited_by_code || trackingInfo.invited_by_code,
        registration_source: trackingInfo.registration_source,
        registration_channel: trackingInfo.registration_channel,
        utm_source: trackingInfo.utm_source,
        utm_medium: trackingInfo.utm_medium,
        utm_campaign: trackingInfo.utm_campaign,
      }

      await registerWithCredentials(registerData)

      // Redirect to main app
      router.push('/dashboard')
    } catch (err) {
      // Error is handled by the store
    }
  }

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden fixed inset-0">
      {/* Background Network Animation Layer */}
      <div className="fixed inset-0 z-0 opacity-20">
        {/* Floating network dots */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-purple-400 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.3, 0.8],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Top Navigation */}
      <div className="absolute top-6 right-6 z-20">
        <LanguageToggle
          className="text-slate-300 hover:text-white"
          variant="ghost"
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 h-full flex items-center justify-center p-6 overflow-y-auto">
        <motion.div
          className="w-full max-w-lg my-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Logo and Branding */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="flex justify-center mb-6">
              <img
                src="/static/logo-light-vertical.png"
                alt="Connet.AI"
                className="w-48"
              />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Join Connet.AI
            </h1>
            <p className="text-slate-300 text-lg">
              Create your AI collaboration account
            </p>
          </motion.div>

          {/* Register Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="bg-slate-800/80 backdrop-blur-md border-slate-700/50 shadow-2xl">
              <CardContent className="p-8">
                <form onSubmit={handleSubmit} className="space-y-5">
                  {error && (
                    <motion.div
                      className="p-4 text-sm text-red-300 bg-red-900/30 rounded-xl border border-red-700/30"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                    >
                      {error}
                    </motion.div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label
                        htmlFor="username"
                        className="text-sm font-medium text-slate-200 flex items-center gap-1"
                      >
                        {t('auth.register.usernameLabel')}
                        <span className="text-red-400">*</span>
                      </Label>
                      <Input
                        id="username"
                        type="text"
                        placeholder={t('auth.register.usernamePlaceholder')}
                        value={formData.username}
                        onChange={(e) =>
                          handleInputChange('username', e.target.value)
                        }
                        onBlur={() => handleBlur('username')}
                        className={cn(
                          'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                          'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                          'hover:border-slate-500/70 transition-all duration-200',
                          touched.username &&
                            fieldErrors.username &&
                            !fieldErrors.username.isValid &&
                            'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                        )}
                        disabled={isLoading}
                        required
                      />
                      {touched.username &&
                        fieldErrors.username &&
                        !fieldErrors.username.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.username.error!)}
                          </p>
                        )}
                    </div>

                    <div className="space-y-2">
                      <Label
                        htmlFor="full_name"
                        className="text-sm font-medium text-slate-200"
                      >
                        {t('auth.register.nicknameLabel', 'Nickname')} <span className="text-slate-400 text-xs">(Optional)</span>
                      </Label>
                      <Input
                        id="full_name"
                        type="text"
                        placeholder={t('auth.register.nicknamePlaceholder', 'Enter your nickname (optional)')}
                        value={formData.full_name}
                        onChange={(e) =>
                          handleInputChange('full_name', e.target.value)
                        }
                        onBlur={() => handleBlur('full_name')}
                        className={cn(
                          'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                          'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                          'hover:border-slate-500/70 transition-all duration-200',
                          touched.full_name &&
                            fieldErrors.full_name &&
                            !fieldErrors.full_name.isValid &&
                            'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                        )}
                        disabled={isLoading}
                      />
                      {touched.full_name &&
                        fieldErrors.full_name &&
                        !fieldErrors.full_name.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.full_name.error!)}
                          </p>
                        )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="email"
                      className="text-sm font-medium text-slate-200 flex items-center gap-1"
                    >
                      {t('auth.register.emailLabel')}
                      <span className="text-red-400">*</span>
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder={t('auth.register.emailPlaceholder')}
                      value={formData.email}
                      onChange={(e) =>
                        handleInputChange('email', e.target.value)
                      }
                      onBlur={() => handleBlur('email')}
                      className={cn(
                        'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                        'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                        'hover:border-slate-500/70 transition-all duration-200',
                        touched.email &&
                          fieldErrors.email &&
                          !fieldErrors.email.isValid &&
                          'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                      )}
                      disabled={isLoading}
                    />
                    {touched.email &&
                      fieldErrors.email &&
                      !fieldErrors.email.isValid && (
                        <p className="text-sm text-red-400">
                          {t(fieldErrors.email.error!)}
                        </p>
                      )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label
                        htmlFor="password"
                        className="text-sm font-medium text-slate-200 flex items-center gap-1"
                      >
                        {t('auth.register.passwordLabel')}
                        <span className="text-red-400">*</span>
                      </Label>
                      <Input
                        id="password"
                        type="password"
                        placeholder={t('auth.register.passwordPlaceholder')}
                        value={formData.password}
                        onChange={(e) =>
                          handleInputChange('password', e.target.value)
                        }
                        onBlur={() => handleBlur('password')}
                        className={cn(
                          'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                          'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                          'hover:border-slate-500/70 transition-all duration-200',
                          touched.password &&
                            fieldErrors.password &&
                            !fieldErrors.password.isValid &&
                            'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                        )}
                        disabled={isLoading}
                      />
                      {touched.password &&
                        fieldErrors.password &&
                        !fieldErrors.password.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.password.error!)}
                          </p>
                        )}
                    </div>

                    <div className="space-y-2">
                      <Label
                        htmlFor="confirmPassword"
                        className="text-sm font-medium text-slate-200 flex items-center gap-1"
                      >
                        {t('auth.register.confirmPasswordLabel')}
                        <span className="text-red-400">*</span>
                      </Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        placeholder={t(
                          'auth.register.confirmPasswordPlaceholder'
                        )}
                        value={formData.confirmPassword}
                        onChange={(e) =>
                          handleInputChange('confirmPassword', e.target.value)
                        }
                        onBlur={() => handleBlur('confirmPassword')}
                        className={cn(
                          'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                          'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                          'hover:border-slate-500/70 transition-all duration-200',
                          touched.confirmPassword &&
                            fieldErrors.confirmPassword &&
                            !fieldErrors.confirmPassword.isValid &&
                            'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                        )}
                        disabled={isLoading}
                      />
                      {touched.confirmPassword &&
                        fieldErrors.confirmPassword &&
                        !fieldErrors.confirmPassword.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.confirmPassword.error!)}
                          </p>
                        )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="invited_by_code"
                      className="text-sm font-medium text-slate-200"
                    >
                      {t('auth.register.inviteCodeLabel')}
                    </Label>
                    <Input
                      id="invited_by_code"
                      type="text"
                      placeholder={t('auth.register.inviteCodePlaceholder')}
                      value={formData.invited_by_code}
                      onChange={(e) =>
                        handleInputChange(
                          'invited_by_code',
                          e.target.value.toUpperCase()
                        )
                      }
                      onBlur={() => handleBlur('invited_by_code')}
                      className={cn(
                        'h-11 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                        'focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/20',
                        'hover:border-slate-500/70 transition-all duration-200',
                        touched.invited_by_code &&
                          fieldErrors.invited_by_code &&
                          !fieldErrors.invited_by_code.isValid &&
                          'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20'
                      )}
                      disabled={isLoading}
                      maxLength={6}
                    />
                    {touched.invited_by_code &&
                      fieldErrors.invited_by_code &&
                      !fieldErrors.invited_by_code.isValid && (
                        <p className="text-sm text-red-400">
                          {t(fieldErrors.invited_by_code.error!)}
                        </p>
                      )}
                  </div>

                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="agreeToTerms"
                      checked={formData.agreeToTerms}
                      onCheckedChange={(checked) =>
                        handleInputChange('agreeToTerms', !!checked)
                      }
                      disabled={isLoading}
                      className="mt-1 border-slate-600 data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600"
                    />
                    <div className="space-y-1">
                      <Label
                        htmlFor="agreeToTerms"
                        className="text-sm text-slate-300 font-medium cursor-pointer leading-relaxed"
                      >
                        {t('auth.register.agreeTerms')}
                      </Label>
                      {fieldErrors.agreeToTerms &&
                        !fieldErrors.agreeToTerms.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.agreeToTerms.error!)}
                          </p>
                        )}
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Creating account...</span>
                      </div>
                    ) : (
                      t('auth.register.registerButton')
                    )}
                  </Button>

                  <div className="text-center text-sm">
                    <span className="text-slate-400">
                      {t('auth.register.hasAccount')}{' '}
                    </span>
                    <Link
                      href="/login"
                      className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
                    >
                      {t('auth.register.signIn')}
                    </Link>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Footer */}
          <motion.div
            className="text-center mt-8 text-slate-400 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            © 2024 Connet.AI. Connecting the future, one interaction at a time.
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
