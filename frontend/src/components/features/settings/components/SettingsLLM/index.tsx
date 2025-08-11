'use client'

import { useState, useMemo } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp, DollarSign, Zap, Calendar, Crown } from 'lucide-react'
import { useTranslations } from '@/lib/i18n/client'
import { useTheme } from 'next-themes'
import { cn } from '@/lib/utils'

interface MembershipLimits {
  premium: number
  pro: number
  basic: number | 'unlimited'
}

const TOKEN_LIMITS: Record<string, MembershipLimits> = {
  free: {
    premium: 0,
    pro: 100000,
    basic: 'unlimited'
  },
  pro: {
    premium: 500000,
    pro: 3000000,
    basic: 'unlimited'
  },
  premium: {
    premium: 2000000,
    pro: 10000000,
    basic: 'unlimited'
  }
}

interface DailyUsage {
  date: string
  day: string
  tokens: number
  cost: number
  month: string
}

const generateMockData = (): DailyUsage[] => {
  const data: DailyUsage[] = []
  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  
  for (let month = 0; month < 12; month++) {
    const daysInMonth = new Date(currentYear, month + 1, 0).getDate()
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, month, day)
      const dateString = date.toISOString().split('T')[0]
      const monthString = date.toLocaleString('default', { month: 'long', year: 'numeric' })
      
      const randomTokens = Math.floor(Math.random() * 150000) + 30000
      data.push({
        date: dateString,
        day: day.toString(),
        tokens: randomTokens,
        cost: randomTokens * 0.00001,
        month: monthString,
      })
    }
  }
  
  return data
}

const mockDailyUsage = generateMockData()

