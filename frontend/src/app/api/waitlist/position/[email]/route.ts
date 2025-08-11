import { NextRequest, NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase-server'

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

    // Get user's position
    const { data: entry, error } = await supabaseServer
      .from('waitlist')
      .select('position, status, referral_code')
      .eq('email', email.toLowerCase().trim())
      .single()

    if (error) {
      if (error.code === 'PGRST116') { // No rows returned
        return NextResponse.json(
          { success: false, error: 'Email not found in waitlist' },
          { status: 404 }
        )
      }
      console.error('Error getting position:', error)
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

    // Get total count
    const { count: totalCount, error: countError } = await supabaseServer
      .from('waitlist')
      .select('*', { count: 'exact', head: true })
      .in('status', ['pending', 'confirmed'])

    if (countError) {
      console.error('Error getting total count:', countError)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        position: entry.position,
        total: totalCount || 0,
        status: entry.status,
        referral_code: entry.referral_code
      }
    })

  } catch (error) {
    console.error('Get position error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}