/**
 * Client-side Supabase placeholder
 * Since we removed NEXT_PUBLIC_ prefixes, client-side code cannot directly access Supabase
 * All Supabase operations should now go through API routes
 */

// This file is kept for type compatibility but should not be used directly
// All Supabase operations should go through API routes (e.g., /api/waitlist/*)
export const supabase = null as any

// Database types
export interface WaitlistEntry {
  id?: string
  email: string
  source?: string
  referrer?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_term?: string
  utm_content?: string
  ref?: string
  referral?: string
  user_agent?: string
  ip_address?: string
  country?: string
  timezone?: string
  position?: number
  status?: 'pending' | 'confirmed' | 'unsubscribed'
  referral_code?: string
  referred_by?: string
  created_at?: string
  updated_at?: string
}

export interface WaitlistStats {
  total_subscribers: number
  growth_rate: number
  recent_signups: number
  countries: Record<string, number>
  sources: Record<string, number>
}
