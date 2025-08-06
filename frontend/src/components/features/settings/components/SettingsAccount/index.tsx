"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { 
  User, 
  Mail, 
  Lock, 
  Camera,
  Shield,
  AlertCircle,
  Check
} from "lucide-react"

export function SettingsAccount() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  
  const [formData, setFormData] = useState({
    nickname: "张晓明",
    email: "zhangxiaoming@example.com",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  const handleSave = async () => {
    setIsSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSaving(false)
    setIsEditing(false)
  }

  return (
    <div className={cn(
      "flex-1 p-6",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.account.title')}</h1>
          <p className={cn(
            "text-sm mt-1",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {t('settings.account.description')}
          </p>
        </div>

        {/* Profile Card */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.account.profile')}</CardTitle>
            <CardDescription>{t('settings.account.profileDesc')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Avatar Section */}
            <div className="flex items-center space-x-6">
              <Avatar className="h-24 w-24">
                <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=user1" />
                <AvatarFallback>ZX</AvatarFallback>
              </Avatar>
              <div className="space-y-2">
                <Button variant="outline" size="sm">
                  <Camera className="h-4 w-4 mr-2" />
                  {t('settings.account.changeAvatar')}
                </Button>
                <p className={cn(
                  "text-xs",
                  theme === 'dark' ? "text-gray-500" : "text-gray-500"
                )}>
                  {t('settings.account.avatarHint')}
                </p>
              </div>
            </div>

            {/* Basic Info */}
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="nickname">
                  <User className="h-4 w-4 inline mr-2" />
                  {t('settings.account.nickname')}
                </Label>
                <Input
                  id="nickname"
                  value={formData.nickname}
                  onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                  disabled={!isEditing}
                  className={cn(
                    !isEditing && "bg-muted/50"
                  )}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="email">
                  <Mail className="h-4 w-4 inline mr-2" />
                  {t('settings.account.email')}
                </Label>
                <div className="flex items-center gap-2">
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={!isEditing}
                    className={cn(
                      "flex-1",
                      !isEditing && "bg-muted/50"
                    )}
                  />
                  <Badge variant="secondary" className="shrink-0">
                    <Check className="h-3 w-3 mr-1" />
                    {t('settings.account.verified')}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-2 pt-4 border-t">
              {!isEditing ? (
                <Button onClick={() => setIsEditing(true)}>
                  {t('settings.account.edit')}
                </Button>
              ) : (
                <>
                  <Button 
                    variant="outline" 
                    onClick={() => setIsEditing(false)}
                    disabled={isSaving}
                  >
                    {t('common.cancel')}
                  </Button>
                  <Button 
                    onClick={handleSave}
                    disabled={isSaving}
                  >
                    {isSaving ? t('common.saving') : t('common.save')}
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Security Card */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">
              <Shield className="h-5 w-5 inline mr-2" />
              {t('settings.account.security')}
            </CardTitle>
            <CardDescription>{t('settings.account.securityDesc')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="currentPassword">
                  <Lock className="h-4 w-4 inline mr-2" />
                  {t('settings.account.currentPassword')}
                </Label>
                <Input
                  id="currentPassword"
                  type="password"
                  value={formData.currentPassword}
                  onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
                  placeholder={t('settings.account.enterCurrentPassword')}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="newPassword">
                  <Lock className="h-4 w-4 inline mr-2" />
                  {t('settings.account.newPassword')}
                </Label>
                <Input
                  id="newPassword"
                  type="password"
                  value={formData.newPassword}
                  onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                  placeholder={t('settings.account.enterNewPassword')}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="confirmPassword">
                  <Lock className="h-4 w-4 inline mr-2" />
                  {t('settings.account.confirmPassword')}
                </Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  placeholder={t('settings.account.enterConfirmPassword')}
                />
              </div>
            </div>

            <div className={cn(
              "flex items-start gap-2 p-3 rounded-lg",
              theme === 'dark' ? "bg-yellow-900/20" : "bg-yellow-50"
            )}>
              <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-yellow-600">
                  {t('settings.account.passwordHint')}
                </p>
                <p className={cn(
                  "mt-1",
                  theme === 'dark' ? "text-gray-400" : "text-gray-600"
                )}>
                  {t('settings.account.passwordRequirements')}
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t">
              <Button variant="default">
                <Lock className="h-4 w-4 mr-2" />
                {t('settings.account.updatePassword')}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Account Status */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.account.status')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.account.memberSince')}</span>
                <span className="text-sm font-medium">2024-01-15</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.account.lastLogin')}</span>
                <span className="text-sm font-medium">2024-03-20 14:30</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.account.accountType')}</span>
                <Badge variant="default">Pro</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsAccount