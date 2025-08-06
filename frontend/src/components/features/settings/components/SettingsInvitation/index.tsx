"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { 
  Ticket, 
  Copy, 
  Gift,
  Users,
  TrendingUp,
  Calendar,
  Check,
  X
} from "lucide-react"

interface InvitationRecord {
  id: string
  code: string
  usedBy?: string
  usedAt?: string
  status: 'unused' | 'used' | 'expired'
  createdAt: string
}

export function SettingsInvitation() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  
  const myInvitationCode = "INVITE-XG2024-A8K9"
  const invitedCount = 12
  const availableInvites = 3
  
  const invitationRecords: InvitationRecord[] = [
    {
      id: '1',
      code: 'INV-001-XYZ',
      usedBy: '李明',
      usedAt: '2024-03-15',
      status: 'used',
      createdAt: '2024-03-01'
    },
    {
      id: '2',
      code: 'INV-002-ABC',
      status: 'unused',
      createdAt: '2024-03-10'
    },
    {
      id: '3',
      code: 'INV-003-DEF',
      usedBy: '王芳',
      usedAt: '2024-03-18',
      status: 'used',
      createdAt: '2024-03-05'
    },
    {
      id: '4',
      code: 'INV-004-GHI',
      status: 'expired',
      createdAt: '2024-02-01'
    }
  ]

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const handleGenerateCode = () => {
    // Generate new invitation code
    console.log('Generating new invitation code...')
  }

  return (
    <div className={cn(
      "flex-1 p-6",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.invitation.title')}</h1>
          <p className={cn(
            "text-sm mt-1",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {t('settings.invitation.description')}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className={cn(
            "border-border/40",
            theme === 'dark' ? "bg-card/50" : "bg-white"
          )}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={cn(
                    "text-sm",
                    theme === 'dark' ? "text-gray-400" : "text-gray-600"
                  )}>
                    {t('settings.invitation.invitedUsers')}
                  </p>
                  <p className="text-2xl font-bold mt-1">{invitedCount}</p>
                </div>
                <Users className="h-8 w-8 text-primary opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className={cn(
            "border-border/40",
            theme === 'dark' ? "bg-card/50" : "bg-white"
          )}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={cn(
                    "text-sm",
                    theme === 'dark' ? "text-gray-400" : "text-gray-600"
                  )}>
                    {t('settings.invitation.availableInvites')}
                  </p>
                  <p className="text-2xl font-bold mt-1">{availableInvites}</p>
                </div>
                <Ticket className="h-8 w-8 text-green-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className={cn(
            "border-border/40",
            theme === 'dark' ? "bg-card/50" : "bg-white"
          )}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={cn(
                    "text-sm",
                    theme === 'dark' ? "text-gray-400" : "text-gray-600"
                  )}>
                    {t('settings.invitation.bonusEarned')}
                  </p>
                  <p className="text-2xl font-bold mt-1">$60</p>
                </div>
                <Gift className="h-8 w-8 text-yellow-500 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* My Invitation Code */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.invitation.myCode')}</CardTitle>
            <CardDescription>{t('settings.invitation.myCodeDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className={cn(
                "flex-1 p-4 rounded-lg font-mono text-lg text-center",
                theme === 'dark' ? "bg-gray-800" : "bg-gray-100"
              )}>
                {myInvitationCode}
              </div>
              <Button
                onClick={() => handleCopyCode(myInvitationCode)}
                variant="outline"
                className="shrink-0"
              >
                {copiedCode === myInvitationCode ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    {t('common.copied')}
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-2" />
                    {t('common.copy')}
                  </>
                )}
              </Button>
            </div>
            <p className={cn(
              "text-sm mt-3",
              theme === 'dark' ? "text-gray-500" : "text-gray-500"
            )}>
              {t('settings.invitation.shareHint')}
            </p>
          </CardContent>
        </Card>

        {/* Generate New Codes */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.invitation.generateCodes')}</CardTitle>
            <CardDescription>{t('settings.invitation.generateDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm">
                  {t('settings.invitation.remainingCodes', { count: availableInvites })}
                </p>
                <p className={cn(
                  "text-xs mt-1",
                  theme === 'dark' ? "text-gray-500" : "text-gray-500"
                )}>
                  {t('settings.invitation.getMoreHint')}
                </p>
              </div>
              <Button
                onClick={handleGenerateCode}
                disabled={availableInvites === 0}
              >
                <Ticket className="h-4 w-4 mr-2" />
                {t('settings.invitation.generateBtn')}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Invitation History */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.invitation.history')}</CardTitle>
            <CardDescription>{t('settings.invitation.historyDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {invitationRecords.map((record) => (
                <div
                  key={record.id}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg",
                    theme === 'dark' ? "bg-gray-800/50" : "bg-gray-50"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "p-2 rounded-lg",
                      record.status === 'used' 
                        ? "bg-green-500/10 text-green-500"
                        : record.status === 'expired'
                        ? "bg-red-500/10 text-red-500"
                        : "bg-blue-500/10 text-blue-500"
                    )}>
                      <Ticket className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-mono text-sm">{record.code}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Calendar className="h-3 w-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {t('settings.invitation.created')}: {record.createdAt}
                        </span>
                        {record.usedBy && (
                          <>
                            <span className="text-xs text-muted-foreground">•</span>
                            <span className="text-xs text-muted-foreground">
                              {t('settings.invitation.usedBy')}: {record.usedBy}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        record.status === 'used' 
                          ? 'default'
                          : record.status === 'expired'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {t(`settings.invitation.status.${record.status}`)}
                    </Badge>
                    {record.status === 'unused' && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleCopyCode(record.code)}
                      >
                        {copiedCode === record.code ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Rewards Info */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">
              <TrendingUp className="h-5 w-5 inline mr-2" />
              {t('settings.invitation.rewards')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.invitation.perUserReward')}</span>
                <span className="text-sm font-medium">$5</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.invitation.totalEarned')}</span>
                <span className="text-sm font-medium text-green-500">$60</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">{t('settings.invitation.pendingRewards')}</span>
                <span className="text-sm font-medium">$10</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsInvitation