"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { 
  Crown,
  Check,
  X,
  Zap,
  Sparkles,
  Rocket,
  MessageSquare,
  Brain,
  Users,
  Clock,
  Shield,
  Globe,
  FileText,
  Database,
  Gauge,
  Star,
  Key,
  AlertCircle,
  ArrowRight
} from "lucide-react"

interface PlanFeature {
  name: string
  free: boolean | string
  pro: boolean | string
  premium: boolean | string
  icon?: any
}

const membershipPlans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    currency: 'USD',
    period: 'month',
    color: 'gray',
    icon: Zap,
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 9.99,
    currency: 'USD',
    period: 'month',
    color: 'blue',
    icon: Crown,
    popular: true
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 19.99,
    currency: 'USD',
    period: 'month',
    color: 'purple',
    icon: Rocket,
    popular: false
  }
]

const planFeatures: PlanFeature[] = [
  {
    name: 'dailyMessages',
    free: 'Unlimited',
    pro: 'Unlimited',
    premium: 'Unlimited',
    icon: MessageSquare
  },
  {
    name: 'aiModels',
    free: 'GPT-4o-mini, Gemini-2.0-flash',
    pro: 'GPT-4o, Gemini-2.5-Pro',
    premium: 'All Premium Models',
    icon: Brain
  },
  {
    name: 'contextMemory',
    free: '2K tokens',
    pro: '8K tokens',
    premium: '32K tokens',
    icon: Database
  },
  {
    name: 'contactsLimit',
    free: '50',
    pro: '500',
    premium: '5000',
    icon: Users
  },
  {
    name: 'responseSpeed',
    free: false,
    pro: true,
    premium: true,
    icon: Gauge
  },
  {
    name: 'fileUpload',
    free: '5 MB',
    pro: '50 MB',
    premium: '500 MB',
    icon: FileText
  },
  {
    name: 'customPrompts',
    free: 'Unlimited',
    pro: 'Unlimited',
    premium: 'Unlimited',
    icon: Sparkles
  },
  {
    name: 'prioritySupport',
    free: false,
    pro: false,
    premium: true,
    icon: Shield
  },
  {
    name: 'exportHistory',
    free: false,
    pro: true,
    premium: true,
    icon: Clock
  },
  {
    name: 'ownApiKey',
    free: true,
    pro: true,
    premium: true,
    icon: Key
  }
]

