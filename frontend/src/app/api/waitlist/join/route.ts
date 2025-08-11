import { NextRequest, NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase-server'
import { Resend } from 'resend'
import { headers } from 'next/headers'

const resend = new Resend(process.env.RESEND_API_KEY)

interface WaitlistJoinRequest {
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
  timezone?: string
  country?: string
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as WaitlistJoinRequest
    const { email, ...metadata } = body

    // Validate email
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { success: false, error: 'Invalid email address' },
        { status: 400 }
      )
    }

    // Get IP address and user agent from request
    const headersList = headers()
    const forwarded = headersList.get('x-forwarded-for')
    const ip = forwarded ? forwarded.split(',')[0].trim() : headersList.get('x-real-ip')
    const userAgent = headersList.get('user-agent')

    // Check if email already exists
    const { data: existingEntry } = await supabaseServer
      .from('waitlist')
      .select('id, position, status, created_at')
      .eq('email', email.toLowerCase().trim())
      .single()

    if (existingEntry) {
      if (existingEntry.status === 'unsubscribed') {
        // Reactivate unsubscribed user
        const { data: reactivatedEntry, error } = await supabaseServer
          .from('waitlist')
          .update({ status: 'pending', updated_at: new Date().toISOString() })
          .eq('email', email.toLowerCase().trim())
          .select('id, position, created_at')
          .single()

        if (error) {
          console.error('Error reactivating waitlist entry:', error)
          return NextResponse.json(
            { success: false, error: 'Failed to rejoin waitlist' },
            { status: 500 }
          )
        }

        return NextResponse.json({
          success: true,
          data: {
            id: reactivatedEntry.id,
            email: email.toLowerCase().trim(),
            position: reactivatedEntry.position,
            total_subscribers: await getTotalSubscribers(),
            confirmation_sent: false, // Don't send confirmation again
            created_at: reactivatedEntry.created_at
          }
        })
      } else {
        // Already exists and active
        return NextResponse.json(
          { success: false, error: 'Email already registered' },
          { status: 409 }
        )
      }
    }

    // Handle referral
    let referredBy = null
    if (metadata.ref || metadata.referral) {
      const referralCode = metadata.ref || metadata.referral
      const { data: referrer } = await supabaseServer
        .from('waitlist')
        .select('id')
        .eq('referral_code', referralCode.toUpperCase())
        .single()
      
      if (referrer) {
        referredBy = referrer.id
      }
    }

    // Create new waitlist entry
    const { data: newEntry, error: insertError } = await supabaseServer
      .from('waitlist')
      .insert({
        email: email.toLowerCase().trim(),
        source: metadata.source || 'homepage',
        referrer: metadata.referrer,
        utm_source: metadata.utm_source,
        utm_medium: metadata.utm_medium,
        utm_campaign: metadata.utm_campaign,
        utm_term: metadata.utm_term,
        utm_content: metadata.utm_content,
        user_agent: userAgent,
        ip_address: ip,
        country: metadata.country,
        timezone: metadata.timezone,
        referred_by: referredBy
      })
      .select('id, email, position, referral_code, created_at')
      .single()

    if (insertError) {
      console.error('Error inserting waitlist entry:', insertError)
      return NextResponse.json(
        { success: false, error: 'Failed to join waitlist' },
        { status: 500 }
      )
    }

    const totalSubscribers = await getTotalSubscribers()

    // Send welcome email
    let confirmationSent = false
    try {
      await sendWelcomeEmail(newEntry.email, {
        position: newEntry.position,
        total: totalSubscribers,
        referralCode: newEntry.referral_code
      })
      confirmationSent = true

      // Update confirmation_sent_at
      await supabaseServer
        .from('waitlist')
        .update({ confirmation_sent_at: new Date().toISOString() })
        .eq('id', newEntry.id)

    } catch (emailError) {
      console.error('Error sending welcome email:', emailError)
      // Don't fail the request if email fails
    }

    return NextResponse.json({
      success: true,
      data: {
        id: newEntry.id,
        email: newEntry.email,
        position: newEntry.position,
        total_subscribers: totalSubscribers,
        confirmation_sent: confirmationSent,
        created_at: newEntry.created_at,
        referral_code: newEntry.referral_code
      }
    })

  } catch (error) {
    console.error('Waitlist join error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function getTotalSubscribers(): Promise<number> {
  const { count } = await supabaseServer
    .from('waitlist')
    .select('*', { count: 'exact', head: true })
    .in('status', ['pending', 'confirmed'])
  
  return count || 0
}

async function sendWelcomeEmail(
  email: string, 
  data: { position: number; total: number; referralCode: string }
) {
  const referralLink = `${process.env.NEXT_PUBLIC_APP_URL}/?ref=${data.referralCode}`
  
  await resend.emails.send({
    from: 'Connet.AI <noreply@connet.ai>',
    to: [email],
    subject: '🎉 Welcome to Connet.AI Waitlist!',
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Welcome to Connet.AI</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="text-align: center; margin-bottom: 40px;">
            <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
              <span style="color: white; font-size: 24px; font-weight: bold;">C</span>
            </div>
            <h1 style="color: #1f2937; margin: 0;">Welcome to Connet.AI! 🚀</h1>
          </div>
          
          <div style="background: linear-gradient(135deg, #f3f4f6, #e5e7eb); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
            <h2 style="color: #3b82f6; margin-top: 0;">You're #${data.position} in line!</h2>
            <p style="color: #6b7280; margin-bottom: 0; font-size: 14px;">Out of ${data.total} early adopters</p>
          </div>
          
          <div style="margin-bottom: 30px;">
            <h3 style="color: #1f2937;">What's Next?</h3>
            <p>Thank you for joining the future of AI collaboration! You're now part of an exclusive community that will shape how humans and AI work together.</p>
            <p>We'll notify you as soon as Connet.AI launches with:</p>
            <ul style="color: #6b7280;">
              <li>Early access to the platform</li>
              <li>Exclusive beta features</li>
              <li>Direct feedback channel with our team</li>
              <li>Special launch pricing</li>
            </ul>
          </div>
          
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
            <h4 style="margin-top: 0; color: #1f2937;">🎯 Skip the Line!</h4>
            <p style="margin-bottom: 15px;">Share your unique referral link and move up for every friend who joins:</p>
            <div style="background: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 12px; font-family: monospace; word-break: break-all; margin-bottom: 15px;">
              ${referralLink}
            </div>
            <a href="${referralLink}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500;">Share This Link</a>
          </div>
          
          <div style="text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
            <p>Questions? Reply to this email - we read every message!</p>
            <p style="margin-bottom: 0;">
              <a href="${process.env.NEXT_PUBLIC_APP_URL}" style="color: #3b82f6; text-decoration: none;">Visit Connet.AI</a> | 
              <a href="${process.env.NEXT_PUBLIC_APP_URL}/unsubscribe?email=${encodeURIComponent(email)}" style="color: #6b7280; text-decoration: none;">Unsubscribe</a>
            </p>
          </div>
        </body>
      </html>
    `
  })
}