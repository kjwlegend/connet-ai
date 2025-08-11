/**
 * Server-side Supabase client
 * Uses server-side environment variables (without NEXT_PUBLIC prefix)
 */

import { createClient } from '@supabase/supabase-js'

// Ensure we're running on server-side
if (typeof window !== 'undefined') {
  throw new Error('supabase-server.ts should only be used on the server side')
}

const supabaseUrl = process.env.SUPABASE_URL
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY

if (!supabaseUrl) {
  throw new Error('Missing SUPABASE_URL environment variable')
}

if (!supabaseAnonKey) {
  throw new Error('Missing SUPABASE_ANON_KEY environment variable')
}

export const supabaseServer = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
})

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