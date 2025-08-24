'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { useTranslations } from '@/lib/i18n/client'
import { FormValidator } from '@/lib/utils/validation'
import { useAuth } from '@/store'
import { useAuthPassword } from '@/hooks/business/auth'
import { cn } from '@/lib/utils/cn'
import { LanguageToggle } from '@/components/ui/LanguageToggle'
import { CheckCircle, ArrowLeft } from 'lucide-react'

export default function ForgotPasswordPage() {
  const t = useTranslations()
  const { ui, error } = useAuth()
  const { requestPasswordReset } = useAuthPassword()
  const isLoading = ui.isLoading
  
  const [email, setEmail] = useState('')
  const [success, setSuccess] = useState(false)
  const [emailError, setEmailError] = useState<string | null>(null)
  const [touched, setTouched] = useState(false)

  // Fixed positions for background dots to avoid hydration mismatch
  const backgroundDots = useMemo(() => [
    { left: 15, top: 20, duration: 4.2, delay: 0.8 },
    { left: 78, top: 15, duration: 3.7, delay: 1.3 },
    { left: 23, top: 65, duration: 4.8, delay: 0.2 },
    { left: 67, top: 45, duration: 3.4, delay: 1.9 },
    { left: 89, top: 75, duration: 4.5, delay: 0.6 },
    { left: 34, top: 35, duration: 3.9, delay: 1.5 },
    { left: 56, top: 82, duration: 4.1, delay: 0.4 },
    { left: 18, top: 48, duration: 3.6, delay: 1.7 },
    { left: 82, top: 22, duration: 4.3, delay: 0.1 },
    { left: 45, top: 78, duration: 3.8, delay: 1.2 },
  ], [])

  const handleEmailChange = (value: string) => {
    setEmail(value)
    if (emailError) {
      setEmailError(null)
    }
  }

  const handleBlur = () => {
    setTouched(true)
    const validation = FormValidator.validateEmail(email)
    if (!validation.isValid) {
      setEmailError(validation.error || null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    setTouched(true)
    const validation = FormValidator.validateEmail(email)
    
    if (!validation.isValid) {
      setEmailError(validation.error || null)
      return
    }

    try {
      const result = await requestPasswordReset({ email })
      setSuccess(true)
    } catch (err) {
      // Error is handled by the business hook and displayed via error state
    }
  }

  if (success) {
    return (
      <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden fixed inset-0">
        {/* Background Network Animation Layer */}
        <div className="fixed inset-0 z-0 opacity-20">
          {backgroundDots.map((dot, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-green-400 rounded-full"
              style={{
                left: `${dot.left}%`,
                top: `${dot.top}%`,
              }}
              animate={{
                opacity: [0.2, 0.8, 0.2],
                scale: [0.8, 1.3, 0.8],
              }}
              transition={{
                duration: dot.duration,
                repeat: Infinity,
                delay: dot.delay,
              }}
            />
          ))}
        </div>

        {/* Top Navigation */}
        <div className="absolute top-6 right-6 z-20">
          <LanguageToggle className="text-slate-300 hover:text-white" variant="ghost" />
        </div>

        {/* Main Content */}
        <div className="relative z-10 h-full flex items-center justify-center p-6">
          <motion.div 
            className="w-full max-w-md text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Success Icon */}
            <motion.div 
              className="flex justify-center mb-8"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <div className="w-20 h-20 bg-green-600 rounded-full flex items-center justify-center">
                <CheckCircle className="w-12 h-12 text-white" />
              </div>
            </motion.div>

            {/* Logo and Branding */}
            <motion.div 
              className="mb-8"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="flex justify-center mb-6">
                <img
                  src="/static/logo-light.png"
                  alt="Connet.AI"
                  className="w-16 h-16"
                />
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">
                {t('auth.forgotPassword.successTitle')}
              </h1>
              <p className="text-slate-300 text-lg">
                {t('auth.forgotPassword.successSubtitle')}
              </p>
            </motion.div>

            {/* Success Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <Card className="bg-slate-800/80 backdrop-blur-md border-slate-700/50 shadow-2xl">
                <CardContent className="p-8 space-y-6">
                  <div className="p-4 text-sm text-green-300 bg-green-900/30 rounded-xl border border-green-700/30">
                    {t('auth.forgotPassword.successMessage').replace('{email}', email)}
                  </div>
                  
                  <div className="text-sm text-slate-300 text-left">
                    <p className="font-medium mb-3">{t('auth.forgotPassword.didntReceive')}</p>
                    <ul className="space-y-2 list-disc list-inside text-slate-400">
                      <li>{t('auth.forgotPassword.checkSpam')}</li>
                      <li>{t('auth.forgotPassword.correctEmail')}</li>
                      <li>{t('auth.forgotPassword.waitMinutes')}</li>
                    </ul>
                  </div>

                  <div className="space-y-4">
                    <Button 
                      variant="outline"
                      className="w-full h-12 rounded-xl bg-slate-700/50 border-slate-600 text-slate-200 hover:bg-slate-600/50 hover:text-white"
                      onClick={() => {
                        setSuccess(false)
                        setEmail('')
                        setTouched(false)
                      }}
                    >
                      {t('auth.forgotPassword.sendAnother')}
                    </Button>
                    
                    <Link href="/login">
                      <Button 
                        variant="ghost"
                        className="w-full h-12 rounded-xl text-blue-400 hover:text-blue-300 hover:bg-blue-900/20"
                      >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        {t('auth.forgotPassword.backToLogin')}
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Footer */}
            <motion.div 
              className="text-center mt-8 text-slate-400 text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              © 2024 Connet.AI. Connecting the future, one interaction at a time.
            </motion.div>
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden fixed inset-0">
      {/* Background Network Animation Layer */}
      <div className="fixed inset-0 z-0 opacity-20">
        {backgroundDots.map((dot, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full"
            style={{
              left: `${dot.left}%`,
              top: `${dot.top}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.3, 0.8],
            }}
            transition={{
              duration: dot.duration,
              repeat: Infinity,
              delay: dot.delay,
            }}
          />
        ))}
      </div>

      {/* Top Navigation */}
      <div className="absolute top-6 right-6 z-20">
        <LanguageToggle className="text-slate-300 hover:text-white" variant="ghost" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 h-full flex items-center justify-center p-6">
        <motion.div 
          className="w-full max-w-md"
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
                src="/static/logo-light.png"
                alt="Connet.AI"
                className="w-16 h-16"
              />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">
              {t('auth.forgotPassword.title')}
            </h1>
            <p className="text-slate-300 text-lg">
              {t('auth.forgotPassword.subtitle')}
            </p>
          </motion.div>

          {/* Reset Form Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="bg-slate-800/80 backdrop-blur-md border-slate-700/50 shadow-2xl">
              <CardContent className="p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {error.current && (
                    <motion.div 
                      className="p-4 text-sm text-red-300 bg-red-900/30 rounded-xl border border-red-700/30"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                    >
                      {error.current}
                    </motion.div>
                  )}
                  
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm font-medium text-slate-200 flex items-center gap-1">
                      {t('auth.login.emailLabel')}
                      <span className="text-red-400">*</span>
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder={t('auth.login.emailPlaceholder')}
                      value={email}
                      onChange={(e) => handleEmailChange(e.target.value)}
                      onBlur={handleBlur}
                      className={cn(
                        'h-12 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400',
                        'focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/20',
                        'hover:border-slate-500/70 transition-all duration-200',
                        touched && emailError && 
                        "border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20"
                      )}
                      disabled={isLoading}
                      required
                    />
                    {touched && emailError && (
                      <p className="text-sm text-red-400">
                        {t(emailError)}
                      </p>
                    )}
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full h-12 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300" 
                    disabled={isLoading || !email}
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>{t('auth.forgotPassword.sending')}</span>
                      </div>
                    ) : (
                      t('auth.forgotPassword.sendButton')
                    )}
                  </Button>
                  
                  <div className="text-center text-sm">
                    <span className="text-slate-400">
                      {t('auth.forgotPassword.rememberPassword')}{' '}
                    </span>
                    <Link 
                      href="/login" 
                      className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      {t('auth.forgotPassword.backToLogin')}
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