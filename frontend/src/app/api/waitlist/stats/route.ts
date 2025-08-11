import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  try {
    // Get public statistics using the view
    const { data: stats, error } = await supabase
      .from('waitlist_public_stats')
      .select('*')
      .single()

    if (error) {
      console.error('Error getting waitlist stats:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to get statistics' },
        { status: 500 }
      )
    }

    // Calculate growth rate (last 7 days vs previous 7 days)
    const { data: recentData } = await supabase
      .from('waitlist')
      .select('created_at')
      .in('status', ['pending', 'confirmed'])
      .gte('created_at', new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString())

    let growthRate = 0
    if (recentData && recentData.length > 0) {
      const now = new Date()
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      const fourteenDaysAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000)

      const lastWeek = recentData.filter(entry => 
        new Date(entry.created_at) > sevenDaysAgo
      ).length

      const previousWeek = recentData.filter(entry => {
        const date = new Date(entry.created_at)
        return date > fourteenDaysAgo && date <= sevenDaysAgo
      }).length

      if (previousWeek > 0) {
        growthRate = ((lastWeek - previousWeek) / previousWeek) * 100
      }
    }

    return NextResponse.json({
      success: true,
      data: {
        total_subscribers: stats.total_subscribers,
        recent_signups: stats.recent_signups,
        growth_rate: Number(growthRate.toFixed(2)),
        countries: stats.countries || {},
        sources: stats.sources || {}
      }
    })

  } catch (error) {
    console.error('Waitlist stats error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}