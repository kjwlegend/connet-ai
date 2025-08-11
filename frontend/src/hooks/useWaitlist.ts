/**
 * useWaitlist hook - Business logic for waitlist functionality
 */

import { useState, useCallback } from 'react'
import { waitlistService, WaitlistEntry, WaitlistResponse } from '@/services/api/waitlistService'
import { useToasts } from '@/store/index.new'
import { useTranslations } from '@/lib/i18n/client'

interface UseWaitlistReturn {
  // State
  isLoading: boolean
  isSubmitted: boolean
  error: string | null
  waitlistData: WaitlistResponse | null
  
  // Actions
  joinWaitlist: (email: string, source?: string) => Promise<WaitlistResponse | null>
  checkEmailExists: (email: string) => Promise<boolean>
  getPosition: (email: string) => Promise<{ position: number; total: number } | null>
  generateReferralLink: (email: string) => Promise<string | null>
  clearError: () => void
  reset: () => void
  
  // Utils
  getStoredSignup: () => { email: string; position: number; joined_at: string } | null
  hasAlreadySignedUp: (email: string) => boolean
}

export const useWaitlist = (): UseWaitlistReturn => {
  const t = useTranslations()
  const toasts = useToasts()
  
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [waitlistData, setWaitlistData] = useState<WaitlistResponse | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const reset = useCallback(() => {
    setIsLoading(false)
    setIsSubmitted(false)
    setError(null)
    setWaitlistData(null)
  }, [])

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email.trim())
  }

  const joinWaitlist = useCallback(async (
    email: string, 
    source: string = 'homepage'
  ): Promise<WaitlistResponse | null> => {
    const trimmedEmail = email.trim().toLowerCase()
    
    // Validation
    if (!trimmedEmail) {
      setError(t('waitlist.errors.email_required', 'Email is required'))
      toasts.error(
        t('waitlist.errors.email_required', 'Email is required'),
        t('waitlist.errors.please_enter_email', 'Please enter your email address')
      )
      return null
    }

    if (!validateEmail(trimmedEmail)) {
      setError(t('waitlist.errors.email_invalid', 'Invalid email address'))
      toasts.error(
        t('waitlist.errors.email_invalid', 'Invalid email address'),
        t('waitlist.errors.please_enter_valid_email', 'Please enter a valid email address')
      )
      return null
    }

    // Check if already signed up with this email
    if (hasAlreadySignedUp(trimmedEmail)) {
      setError(t('waitlist.errors.already_signed_up', 'Already signed up'))
      toasts.warning(
        t('waitlist.errors.already_signed_up', 'Already signed up'),
        t('waitlist.errors.email_already_registered', 'This email is already registered for the waitlist')
      )
      return null
    }

    setIsLoading(true)
    setError(null)

    try {
      // Show loading toast
      toasts.loading(
        t('waitlist.loading.joining', 'Joining waitlist...'),
        t('waitlist.loading.please_wait', 'Please wait while we process your request')
      )

      const entry: WaitlistEntry = {
        email: trimmedEmail,
        source,
      }

      const response = await waitlistService.joinWaitlist(entry)

      if (response.success && response.data) {
        setWaitlistData(response.data)
        setIsSubmitted(true)
        
        // Success feedback
        toasts.success(
          t('waitlist.success.welcome', 'Welcome to the waitlist!'),
          t('waitlist.success.position_message', 'You are #{{position}} in line with {{total}} total subscribers', {
            position: response.data.position,
            total: response.data.total_subscribers
          })
        )

        return response.data
      } else {
        throw new Error(response.error || t('waitlist.errors.join_failed', 'Failed to join waitlist'))
      }

    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : t('waitlist.errors.unexpected', 'An unexpected error occurred')
      
      setError(errorMessage)
      
      // Error feedback
      toasts.error(
        t('waitlist.errors.join_failed', 'Failed to join waitlist'),
        errorMessage
      )

      console.error('Waitlist signup error:', error)
      return null

    } finally {
      setIsLoading(false)
    }
  }, [t, toasts])

  const checkEmailExists = useCallback(async (email: string): Promise<boolean> => {
    if (!validateEmail(email)) {
      return false
    }

    try {
      const response = await waitlistService.checkEmail(email.trim().toLowerCase())
      return response.success && response.data?.exists === true
    } catch (error) {
      console.error('Error checking email:', error)
      return false
    }
  }, [])

  const getPosition = useCallback(async (email: string) => {
    if (!validateEmail(email)) {
      setError(t('waitlist.errors.email_invalid', 'Invalid email address'))
      return null
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await waitlistService.getPosition(email.trim().toLowerCase())
      
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.error || t('waitlist.errors.position_failed', 'Failed to get position'))
      }

    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : t('waitlist.errors.unexpected', 'An unexpected error occurred')
      
      setError(errorMessage)
      toasts.error(
        t('waitlist.errors.position_failed', 'Failed to get position'),
        errorMessage
      )

      return null

    } finally {
      setIsLoading(false)
    }
  }, [t, toasts])

  const generateReferralLink = useCallback(async (email: string): Promise<string | null> => {
    if (!validateEmail(email)) {
      setError(t('waitlist.errors.email_invalid', 'Invalid email address'))
      return null
    }

    try {
      const response = await waitlistService.generateReferralLink(email.trim().toLowerCase())
      
      if (response.success && response.data) {
        toasts.success(
          t('waitlist.referral.link_generated', 'Referral link generated'),
          t('waitlist.referral.share_to_improve', 'Share this link to improve your position in line')
        )
        return response.data.referral_link
      } else {
        throw new Error(response.error || t('waitlist.errors.referral_failed', 'Failed to generate referral link'))
      }

    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : t('waitlist.errors.unexpected', 'An unexpected error occurred')
      
      toasts.error(
        t('waitlist.errors.referral_failed', 'Failed to generate referral link'),
        errorMessage
      )

      return null
    }
  }, [t, toasts])

  const getStoredSignup = useCallback(() => {
    try {
      const stored = localStorage.getItem('waitlist_signup')
      return stored ? JSON.parse(stored) : null
    } catch (error) {
      console.warn('Failed to get stored signup:', error)
      return null
    }
  }, [])

  const hasAlreadySignedUp = useCallback((email: string): boolean => {
    const stored = getStoredSignup()
    return stored && stored.email === email.trim().toLowerCase()
  }, [getStoredSignup])

  return {
    // State
    isLoading,
    isSubmitted,
    error,
    waitlistData,
    
    // Actions
    joinWaitlist,
    checkEmailExists,
    getPosition,
    generateReferralLink,
    clearError,
    reset,
    
    // Utils
    getStoredSignup,
    hasAlreadySignedUp
  }
}