export function SettingsMembership() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [selectedPlan, setSelectedPlan] = useState<string>('pro')
  const currentPlan = 'free' // This would come from user state
  
  const handleSelectPlan = (planId: string) => {
    setSelectedPlan(planId)
    // Handle plan selection/purchase
    console.log('Selected plan:', planId)
  }

  const getFeatureValue = (feature: PlanFeature, plan: 'free' | 'pro' | 'premium') => {
    const value = feature[plan]
    if (typeof value === 'boolean') {
      return value ? (
        <Check className="h-5 w-5 text-green-500" />
      ) : (
        <X className="h-5 w-5 text-gray-400" />
      )
    }
    return <span className="font-medium">{value}</span>
  }

  return (
    <div className={cn(
      "flex-1 p-6 overflow-y-auto",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.membership.title')}</h1>
          <p className={cn(
            "text-sm mt-1",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {t('settings.membership.description')}
          </p>
        </div>

        {/* Current Plan Status */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-gradient-to-r from-blue-900/20 to-purple-900/20" : "bg-gradient-to-r from-blue-50 to-purple-50"
        )}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-lg">
                  {t('settings.membership.currentPlan')}: {membershipPlans.find(p => p.id === currentPlan)?.name}
                </h3>
                <p className={cn(
                  "text-sm mt-1",
                  theme === 'dark' ? "text-gray-400" : "text-gray-600"
                )}>
                  {currentPlan === 'free' 
                    ? t('settings.membership.upgradeMessage')
                    : t('settings.membership.enjoyingPlan')
                  }
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span className="font-semibold">{t('settings.membership.memberSince')}: 2024-01-15</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Own API Key Notice */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className={cn(
                "p-2 rounded-lg flex-shrink-0",
                theme === 'dark' ? "bg-blue-900/50" : "bg-blue-100"
              )}>
                <Key className="h-5 w-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium mb-1">{t('settings.membership.ownApiKey')}</h4>
                <p className={cn(
                  "text-sm",
                  theme === 'dark' ? "text-gray-400" : "text-gray-600"
                )}>
                  {t('settings.membership.ownApiKeyDesc')}
                </p>
                <Button 
                  variant="link" 
                  className="px-0 h-auto mt-2"
                  onClick={() => window.location.href = '/settings/llm'}
                >
                  {t('settings.membership.configureApiKey')}
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {membershipPlans.map((plan) => {
            const Icon = plan.icon
            const isCurrentPlan = plan.id === currentPlan
            const isSelected = plan.id === selectedPlan
            
            return (
              <Card
                key={plan.id}
                className={cn(
                  "relative border-2 transition-all",
                  isSelected 
                    ? "border-primary shadow-lg scale-105" 
                    : theme === 'dark'
                      ? "border-gray-700 hover:border-gray-600"
                      : "border-gray-200 hover:border-gray-300",
                  plan.popular && "ring-2 ring-primary/20"
                )}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                      {t('settings.membership.mostPopular')}
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-4">
                  <div className={cn(
                    "w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center",
                    plan.id === 'free' 
                      ? "bg-gray-100 dark:bg-gray-800"
                      : plan.id === 'pro'
                      ? "bg-blue-100 dark:bg-blue-900/50"
                      : "bg-purple-100 dark:bg-purple-900/50"
                  )}>
                    <Icon className={cn(
                      "h-6 w-6",
                      plan.id === 'free' 
                        ? "text-gray-600"
                        : plan.id === 'pro'
                        ? "text-blue-600"
                        : "text-purple-600"
                    )} />
                  </div>
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">
                      ${plan.price}
                    </span>
                    {plan.price > 0 && (
                      <span className="text-sm text-muted-foreground">/{t('settings.membership.perMonth')}</span>
                    )}
                  </div>
                  {isCurrentPlan && (
                    <Badge variant="secondary" className="mt-2">
                      {t('settings.membership.current')}
                    </Badge>
                  )}
                </CardHeader>

                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    {planFeatures.slice(0, 5).map((feature) => {
                      const Icon = feature.icon
                      return (
                        <div key={feature.name} className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4 text-muted-foreground" />
                            <span>{t(`settings.membership.features.${feature.name}`)}</span>
                          </div>
                          {getFeatureValue(feature, plan.id as 'free' | 'pro' | 'premium')}
                        </div>
                      )
                    })}
                  </div>
                </CardContent>

                <CardFooter>
                  <Button
                    className="w-full"
                    variant={isCurrentPlan ? "outline" : plan.id === 'pro' ? "default" : "outline"}
                    disabled={isCurrentPlan}
                    onClick={() => handleSelectPlan(plan.id)}
                  >
                    {isCurrentPlan 
                      ? t('settings.membership.currentPlan')
                      : plan.price === 0 
                      ? t('settings.membership.downgrade')
                      : t('settings.membership.upgrade')
                    }
                  </Button>
                </CardFooter>
              </Card>
            )
          })}
        </div>

        {/* Detailed Feature Comparison */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.membership.detailedComparison')}</CardTitle>
            <CardDescription>{t('settings.membership.comparisonDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className={cn(
                    "border-b",
                    theme === 'dark' ? "border-gray-700" : "border-gray-200"
                  )}>
                    <th className="text-left py-3 px-4">{t('settings.membership.features.title')}</th>
                    <th className="text-center py-3 px-4">Free</th>
                    <th className="text-center py-3 px-4">
                      <div className="flex items-center justify-center gap-2">
                        Pro
                        <Badge variant="secondary" className="text-xs">Popular</Badge>
                      </div>
                    </th>
                    <th className="text-center py-3 px-4">Premium</th>
                  </tr>
                </thead>
                <tbody>
                  {planFeatures.map((feature, index) => {
                    const Icon = feature.icon
                    return (
                      <tr 
                        key={feature.name}
                        className={cn(
                          "border-b",
                          theme === 'dark' ? "border-gray-800" : "border-gray-100"
                        )}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {t(`settings.membership.features.${feature.name}`)}
                            </span>
                          </div>
                        </td>
                        <td className="text-center py-3 px-4">
                          {getFeatureValue(feature, 'free')}
                        </td>
                        <td className="text-center py-3 px-4">
                          {getFeatureValue(feature, 'pro')}
                        </td>
                        <td className="text-center py-3 px-4">
                          {getFeatureValue(feature, 'premium')}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQ or Additional Info */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.membership.faq')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">{t('settings.membership.faq1Question')}</h4>
              <p className={cn(
                "text-sm",
                theme === 'dark' ? "text-gray-400" : "text-gray-600"
              )}>
                {t('settings.membership.faq1Answer')}
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-2">{t('settings.membership.faq2Question')}</h4>
              <p className={cn(
                "text-sm",
                theme === 'dark' ? "text-gray-400" : "text-gray-600"
              )}>
                {t('settings.membership.faq2Answer')}
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-2">{t('settings.membership.faq3Question')}</h4>
              <p className={cn(
                "text-sm",
                theme === 'dark' ? "text-gray-400" : "text-gray-600"
              )}>
                {t('settings.membership.faq3Answer')}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsMembership