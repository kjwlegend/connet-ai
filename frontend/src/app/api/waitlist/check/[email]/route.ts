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

    // Check if email exists in waitlist
    const { data: entry, error } = await supabaseServer
      .from('waitlist')
      .select('id, position, status')
      .eq('email', email.toLowerCase().trim())
      .single()

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
      console.error('Error checking email:', error)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    const exists = !!entry && entry.status !== 'unsubscribed'
    
    return NextResponse.json({
      success: true,
      data: {
        exists,
        position: exists ? entry?.position : undefined
      }
    })

  } catch (error) {
    console.error('Check email error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}