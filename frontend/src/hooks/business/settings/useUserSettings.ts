/**
 * User Settings Business Hook
 * 处理用户设置相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface UserSubscription {
  id: string
  user_id: string
  plan_type: 'basic' | 'premium' | 'enterprise'
  billing_cycle: 'monthly' | 'yearly'
  status: 'active' | 'cancelled' | 'expired'
  current_period_start: string
  current_period_end: string
  auto_renew: boolean
}

interface InviteStats {
  total_invites_sent: number
  total_invites_accepted: number
  invitation_code: string
  referral_rewards_earned: number
  current_month_invites: number
}

interface OrderHistory {
  id: string
  user_id: string
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed' | 'refunded'
  description: string
  created_at: string
}

export const useUserSettings = () => {
  const getSubscription = useCallback(async (): Promise<UserSubscription | null> => {
    try {
      const response = await fetch('/api/v1/settings/subscription', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get subscription failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get subscription failed:', error)
      toast({
        title: "Get subscription failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const upgradeSubscription = useCallback(async (
    planType: 'basic' | 'premium' | 'enterprise',
    billingCycle: 'monthly' | 'yearly' = 'monthly'
  ): Promise<any | null> => {
    try {
      const params = new URLSearchParams({
        plan_type: planType,
        billing_cycle: billingCycle,
      })

      const response = await fetch(`/api/v1/settings/subscription/upgrade?${params}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Upgrade subscription failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Subscription upgraded",
        description: `Successfully upgraded to ${planType} plan`,
      })

      return data
    } catch (error: any) {
      console.error('Upgrade subscription failed:', error)
      toast({
        title: "Upgrade failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getInviteStats = useCallback(async (): Promise<InviteStats | null> => {
    try {
      const response = await fetch('/api/v1/settings/invite-stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get invite stats failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get invite stats failed:', error)
      toast({
        title: "Get invite stats failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const getOrderHistory = useCallback(async (
    limit: number = 10,
    status?: string
  ): Promise<OrderHistory[]> => {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        ...(status && { status })
      })

      const response = await fetch(`/api/v1/settings/orders?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get order history failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get order history failed:', error)
      toast({
        title: "Get order history failed",
        description: error.message,
        variant: "destructive",
      })
      return []
    }
  }, [])

  return {
    getSubscription,
    upgradeSubscription,
    getInviteStats,
    getOrderHistory,
  }
}