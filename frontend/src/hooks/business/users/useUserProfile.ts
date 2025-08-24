/**
 * User Profile Business Hook
 * 处理用户资料相关的业务逻辑
 */

import { useCallback } from 'react'
import { toast } from '@/components/ui/use-toast'

interface UserProfile {
  id: string
  email: string
  full_name: string
  username?: string
  bio?: string
  location?: string
  website?: string
  avatar_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
  last_login_at?: string
  preferences?: UserPreferences
  social_links?: SocialLinks
  privacy_settings?: PrivacySettings
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'zh'
  notifications: {
    email: boolean
    push: boolean
    mentions: boolean
    follows: boolean
    likes: boolean
    comments: boolean
  }
  privacy: {
    profile_visibility: 'public' | 'friends' | 'private'
    show_online_status: boolean
    allow_friend_requests: boolean
  }
}

interface SocialLinks {
  twitter?: string
  linkedin?: string
  github?: string
  personal_website?: string
}

interface PrivacySettings {
  profile_visibility: 'public' | 'friends' | 'private'
  show_email: boolean
  show_online_status: boolean
  allow_friend_requests: boolean
  allow_direct_messages: boolean
}

export const useUserProfile = () => {
  const getUserProfile = useCallback(async (userId: string): Promise<UserProfile | null> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}/profile`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Get user profile failed: ${response.status} - ${error}`)
      }

      return await response.json()
    } catch (error: any) {
      console.error('Get user profile failed:', error)
      toast({
        title: "Get user profile failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updateProfile = useCallback(async (
    userId: string,
    profileData: Partial<UserProfile>
  ): Promise<UserProfile | null> => {
    try {
      const response = await fetch(`/api/v1/users/${userId}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(profileData),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update profile failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Profile updated",
        description: "Your profile has been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update profile failed:', error)
      toast({
        title: "Update profile failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updatePreferences = useCallback(async (
    preferences: Partial<UserPreferences>
  ): Promise<UserPreferences | null> => {
    try {
      const response = await fetch('/api/v1/users/me/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(preferences),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update preferences failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Preferences updated",
        description: "Your preferences have been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update preferences failed:', error)
      toast({
        title: "Update preferences failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updateSocialLinks = useCallback(async (
    socialLinks: SocialLinks
  ): Promise<SocialLinks | null> => {
    try {
      const response = await fetch('/api/v1/users/me/social-links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(socialLinks),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update social links failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Social links updated",
        description: "Your social links have been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update social links failed:', error)
      toast({
        title: "Update social links failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const updatePrivacySettings = useCallback(async (
    privacySettings: Partial<PrivacySettings>
  ): Promise<PrivacySettings | null> => {
    try {
      const response = await fetch('/api/v1/users/me/privacy', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(privacySettings),
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Update privacy settings failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Privacy settings updated",
        description: "Your privacy settings have been updated successfully",
      })

      return data
    } catch (error: any) {
      console.error('Update privacy settings failed:', error)
      toast({
        title: "Update privacy settings failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  const uploadAvatar = useCallback(async (file: File): Promise<string | null> => {
    try {
      const formData = new FormData()
      formData.append('avatar', file)

      const response = await fetch('/api/v1/users/me/avatar', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`Upload avatar failed: ${response.status} - ${error}`)
      }

      const data = await response.json()
      
      toast({
        title: "Avatar uploaded",
        description: "Your avatar has been updated successfully",
      })

      return data.avatar_url
    } catch (error: any) {
      console.error('Upload avatar failed:', error)
      toast({
        title: "Upload avatar failed",
        description: error.message,
        variant: "destructive",
      })
      return null
    }
  }, [])

  return {
    getUserProfile,
    updateProfile,
    updatePreferences,
    updateSocialLinks,
    updatePrivacySettings,
    uploadAvatar,
  }
}