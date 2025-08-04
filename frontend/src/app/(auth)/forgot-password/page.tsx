'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { useTranslations } from '@/lib/i18n/client'
import { FormValidator } from '@/lib/utils/validation'
import { AuthAPI } from '@/lib/api/auth'
import { APIError } from '@/lib/api/client'
import { cn } from '@/lib/utils/cn'
import { AuthLayout } from '@/components/auth/AuthLayout'

export default function ForgotPasswordPage() {
  const t = useTranslations()
  
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [emailError, setEmailError] = useState<string | null>(null)
  const [touched, setTouched] = useState(false)

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
      setIsLoading(true)
      setError(null)
      
      await AuthAPI.requestPasswordReset({ email })
      setSuccess(true)
      
    } catch (err) {
      const errorMessage = err instanceof APIError 
        ? err.message 
        : 'Failed to send reset email. Please try again.'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <AuthLayout 
        title="Email Sent"
        subtitle="Check your email for reset instructions"
        showBranding={false}
      >
        <Card className="w-full border-0 shadow-2xl bg-card/50 backdrop-blur-md">
          
          <CardContent className="space-y-4">
            <div className="p-3 text-sm text-green-600 bg-green-50 dark:bg-green-950 rounded-md">
              We've sent a password reset link to <strong>{email}</strong>. 
              Please check your email and click the link to reset your password.
            </div>
            
            <div className="text-sm text-muted-foreground">
              <p>Didn't receive the email?</p>
              <ul className="mt-2 space-y-1 list-disc list-inside">
                <li>Check your spam folder</li>
                <li>Make sure you entered the correct email address</li>
                <li>Wait a few minutes and try again</li>
              </ul>
            </div>
          </CardContent>
          
          <CardFooter className="flex flex-col space-y-4">
            <Button 
              variant="outline"
              className="w-full"
              onClick={() => {
                setSuccess(false)
                setEmail('')
                setTouched(false)
              }}
            >
              Send Another Email
            </Button>
            
            <div className="text-center text-sm">
              <Link 
                href="/login" 
                className="text-primary hover:underline font-medium"
              >
                Back to Login
              </Link>
            </div>
          </CardFooter>
        </Card>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout 
      title="Reset Password"
      subtitle="Enter your email address and we'll send you a link to reset your password"
      showBranding={false}
    >
      <Card className="w-full border-0 shadow-2xl bg-card/50 backdrop-blur-md">
        
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                onBlur={handleBlur}
                className={cn(
                  touched && emailError && 
                  "border-destructive focus-visible:ring-destructive"
                )}
                disabled={isLoading}
                required
              />
              {touched && emailError && (
                <p className="text-sm text-destructive">
                  {t(emailError)}
                </p>
              )}
            </div>
          </CardContent>
          
          <CardFooter className="flex flex-col space-y-4">
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading || !email}
            >
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </Button>
            
            <div className="text-center text-sm">
              <span className="text-muted-foreground">
                Remember your password?{' '}
              </span>
              <Link 
                href="/login" 
                className="text-primary hover:underline font-medium"
              >
                Back to Login
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </AuthLayout>
  )
}