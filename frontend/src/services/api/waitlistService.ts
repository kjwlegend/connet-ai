/**
 * Waitlist Service - API calls for waitlist functionality
 */

import { apiClient } from './client'
import { ApiResponse } from '../types'

export interface WaitlistEntry {
  id?: string
  email: string
  source?: string
  referrer?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  user_agent?: string
  ip_address?: string
  country?: string
  created_at?: string
  status?: 'pending' | 'confirmed' | 'unsubscribed'
}

export interface WaitlistResponse {
  id: string
  email: string
  position: number
  total_subscribers: number
  confirmation_sent: boolean
  created_at: string
  estimated_launch_date?: string
}

export interface WaitlistStats {
  total_subscribers: number
  growth_rate: number
  recent_signups: number
  countries: Record<string, number>
  sources: Record<string, number>
}

export class WaitlistService {
  /**
   * Join the waitlist
   */
  async joinWaitlist(entry: WaitlistEntry): Promise<ApiResponse<WaitlistResponse>> {
    try {
      // Collect additional context data
      const enrichedEntry = {
        ...entry,
        source: entry.source || 'homepage',
        referrer: entry.referrer || (typeof document !== 'undefined' ? document.referrer : undefined),
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
        // Get UTM parameters from URL
        ...(this.getUTMParameters()),
        // Get user location (if available)
        ...(await this.getUserLocation()),
      }

      // Call API route
      const response = await apiClient.post<WaitlistResponse>('/api/waitlist/join', enrichedEntry)

      if (response.success && response.data) {
        // Store successful signup in localStorage for analytics
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('waitlist_signup', JSON.stringify({
            email: entry.email,
            position: response.data.position,
            joined_at: new Date().toISOString()
          }))
        }

        // Track conversion event
        this.trackConversion(response.data)
      }

      return response
    } catch (error) {
      console.error('Failed to join waitlist:', error)
      return {
        success: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to join waitlist'
      }
    }
  }

  /**
   * Check if email is already in waitlist
   */
  async checkEmail(email: string): Promise<ApiResponse<{ exists: boolean; position?: number }>> {
    try {
      const response = await apiClient.get<{ exists: boolean; position?: number }>(
        `/api/waitlist/check/${encodeURIComponent(email)}`
      )
      return response
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to check email'
      }
    }
  }

  /**
   * Get waitlist position by email
   */
  async getPosition(email: string): Promise<ApiResponse<{ position: number; total: number }>> {
    try {
      const response = await apiClient.get<{ position: number; total: number; status: string; referral_code?: string }>(
        `/api/waitlist/position/${encodeURIComponent(email)}`
      )
      return {
        success: response.success,
        data: response.data ? { position: response.data.position, total: response.data.total } : null,
        error: response.error || null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to get position'
      }
    }
  }

  /**
   * Confirm email subscription
   */
  async confirmEmail(token: string): Promise<ApiResponse<{ confirmed: boolean }>> {
    // For now, return success as we're using direct Supabase
    return {
      success: true,
      data: { confirmed: true },
      error: null
    }
  }

  /**
   * Unsubscribe from waitlist
   */
  async unsubscribe(token: string): Promise<ApiResponse<{ unsubscribed: boolean }>> {
    // For now, return success as we're using direct Supabase
    return {
      success: true,
      data: { unsubscribed: true },
      error: null
    }
  }

  /**
   * Get public waitlist statistics
   */
  async getPublicStats(): Promise<ApiResponse<WaitlistStats>> {
    try {
      const { count: totalCount } = await supabase
        .from('waitlist')
        .select('*', { count: 'exact', head: true })

      return {
        success: true,
        data: {
          total_subscribers: totalCount || 0,
          growth_rate: 0,
          recent_signups: 0,
          countries: {},
          sources: {}
        },
        error: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to get stats'
      }
    }
  }

  /**
   * Share referral link
   */
  async generateReferralLink(email: string): Promise<ApiResponse<{ referral_code: string; referral_link: string }>> {
    // Generate a simple referral code
    const referral_code = btoa(email).replace(/[^a-zA-Z0-9]/g, '').slice(0, 8)
    const referral_link = `${window.location.origin}?ref=${referral_code}`
    
    return {
      success: true,
      data: { referral_code, referral_link },
      error: null
    }
  }

  /**
   * Get referral statistics
   */
  async getReferralStats(email: string): Promise<ApiResponse<{ referrals: number; bonus_position: number }>> {
    return {
      success: true,
      data: { referrals: 0, bonus_position: 0 },
      error: null
    }
  }

  // Private helper methods

  /**
   * Extract UTM parameters from current URL
   */
  private getUTMParameters(): Record<string, string> {
    if (typeof window === 'undefined') return {}
    
    const params = new URLSearchParams(window.location.search)
    const utmParams: Record<string, string> = {}

    // Standard UTM parameters
    const utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    utmKeys.forEach(key => {
      const value = params.get(key)
      if (value) {
        utmParams[key] = value
      }
    })

    // Additional tracking parameters
    const additionalKeys = ['ref', 'referral', 'source']
    additionalKeys.forEach(key => {
      const value = params.get(key)
      if (value) {
        utmParams[key] = value
      }
    })

    return utmParams
  }

  /**
   * Get user's approximate location (country only for privacy)
   */
  private async getUserLocation(): Promise<{ country?: string; timezone?: string }> {
    if (typeof Intl === 'undefined') return {}
    
    try {
      // Use timezone to approximate location
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      
      // Try to get country from timezone
      let country: string | undefined
      if (timezone) {
        const parts = timezone.split('/')
        if (parts.length > 1) {
          // This is a rough approximation - in production you might use a proper geolocation service
          country = parts[0] === 'America' ? 'US' : 
                   parts[0] === 'Europe' ? 'EU' : 
                   parts[0] === 'Asia' ? 'AS' : 
                   parts[0] === 'Australia' ? 'AU' : 
                   parts[0]
        }
      }

      return { country, timezone }
    } catch (error) {
      console.warn('Could not determine user location:', error)
      return {}
    }
  }

  /**
   * Track conversion event for analytics
   */
  private trackConversion(data: WaitlistResponse) {
    if (typeof window === 'undefined') return
    
    try {
      // Google Analytics 4 event
      if (typeof gtag !== 'undefined') {
        gtag('event', 'waitlist_signup', {
          event_category: 'engagement',
          event_label: 'homepage_waitlist',
          value: data.position,
          user_id: data.email
        })
      }

      // Facebook Pixel
      if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead', {
          content_name: 'Waitlist Signup',
          content_category: 'waitlist',
          value: 1,
          currency: 'USD'
        })
      }

      // Custom analytics event
      if (window.analytics) {
        window.analytics.track('Waitlist Joined', {
          email: data.email,
          position: data.position,
          total_subscribers: data.total_subscribers,
          source: 'homepage',
          timestamp: new Date().toISOString()
        })
      }

      // PostHog
      if (window.posthog) {
        window.posthog.capture('waitlist_signup', {
          email: data.email,
          position: data.position,
          total_subscribers: data.total_subscribers
        })
      }

    } catch (error) {
      console.warn('Failed to track conversion:', error)
    }
  }
}

// Export singleton instance
export const waitlistService = new WaitlistService()

// Type declarations for external analytics libraries
declare global {
  interface Window {
    gtag?: (command: string, action: string, params?: any) => void
    fbq?: (command: string, action: string, params?: any) => void
    analytics?: {
      track: (event: string, properties?: any) => void
    }
    posthog?: {
      capture: (event: string, properties?: any) => void
    }
  }
}