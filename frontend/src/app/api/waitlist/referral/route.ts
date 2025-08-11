import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json()
    
    // Validate email format
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { success: false, error: 'Invalid email address' },
        { status: 400 }
      )
    }

    // Get user's referral code
    const { data: entry, error } = await supabase
      .from('waitlist')
      .select('referral_code, status')
      .eq('email', email.toLowerCase().trim())
      .single()

    if (error) {
      if (error.code === 'PGRST116') { // No rows returned
        return NextResponse.json(
          { success: false, error: 'Email not found in waitlist' },
          { status: 404 }
        )
      }
      console.error('Error getting referral code:', error)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    if (entry.status === 'unsubscribed') {
      return NextResponse.json(
        { success: false, error: 'Email has been unsubscribed' },
        { status: 404 }
      )
    }

    const referralLink = `${process.env.NEXT_PUBLIC_APP_URL}/?ref=${entry.referral_code}`

    return NextResponse.json({
      success: true,
      data: {
        referral_code: entry.referral_code,
        referral_link: referralLink
      }
    })

  } catch (error) {
    console.error('Generate referral link error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}