export function SettingsLLM() {
  const t = useTranslations()
  const { theme } = useTheme()
  const currentPlan = 'pro'
  
  const availableMonths = useMemo(() => {
    const months = [...new Set(mockDailyUsage.map(d => d.month))]
    return months
  }, [])
  
  const currentMonth = useMemo(() => {
    const now = new Date()
    return now.toLocaleString('default', { month: 'long', year: 'numeric' })
  }, [])
  
  const [selectedMonth, setSelectedMonth] = useState<string>(currentMonth)
  
  const currentLimits = TOKEN_LIMITS[currentPlan]
  const premiumUsage = 180000
  const proUsage = 2100000
  const basicUsage = 'unlimited'
  
  const nextResetDate = useMemo(() => {
    const now = new Date()
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)
    return nextMonth.toLocaleDateString('default', { 
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    })
  }, [])
  
  const filteredData = useMemo(() => {
    return mockDailyUsage.filter(d => d.month === selectedMonth)
  }, [selectedMonth])
  
  const totalTokens = filteredData.reduce((sum, day) => sum + day.tokens, 0)
  const totalCost = filteredData.reduce((sum, day) => sum + day.cost, 0)
  const maxTokens = Math.max(...filteredData.map((d) => d.tokens))
  const avgTokensPerDay = Math.round(totalTokens / filteredData.length)

  const membershipPrice = 9.99
  const savings = totalCost - membershipPrice
  
  const chartData = filteredData.map(d => ({
    day: parseInt(d.day),
    tokens: d.tokens / 1000,
    cost: d.cost,
  })).sort((a, b) => a.day - b.day)

  return (
    <div
      className={cn(
        'flex-1 p-6 overflow-y-auto',
        theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
      )}
    >
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.usage.title')}</h1>
          <p
            className={cn(
              'text-sm mt-1',
              theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
            )}
          >
            {t('settings.usage.description')}
          </p>
        </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">{t('settings.usage.selectMonth')}:</span>
        </div>
        <Select value={selectedMonth} onValueChange={setSelectedMonth}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select a month" />
          </SelectTrigger>
          <SelectContent>
            {availableMonths.map((month) => (
              <SelectItem key={month} value={month}>
                {month}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t('settings.usage.totalTokens')}
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(totalTokens / 1000000).toFixed(2)}M
            </div>
            <p className="text-xs text-muted-foreground">
              {selectedMonth}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t('settings.usage.equivalentCost')}
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalCost.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              {t('settings.usage.ifPayAsYouGo')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t('settings.usage.yourPlan')}
            </CardTitle>
            <Badge variant="secondary" className="ml-2">
              Pro
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${membershipPrice}</div>
            <p className="text-xs text-muted-foreground">
              {t('settings.usage.perMonth')}
            </p>
          </CardContent>
        </Card>

        <Card
          className={cn(
            'border-2',
            savings > 0 ? 'border-green-500' : 'border-border'
          )}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t('settings.usage.yourSavings')}
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div
              className={cn(
                'text-2xl font-bold',
                savings > 0 ? 'text-green-500' : ''
              )}
            >
              ${Math.abs(savings).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              {savings > 0
                ? t('settings.usage.saved')
                : t('settings.usage.moreThanPlan')}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('settings.usage.dailyUsage')}</CardTitle>
          <CardDescription>
            Token usage for {selectedMonth}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {t('settings.usage.average')}:{' '}
                {(avgTokensPerDay / 1000).toFixed(1)}K tokens/day
              </span>
              <span className="text-muted-foreground">
                {t('settings.usage.peak')}: {(maxTokens / 1000).toFixed(1)}K
                tokens
              </span>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke={theme === 'dark' ? '#374151' : '#e5e7eb'}
                />
                <XAxis 
                  dataKey="day" 
                  stroke={theme === 'dark' ? '#9ca3af' : '#6b7280'}
                  fontSize={12}
                  label={{ 
                    value: 'Day of Month', 
                    position: 'insideBottom', 
                    offset: -5,
                    style: { fill: theme === 'dark' ? '#9ca3af' : '#6b7280' }
                  }}
                />
                <YAxis 
                  stroke={theme === 'dark' ? '#9ca3af' : '#6b7280'}
                  fontSize={12}
                  label={{ 
                    value: 'Tokens (K)', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fill: theme === 'dark' ? '#9ca3af' : '#6b7280' }
                  }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
                    border: '1px solid ' + (theme === 'dark' ? '#374151' : '#e5e7eb'),
                    borderRadius: '6px',
                  }}
                  labelStyle={{
                    color: theme === 'dark' ? '#e5e7eb' : '#111827',
                  }}
                  formatter={(value: number) => [`${value.toFixed(1)}K tokens`, 'Usage']}
                  labelFormatter={(label) => `Day ${label}`}
                />
                <Bar 
                  dataKey="tokens" 
                  fill={theme === 'dark' ? '#8b5cf6' : '#7c3aed'}
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t('settings.usage.modelBreakdown')}</CardTitle>
            <CardDescription>
              {t('settings.usage.modelBreakdownDesc')} {selectedMonth}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-700 dark:text-blue-400">
                  {t('settings.usage.resetTime')}
                </span>
              </div>
              <span className="text-sm text-blue-600 dark:text-blue-300 font-medium">
                {nextResetDate}
              </span>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Crown className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm font-medium">
                    {t('settings.usage.premiumModels')}
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {currentLimits.premium === 0 ? t('settings.usage.notAvailable') : 
                   `${(premiumUsage / 1000).toFixed(0)}K / ${(currentLimits.premium / 1000).toFixed(0)}K`}
                </span>
              </div>
              <Progress 
                value={currentLimits.premium === 0 ? 0 : (premiumUsage / currentLimits.premium) * 100} 
                className="h-2" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                GPT-o1, Claude-4 Opus, GPT-4o
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium">
                    {t('settings.usage.proModels')}
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {(proUsage / 1000000).toFixed(1)}M / {(currentLimits.pro / 1000000).toFixed(0)}M
                </span>
              </div>
              <Progress value={(proUsage / currentLimits.pro) * 100} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                GPT-5, Claude-4 Sonnet, Gemini Pro
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="h-4 w-4 rounded-full bg-green-500 flex items-center justify-center text-[8px] text-white font-bold">∞</span>
                  <span className="text-sm font-medium">
                    {t('settings.usage.basicModels')}
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">{t('settings.usage.unlimited')}</span>
              </div>
              <Progress value={100} className="h-2 bg-green-100 dark:bg-green-900/20" />
              <div className="h-2 bg-green-500 rounded-full mt-[-8px]" />
              <p className="text-xs text-muted-foreground mt-1">
                GPT-4o-mini, Kimi, DeepSeek, Gemini Flash
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('settings.usage.comparison')}</CardTitle>
            <CardDescription>
              {t('settings.usage.comparisonDesc')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <h4 className="font-semibold text-green-700 dark:text-green-400 mb-2">
                  {t('settings.usage.withMembership')}
                </h4>
                <ul className="space-y-1 text-sm text-green-600 dark:text-green-300">
                  <li>• {t('settings.usage.unlimitedConversations')}</li>
                  <li>• {t('settings.usage.premiumModels')}</li>
                  <li>• {t('settings.usage.priorityAccess')}</li>
                  <li>
                    • {t('settings.usage.fixedPrice')}: ${membershipPrice}/month
                  </li>
                </ul>
              </div>

              <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800">
                <h4 className="font-semibold text-gray-700 dark:text-gray-400 mb-2">
                  {t('settings.usage.withoutMembership')}
                </h4>
                <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-300">
                  <li>• {t('settings.usage.payPerUse')}</li>
                  <li>• {t('settings.usage.limitedModels')}</li>
                  <li>• {t('settings.usage.rateLimits')}</li>
                  <li>
                    • {t('settings.usage.estimatedCost')}: $
                    {totalCost.toFixed(2)}/month
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      </div>
    </div>
  )
}