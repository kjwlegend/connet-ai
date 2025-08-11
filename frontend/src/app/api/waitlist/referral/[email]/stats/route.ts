import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(
  request: NextRequest,
  { params }: { params: { email: string } }
) {
  try {
    const email = decodeURIComponent(params.email)
    
    // Validate email format
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { success: false, error: 'Invalid email address' },
        { status: 400 }
      )
    }

    // Get user's referral stats
    const { data: userEntry, error: userError } = await supabase
      .from('waitlist')
      .select('id, status')
      .eq('email', email.toLowerCase().trim())
      .single()

    if (userError) {
      if (userError.code === 'PGRST116') { // No rows returned
        return NextResponse.json(
          { success: false, error: 'Email not found in waitlist' },
          { status: 404 }
        )
      }
      console.error('Error getting user entry:', userError)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    if (userEntry.status === 'unsubscribed') {
      return NextResponse.json(
        { success: false, error: 'Email has been unsubscribed' },
        { status: 404 }
      )
    }

    // Count referrals
    const { count: referralCount, error: countError } = await supabase
      .from('waitlist')
      .select('*', { count: 'exact', head: true })
      .eq('referred_by', userEntry.id)
      .in('status', ['pending', 'confirmed'])

    if (countError) {
      console.error('Error counting referrals:', countError)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    // Calculate bonus position (e.g., 5 positions per referral)
    const bonusPosition = (referralCount || 0) * 5

    return NextResponse.json({
      success: true,
      data: {
        referrals: referralCount || 0,
        bonus_position: bonusPosition
      }
    })

  } catch (error) {
    console.error('Get referral stats error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}