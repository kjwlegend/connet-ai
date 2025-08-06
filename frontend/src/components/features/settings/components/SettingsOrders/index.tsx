"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useTranslations } from "@/lib/i18n/client"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { 
  ShoppingBag, 
  Package,
  Clock,
  CheckCircle,
  XCircle,
  Download,
  Eye,
  CreditCard,
  Calendar,
  RefreshCw,
  DollarSign
} from "lucide-react"

interface Order {
  id: string
  orderNumber: string
  date: string
  status: 'pending' | 'processing' | 'completed' | 'cancelled' | 'refunded'
  plan: string
  amount: number
  currency: string
  paymentMethod: string
  description: string
}

export function SettingsOrders() {
  const t = useTranslations()
  const { theme } = useTheme()
  const [activeTab, setActiveTab] = useState('all')
  
  const orders: Order[] = [
    {
      id: '1',
      orderNumber: 'ORD-2024-001',
      date: '2024-03-15',
      status: 'completed',
      plan: 'Pro Plan',
      amount: 9.99,
      currency: 'USD',
      paymentMethod: 'Credit Card',
      description: 'Pro Plan - Monthly'
    },
    {
      id: '2',
      orderNumber: 'ORD-2024-002',
      date: '2024-02-15',
      status: 'completed',
      plan: 'Pro Plan',
      amount: 9.99,
      currency: 'USD',
      paymentMethod: 'PayPal',
      description: 'Pro Plan - Monthly'
    },
    {
      id: '3',
      orderNumber: 'ORD-2024-003',
      date: '2024-01-15',
      status: 'completed',
      plan: 'Pro Plan',
      amount: 9.99,
      currency: 'USD',
      paymentMethod: 'Credit Card',
      description: 'Pro Plan - Monthly'
    },
    {
      id: '4',
      orderNumber: 'ORD-2023-012',
      date: '2023-12-15',
      status: 'refunded',
      plan: 'Premium Plan',
      amount: 19.99,
      currency: 'USD',
      paymentMethod: 'Credit Card',
      description: 'Premium Plan - Monthly (Refunded)'
    }
  ]

  const getStatusIcon = (status: Order['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4" />
      case 'cancelled':
        return <XCircle className="h-4 w-4" />
      case 'refunded':
        return <RefreshCw className="h-4 w-4" />
      default:
        return <Package className="h-4 w-4" />
    }
  }

  const getStatusVariant = (status: Order['status']): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'pending':
      case 'processing':
        return 'secondary'
      case 'cancelled':
      case 'refunded':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  const filteredOrders = activeTab === 'all' 
    ? orders 
    : orders.filter(order => order.status === activeTab)

  const totalSpent = orders
    .filter(order => order.status === 'completed')
    .reduce((sum, order) => sum + order.amount, 0)

  return (
    <div className={cn(
      "flex-1 p-6",
      theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
    )}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">{t('settings.orders.title')}</h1>
          <p className={cn(
            "text-sm mt-1",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {t('settings.orders.description')}
          </p>
        </div>

        {/* Statistics Cards */}
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
                    {t('settings.orders.totalOrders')}
                  </p>
                  <p className="text-2xl font-bold mt-1">{orders.length}</p>
                </div>
                <ShoppingBag className="h-8 w-8 text-primary opacity-50" />
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
                    {t('settings.orders.totalSpent')}
                  </p>
                  <p className="text-2xl font-bold mt-1">${totalSpent.toFixed(2)}</p>
                </div>
                <DollarSign className="h-8 w-8 text-green-500 opacity-50" />
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
                    {t('settings.orders.currentPlan')}
                  </p>
                  <p className="text-2xl font-bold mt-1">Pro</p>
                </div>
                <Package className="h-8 w-8 text-blue-500 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Order History */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.orders.history')}</CardTitle>
            <CardDescription>{t('settings.orders.historyDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="all">{t('settings.orders.all')}</TabsTrigger>
                <TabsTrigger value="completed">{t('settings.orders.completed')}</TabsTrigger>
                <TabsTrigger value="pending">{t('settings.orders.pending')}</TabsTrigger>
                <TabsTrigger value="refunded">{t('settings.orders.refunded')}</TabsTrigger>
              </TabsList>

              <TabsContent value={activeTab} className="space-y-3">
                {filteredOrders.length === 0 ? (
                  <div className={cn(
                    "text-center py-8",
                    theme === 'dark' ? "text-gray-400" : "text-gray-500"
                  )}>
                    <ShoppingBag className="h-12 w-12 mx-auto mb-3 opacity-30" />
                    <p>{t('settings.orders.noOrders')}</p>
                  </div>
                ) : (
                  filteredOrders.map((order) => (
                    <div
                      key={order.id}
                      className={cn(
                        "flex items-center justify-between p-4 rounded-lg",
                        theme === 'dark' ? "bg-gray-800/50" : "bg-gray-50"
                      )}
                    >
                      <div className="flex items-start gap-4">
                        <div className={cn(
                          "p-2 rounded-lg",
                          theme === 'dark' ? "bg-gray-700" : "bg-white"
                        )}>
                          <Package className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{order.orderNumber}</p>
                            <Badge variant={getStatusVariant(order.status)}>
                              {getStatusIcon(order.status)}
                              <span className="ml-1">
                                {t(`settings.orders.status.${order.status}`)}
                              </span>
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {order.description}
                          </p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {order.date}
                            </span>
                            <span className="flex items-center gap-1">
                              <CreditCard className="h-3 w-3" />
                              {order.paymentMethod}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="font-semibold">
                            ${order.amount.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {order.currency}
                          </p>
                        </div>
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="ghost">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Payment Methods */}
        <Card className={cn(
          "border-border/40",
          theme === 'dark' ? "bg-card/50" : "bg-white"
        )}>
          <CardHeader>
            <CardTitle className="text-lg">{t('settings.orders.paymentMethods')}</CardTitle>
            <CardDescription>{t('settings.orders.paymentMethodsDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className={cn(
                "flex items-center justify-between p-3 rounded-lg",
                theme === 'dark' ? "bg-gray-800/50" : "bg-gray-50"
              )}>
                <div className="flex items-center gap-3">
                  <CreditCard className="h-5 w-5" />
                  <div>
                    <p className="font-medium">•••• •••• •••• 4242</p>
                    <p className="text-xs text-muted-foreground">Expires 12/24</p>
                  </div>
                </div>
                <Badge variant="secondary">{t('settings.orders.default')}</Badge>
              </div>
            </div>
            <Button variant="outline" className="mt-4" size="sm">
              {t('settings.orders.addPaymentMethod')}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsOrders