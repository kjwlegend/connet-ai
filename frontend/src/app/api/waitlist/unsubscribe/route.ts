import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

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

    // Update user status to unsubscribed
    const { data: updatedEntry, error } = await supabase
      .from('waitlist')
      .update({ 
        status: 'unsubscribed',
        unsubscribed_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('email', email.toLowerCase().trim())
      .select('id')
      .single()

    if (error) {
      if (error.code === 'PGRST116') { // No rows returned
        return NextResponse.json(
          { success: false, error: 'Email not found in waitlist' },
          { status: 404 }
        )
      }
      console.error('Error unsubscribing:', error)
      return NextResponse.json(
        { success: false, error: 'Database error' },
        { status: 500 }
      )
    }

    // Send unsubscribe confirmation email
    try {
      await resend.emails.send({
        from: 'Connet.AI <noreply@connet.ai>',
        to: [email],
        subject: 'You\'ve been unsubscribed from Connet.AI',
        html: `
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Unsubscribed - Connet.AI</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
              <div style="text-align: center; margin-bottom: 40px;">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                  <span style="color: white; font-size: 24px; font-weight: bold;">C</span>
                </div>
                <h1 style="color: #1f2937; margin: 0;">You've been unsubscribed</h1>
              </div>
              
              <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 30px; text-align: center; margin-bottom: 30px;">
                <p>We're sorry to see you go! You've been successfully removed from the Connet.AI waitlist.</p>
                <p style="margin-bottom: 0;">If this was a mistake, you can always <a href="${process.env.NEXT_PUBLIC_APP_URL}" style="color: #3b82f6; text-decoration: none;">rejoin the waitlist</a>.</p>
              </div>
              
              <div style="text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                <p>Questions? Reply to this email - we read every message!</p>
                <p style="margin-bottom: 0;">
                  <a href="${process.env.NEXT_PUBLIC_APP_URL}" style="color: #3b82f6; text-decoration: none;">Visit Connet.AI</a>
                </p>
              </div>
            </body>
          </html>
        `
      })
    } catch (emailError) {
      console.error('Error sending unsubscribe confirmation:', emailError)
      // Don't fail the request if email fails
    }

    return NextResponse.json({
      success: true,
      data: {
        unsubscribed: true,
        message: 'Successfully unsubscribed from waitlist'
      }
    })

  } catch (error) {
    console.error('Unsubscribe error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}