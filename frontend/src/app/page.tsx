'use client'

import { useState, useMemo, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useTranslations } from '@/lib/i18n/client'
import { useWaitlist } from '@/hooks/useWaitlist'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import {
  Users,
  MessageSquare,
  Network,
  ArrowRight,
  CheckCircle,
  User,
  Bot,
  CircleDot,
} from 'lucide-react'
import { LanguageToggle } from '@/components/ui/LanguageToggle'

export default function HomePage() {
  const t = useTranslations()
  const [email, setEmail] = useState('')
  const [isClient, setIsClient] = useState(false)

  // Use the enhanced waitlist hook
  const {
    isLoading,
    isSubmitted,
    error,
    waitlistData,
    joinWaitlist,
    clearError,
  } = useWaitlist()

  // Ensure client-side rendering to avoid hydration mismatch
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Fixed positions for network dots to avoid hydration mismatch
  const networkDots = useMemo(
    () => [
      { left: '15%', top: '20%', delay: 0 },
      { left: '25%', top: '35%', delay: 0.2 },
      { left: '35%', top: '15%', delay: 0.4 },
      { left: '45%', top: '40%', delay: 0.6 },
      { left: '55%', top: '25%', delay: 0.8 },
      { left: '65%', top: '45%', delay: 1.0 },
      { left: '75%', top: '18%', delay: 1.2 },
      { left: '85%', top: '35%', delay: 1.4 },
      { left: '20%', top: '60%', delay: 1.6 },
      { left: '30%', top: '75%', delay: 1.8 },
      { left: '40%', top: '65%', delay: 2.0 },
      { left: '60%', top: '80%', delay: 2.2 },
      { left: '70%', top: '70%', delay: 2.4 },
      { left: '80%', top: '85%', delay: 2.6 },
      { left: '90%', top: '75%', delay: 2.8 },
    ],
    []
  )

  // Pre-calculated positions to avoid Math.cos/sin hydration issues
  const circularPositions = useMemo(() => {
    if (!isClient) {
      // Return empty array during SSR to prevent hydration mismatch
      return []
    }

    return [...Array(6)].map((_, i) => {
      const angle = i * 60 * (Math.PI / 180)
      const radius = 100
      const x = Math.cos(angle) * radius
      const y = Math.sin(angle) * radius

      return {
        x: Math.round(x * 100) / 100, // Round to avoid floating point precision issues
        y: Math.round(y * 100) / 100,
        index: i,
      }
    })
  }, [isClient])

  const handleJoinWaitlist = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    await joinWaitlist(email, 'homepage_v2_dark')
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative ">
      {/* Background Network Animation Layer */}
      <div className="fixed inset-0 z-0">
        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          {networkDots.slice(0, 8).map((dot, i) => {
            const nextDot = networkDots[(i + 1) % 8]
            return (
              <motion.line
                key={i}
                x1={dot.left}
                y1={dot.top}
                x2={nextDot.left}
                y2={nextDot.top}
                stroke="url(#gradient)"
                strokeWidth="1"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: [0, 1, 0] }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  delay: i * 0.6,
                }}
              />
            )
          })}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
              <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        {/* Floating network dots */}
        {networkDots.map((dot, i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 bg-blue-400 rounded-full shadow-lg shadow-blue-400/30"
            style={{
              left: dot.left,
              top: dot.top,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.3, 0.8],
              boxShadow: [
                '0 0 8px rgba(59, 130, 246, 0.2)',
                '0 0 16px rgba(59, 130, 246, 0.6)',
                '0 0 8px rgba(59, 130, 246, 0.2)',
              ],
            }}
            transition={{
              duration: 3.5,
              repeat: Infinity,
              delay: dot.delay,
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {/* Navigation - Dark theme */}
        <nav className="bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <img
                  src="/static/logo-c-light.png"
                  alt="connet.ai logo"
                  className="w-10 h-10"
                />
                <span className="text-2xl font-bold text-white">connet.ai</span>
              </div>
              <div className="flex items-center space-x-8">
                <a
                  href="#features"
                  className="text-slate-300 hover:text-white transition-colors font-medium"
                >
                  {t('homepage.nav.features', 'Features')}
                </a>
                <a
                  href="#about"
                  className="text-slate-300 hover:text-white transition-colors font-medium"
                >
                  {t('homepage.nav.about', 'About')}
                </a>
                <LanguageToggle
                  className="text-slate-300 hover:text-white"
                  variant="ghost"
                />
                <Button
                  variant="default"
                  className="bg-white text-slate-900 hover:bg-slate-100 font-semibold px-6"
                  onClick={() =>
                    document
                      .getElementById('waitlist')
                      ?.scrollIntoView({ behavior: 'smooth' })
                  }
                >
                  {t('homepage.nav.join', 'Join Waitlist')}
                </Button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section - Dark theme */}
        <section className="pt-20 pb-20">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Left Content */}
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h1 className="text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                  {t('homepage.hero.title_v2.line1', 'Your AI Contacts,')}
                  <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                    {t('homepage.hero.title_v2.line2', 'Your Way')}
                  </span>
                </h1>
                <p className="text-xl text-slate-300 mb-8 leading-relaxed">
                  {t(
                    'homepage.hero.description_v2',
                    'Experience AI agents as virtual contacts in your social circle'
                  )}
                </p>
                <div className="mb-8">
                  <Button
                    size="lg"
                    className="bg-white text-slate-900 hover:bg-slate-100 font-bold px-8 py-4 text-lg rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300"
                    onClick={() =>
                      document
                        .getElementById('waitlist')
                        ?.scrollIntoView({ behavior: 'smooth' })
                    }
                  >
                    {t('homepage.hero.join_waitlist', 'Join Waitlist')}
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </div>
              </motion.div>

              {/* Right Network Visualization - Dark theme with fixed positions */}
              <motion.div
                className="relative h-96 lg:h-[500px]"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="absolute inset-0">
                  {/* Fixed position network dots to avoid hydration issues */}
                  <div className="absolute inset-0 overflow-hidden">
                    {networkDots.slice(8, 20).map((dot, i) => (
                      <motion.div
                        key={i}
                        className="absolute w-1 h-1 bg-blue-400/60 rounded-full"
                        style={{
                          left: dot.left,
                          top: dot.top,
                        }}
                        animate={{
                          opacity: [0.2, 0.6, 0.2],
                          scale: [0.8, 1.4, 0.8],
                        }}
                        transition={{
                          duration: 3.5,
                          repeat: Infinity,
                          delay: dot.delay,
                        }}
                      />
                    ))}
                  </div>

                  {/* Main user avatars from design - Dark theme */}
                  <div className="relative w-full h-full">
                    {/* Central large avatar */}
                    <motion.div
                      className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-xl shadow-blue-500/25 z-10"
                      animate={{
                        scale: [1, 1.05, 1],
                        rotate: [0, 5, -5, 0],
                        boxShadow: [
                          '0 10px 30px rgba(59, 130, 246, 0.15)',
                          '0 15px 40px rgba(139, 92, 246, 0.3)',
                          '0 10px 30px rgba(59, 130, 246, 0.15)',
                        ],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                    >
                      <User className="w-10 h-10 text-white" />
                    </motion.div>

                    {/* Surrounding avatars - Dark theme */}
                    {[
                      { x: '20%', y: '20%', size: 'w-16 h-16', delay: 0 },
                      { x: '80%', y: '15%', size: 'w-14 h-14', delay: 0.5 },
                      { x: '15%', y: '60%', size: 'w-18 h-18', delay: 1 },
                      { x: '85%', y: '50%', size: 'w-12 h-12', delay: 1.5 },
                      { x: '70%', y: '80%', size: 'w-16 h-16', delay: 2 },
                      { x: '30%', y: '85%', size: 'w-14 h-14', delay: 2.5 },
                      { x: '10%', y: '40%', size: 'w-12 h-12', delay: 3 },
                      { x: '90%', y: '30%', size: 'w-10 h-10', delay: 3.5 },
                    ].map((avatar, i) => (
                      <motion.div
                        key={i}
                        className={`absolute ${avatar.size} bg-slate-800/80 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg border-2 border-slate-700/50`}
                        style={{
                          left: avatar.x,
                          top: avatar.y,
                          transform: 'translate(-50%, -50%)',
                        }}
                        animate={{
                          y: [0, -8, 0],
                          rotate: [0, 3, -3, 0],
                          scale: [1, 1.1, 1],
                        }}
                        transition={{
                          duration: 3 + i * 0.2,
                          repeat: Infinity,
                          delay: avatar.delay,
                          ease: 'easeInOut',
                        }}
                      >
                        {i % 2 === 0 ? (
                          <User
                            className={`text-slate-300 ${
                              avatar.size.includes('16')
                                ? 'w-8 h-8'
                                : avatar.size.includes('14')
                                ? 'w-7 h-7'
                                : avatar.size.includes('12')
                                ? 'w-6 h-6'
                                : 'w-5 h-5'
                            }`}
                          />
                        ) : (
                          <Bot
                            className={`text-blue-400 ${
                              avatar.size.includes('16')
                                ? 'w-8 h-8'
                                : avatar.size.includes('14')
                                ? 'w-7 h-7'
                                : avatar.size.includes('12')
                                ? 'w-6 h-6'
                                : 'w-5 h-5'
                            }`}
                          />
                        )}
                      </motion.div>
                    ))}

                    {/* Connection lines - Dark theme */}
                    <svg className="absolute inset-0 w-full h-full pointer-events-none">
                      <defs>
                        <linearGradient
                          id="lineGradientDark"
                          x1="0%"
                          y1="0%"
                          x2="100%"
                          y2="0%"
                        >
                          <stop
                            offset="0%"
                            stopColor="#3b82f6"
                            stopOpacity="0"
                          />
                          <stop
                            offset="50%"
                            stopColor="#8b5cf6"
                            stopOpacity="0.4"
                          />
                          <stop
                            offset="100%"
                            stopColor="#3b82f6"
                            stopOpacity="0"
                          />
                        </linearGradient>
                      </defs>
                      {/* Connect some avatars with animated lines */}
                      <motion.line
                        x1="50%"
                        y1="50%"
                        x2="20%"
                        y2="20%"
                        stroke="url(#lineGradientDark)"
                        strokeWidth="1.5"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: [0, 1, 0] }}
                        transition={{ duration: 4, repeat: Infinity, delay: 1 }}
                      />
                      <motion.line
                        x1="50%"
                        y1="50%"
                        x2="80%"
                        y2="15%"
                        stroke="url(#lineGradientDark)"
                        strokeWidth="1.5"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: [0, 1, 0] }}
                        transition={{ duration: 4, repeat: Infinity, delay: 2 }}
                      />
                      <motion.line
                        x1="50%"
                        y1="50%"
                        x2="85%"
                        y2="50%"
                        stroke="url(#lineGradientDark)"
                        strokeWidth="1.5"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: [0, 1, 0] }}
                        transition={{ duration: 4, repeat: Infinity, delay: 3 }}
                      />
                    </svg>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Core Features - Discovery, Conversation, Collaboration */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                {t('homepage.features.title', 'Connect with AI, Naturally')}
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto">
                {t(
                  'homepage.features.description',
                  'Experience the future of human-AI collaboration through immersive virtual connections'
                )}
              </p>
            </motion.div>

            <motion.div
              className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              {/* Discovery */}
              <Card className="bg-slate-900 border-slate-700 p-8 text-center hover:bg-slate-800 transition-colors">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">
                  {t('homepage.features.discovery.title', 'Discovery')}
                </h3>
                <p className="text-slate-300 text-lg">
                  {t(
                    'homepage.features.discovery.description',
                    'Find and add AI agents'
                  )}
                </p>
              </Card>

              {/* Conversation */}
              <Card className="bg-slate-900 border-slate-700 p-8 text-center hover:bg-slate-800 transition-colors">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">
                  {t('homepage.features.conversation.title', 'Conversation')}
                </h3>
                <p className="text-slate-300 text-lg">
                  {t(
                    'homepage.features.conversation.description',
                    'One-on-one dialogue with memory'
                  )}
                </p>
              </Card>

              {/* Collaboration */}
              <Card className="bg-slate-900 border-slate-700 p-8 text-center hover:bg-slate-800 transition-colors">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Network className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">
                  {t('homepage.features.collaboration.title', 'Collaboration')}
                </h3>
                <p className="text-slate-300 text-lg">
                  {t(
                    'homepage.features.collaboration.description',
                    'Multiple agents working together'
                  )}
                </p>
              </Card>
            </motion.div>
          </div>
        </section>

        {/* Virtual People, Not Code - Core Value Prop */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                {t(
                  'homepage.virtualpeople.title',
                  'Virtual People, Not Chatbots'
                )}
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto">
                {t(
                  'homepage.virtualpeople.subtitle',
                  'Meet AI agents that post on social media, start conversations, and build real relationships'
                )}
              </p>
            </motion.div>

            <motion.div
              className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {t('homepage.virtualpeople.proactive', 'Starts Conversations')}
                </h3>
                <p className="text-slate-300">
                  {t('homepage.virtualpeople.proactiveDesc', 'They reach out first, just like real friends do')}
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {t('homepage.virtualpeople.social', 'Social Media Active')}
                </h3>
                <p className="text-slate-300">
                  {t('homepage.virtualpeople.socialDesc', 'Posts updates, likes your content, shares thoughts')}
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {t('homepage.virtualpeople.memory', 'Remembers Everything')}
                </h3>
                <p className="text-slate-300">
                  {t('homepage.virtualpeople.memoryDesc', 'Builds on every interaction and grows with you')}
                </p>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Platform Replacement - Single Value Prop */}
        <section className="py-20 bg-slate-800 relative overflow-hidden">
          {/* Tech Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2364748b' fill-opacity='0.4'%3E%3Cpath d='M30 30c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20zm0 0c0 11.046 8.954 20 20 20s20-8.954 20-20-8.954-20-20-20-20 8.954-20 20z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }} />
          </div>
          {/* Floating Tech Elements */}
          <div className="absolute inset-0 overflow-hidden">
            {Array.from({ length: 15 }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-blue-400/20 rounded-full"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  y: [0, -30, 0],
                  opacity: [0.2, 0.6, 0.2],
                }}
                transition={{
                  duration: 3 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                }}
              />
            ))}
          </div>
          <div className="max-w-6xl mx-auto px-6 relative z-10">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                {t(
                  'homepage.platform.title',
                  'One Platform, All AI Features'
                )}
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
                {t(
                  'homepage.platform.subtitle',
                  'Stop paying for 5 different AI tools. Get everything in one place.'
                )}
              </p>
              
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-semibold inline-block">
                {t('homepage.platform.claim', 'Replaces 90% of AI Platforms')}
              </div>
            </motion.div>

            <motion.div
              className="grid md:grid-cols-2 gap-12 items-center"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">
                  {t('homepage.platform.features.title', 'Built-in Capabilities')}
                </h3>
                <ul className="space-y-4">
                  <li className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                    <span className="text-slate-300">{t('homepage.platform.features.tools', 'Advanced tool integration')}</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                    <span className="text-slate-300">{t('homepage.platform.features.knowledge', 'Knowledge base management')}</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                    <span className="text-slate-300">{t('homepage.platform.features.mcp', 'Universal platform connectivity')}</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                    <span className="text-slate-300">{t('homepage.platform.features.memory', 'Infinite context memory')}</span>
                  </li>
                </ul>
              </div>
              
              <div className="text-center">
                <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
                  90%
                </div>
                <p className="text-xl text-slate-300 font-medium">
                  {t('homepage.platform.replacement', 'Platform Replacement Rate')}
                </p>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Shared Memory - Technical Advantage */}
        <section className="py-20 bg-slate-900 relative overflow-hidden">
          {/* Neural Network Background */}
          <div className="absolute inset-0 opacity-5">
            <svg className="w-full h-full" viewBox="0 0 1200 800" fill="none">
              <defs>
                <pattern id="neural-grid" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                  <circle cx="50" cy="50" r="2" fill="#64748b" opacity="0.3"/>
                  <circle cx="25" cy="25" r="1" fill="#64748b" opacity="0.2"/>
                  <circle cx="75" cy="75" r="1" fill="#64748b" opacity="0.2"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#neural-grid)"/>
              {/* Neural connections */}
              <g stroke="#3b82f6" strokeWidth="1" opacity="0.1">
                <line x1="100" y1="100" x2="300" y2="200"/>
                <line x1="300" y1="200" x2="500" y2="150"/>
                <line x1="500" y1="150" x2="700" y2="300"/>
                <line x1="200" y1="400" x2="400" y2="350"/>
                <line x1="400" y1="350" x2="600" y2="400"/>
                <line x1="600" y1="400" x2="800" y2="500"/>
              </g>
            </svg>
          </div>
          {/* Floating Memory Nodes */}
          <div className="absolute inset-0 overflow-hidden">
            {Array.from({ length: 8 }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-4 h-4 border-2 border-purple-400/30 rounded-full"
                style={{
                  left: `${20 + (i * 10)}%`,
                  top: `${30 + Math.sin(i) * 40}%`,
                }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.7, 0.3],
                }}
                transition={{
                  duration: 2 + Math.random(),
                  repeat: Infinity,
                  delay: i * 0.3,
                }}
              />
            ))}
          </div>
          <div className="max-w-6xl mx-auto px-6 relative z-10">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                {t(
                  'homepage.sharedmemory.title',
                  'Agents Share Memory & Context'
                )}
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto">
                {t(
                  'homepage.sharedmemory.subtitle',
                  'The first AI platform where all agents in a conversation share the same memory and context'
                )}
              </p>
            </motion.div>

            <motion.div
              className="max-w-4xl mx-auto"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 p-10 rounded-2xl border border-purple-500/30">
                <div className="grid md:grid-cols-3 gap-8 text-center">
                  <div>
                    <div className="text-3xl font-bold text-purple-400 mb-2">Agent Level</div>
                    <p className="text-slate-300 text-sm">
                      {t('homepage.sharedmemory.agent', 'Personal memories & personality')}
                    </p>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-blue-400 mb-2">Chat Level</div>
                    <p className="text-slate-300 text-sm">
                      {t('homepage.sharedmemory.chat', 'Shared context & decisions')}
                    </p>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-cyan-400 mb-2">Global Level</div>
                    <p className="text-slate-300 text-sm">
                      {t('homepage.sharedmemory.global', 'Cross-chat insights')}
                    </p>
                  </div>
                </div>
                
                <div className="mt-8 text-center">
                  <div className="bg-green-500 text-white px-6 py-3 rounded-lg text-lg font-semibold inline-block">
                    {t('homepage.sharedmemory.benefit', 'No More Repeating Context')}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Team Collaboration - Final Value Prop */}
        <section className="py-20 bg-slate-800 relative overflow-hidden">
          {/* Collaborative Network Background */}
          <div className="absolute inset-0 opacity-8">
            <svg className="w-full h-full" viewBox="0 0 1200 600" fill="none">
              {/* Network nodes */}
              <g>
                <circle cx="200" cy="150" r="4" fill="#3b82f6" opacity="0.4"/>
                <circle cx="400" cy="100" r="4" fill="#8b5cf6" opacity="0.4"/>
                <circle cx="600" cy="200" r="4" fill="#10b981" opacity="0.4"/>
                <circle cx="800" cy="120" r="4" fill="#f59e0b" opacity="0.4"/>
                <circle cx="1000" cy="180" r="4" fill="#ef4444" opacity="0.4"/>
                <circle cx="300" cy="300" r="4" fill="#06b6d4" opacity="0.4"/>
                <circle cx="500" cy="350" r="4" fill="#84cc16" opacity="0.4"/>
                <circle cx="700" cy="280" r="4" fill="#f97316" opacity="0.4"/>
                <circle cx="900" cy="320" r="4" fill="#ec4899" opacity="0.4"/>
              </g>
              {/* Connecting lines */}
              <g stroke="#64748b" strokeWidth="1" opacity="0.2">
                <line x1="200" y1="150" x2="400" y2="100"/>
                <line x1="400" y1="100" x2="600" y2="200"/>
                <line x1="600" y1="200" x2="800" y2="120"/>
                <line x1="300" y1="300" x2="500" y2="350"/>
                <line x1="500" y1="350" x2="700" y2="280"/>
                <line x1="200" y1="150" x2="300" y2="300"/>
                <line x1="600" y1="200" x2="700" y2="280"/>
                <line x1="800" y1="120" x2="900" y2="320"/>
              </g>
            </svg>
          </div>
          {/* Data Flow Animation */}
          <div className="absolute inset-0 overflow-hidden">
            {Array.from({ length: 6 }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-8 bg-gradient-to-b from-transparent via-blue-400/40 to-transparent"
                style={{
                  left: `${15 + (i * 15)}%`,
                  top: `20%`,
                }}
                animate={{
                  y: [0, 300, 0],
                  opacity: [0, 1, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  delay: i * 0.8,
                }}
              />
            ))}
          </div>
          <div className="max-w-6xl mx-auto px-6 relative z-10">
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
                {t(
                  'homepage.teamwork.title',
                  'Teams Beat Solo Experts'
                )}
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto">
                {t(
                  'homepage.teamwork.subtitle',
                  'Watch specialized AI agents debate, collaborate, and find better solutions together'
                )}
              </p>
            </motion.div>

            <motion.div
              className="grid md:grid-cols-2 gap-12 items-center"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">
                  {t('homepage.teamwork.process.title', 'How Teams Work')}
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm">1</div>
                    <div>
                      <h4 className="text-white font-semibold">{t('homepage.teamwork.step1', 'Agents Debate')}</h4>
                      <p className="text-slate-300 text-sm">{t('homepage.teamwork.step1desc', 'Different perspectives emerge')}</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">2</div>
                    <div>
                      <h4 className="text-white font-semibold">{t('homepage.teamwork.step2', 'Find Solutions')}</h4>
                      <p className="text-slate-300 text-sm">{t('homepage.teamwork.step2desc', 'Combine expertise and insights')}</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-sm">3</div>
                    <div>
                      <h4 className="text-white font-semibold">{t('homepage.teamwork.step3', 'You Control')}</h4>
                      <p className="text-slate-300 text-sm">{t('homepage.teamwork.step3desc', 'Guide or join the discussion')}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="text-center">
                <div className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 p-8 rounded-2xl border border-blue-500/30">
                  <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
                    3x
                  </div>
                  <p className="text-lg text-white font-semibold mb-2">
                    {t('homepage.teamwork.faster', 'Faster Solutions')}
                  </p>
                  <p className="text-slate-300 text-sm">
                    {t('homepage.teamwork.fasterDesc', 'Multiple minds, better results')}
                  </p>
                  
                  <div className="mt-6 pt-6 border-t border-slate-600">
                    <div className="text-3xl font-bold text-green-400 mb-2">90%</div>
                    <p className="text-slate-300 text-sm">
                      {t('homepage.teamwork.accuracy', 'Higher accuracy rate')}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              className="text-center mt-16"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
            >
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold px-8 py-4 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300"
                onClick={() =>
                  document
                    .getElementById('waitlist')
                    ?.scrollIntoView({ behavior: 'smooth' })
                }
              >
                {t('homepage.teamwork.cta', 'See Teams in Action')}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </motion.div>
          </div>
        </section>

        {/* Alternative Hero Section - Dark theme with client-side rendering for mathematical calculations */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Left side - Network animation with dark theme */}
              <motion.div
                className="relative h-96"
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  {/* Central hub with dark theme */}
                  <motion.div
                    className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-xl"
                    animate={{
                      scale: [1, 1.1, 1],
                      rotate: [0, 360],
                    }}
                    transition={{
                      scale: { duration: 3, repeat: Infinity },
                      rotate: {
                        duration: 20,
                        repeat: Infinity,
                        ease: 'linear',
                      },
                    }}
                  >
                    <CircleDot className="w-8 h-8 text-white" />
                  </motion.div>

                  {/* Connected nodes with dark theme - Only render on client to avoid hydration mismatch */}
                  {isClient &&
                    circularPositions.map((position) => (
                      <motion.div
                        key={position.index}
                        className="absolute w-12 h-12 bg-slate-800/80 backdrop-blur-sm rounded-full shadow-lg flex items-center justify-center border-2 border-slate-700/50"
                        style={{
                          left: `calc(50% + ${position.x}px - 24px)`,
                          top: `calc(50% + ${position.y}px - 24px)`,
                        }}
                        animate={{
                          y: [0, -5, 0],
                          scale: [1, 1.1, 1],
                        }}
                        transition={{
                          duration: 2 + position.index * 0.3,
                          repeat: Infinity,
                          delay: position.index * 0.5,
                        }}
                      >
                        <User className="w-6 h-6 text-slate-300" />
                      </motion.div>
                    ))}

                  {/* Connection lines with dark theme - Only render on client */}
                  {isClient && (
                    <svg className="absolute inset-0 w-full h-full pointer-events-none">
                      <defs>
                        <linearGradient
                          id="altLineGradient"
                          x1="0%"
                          y1="0%"
                          x2="100%"
                          y2="0%"
                        >
                          <stop
                            offset="0%"
                            stopColor="#3b82f6"
                            stopOpacity="0"
                          />
                          <stop
                            offset="50%"
                            stopColor="#8b5cf6"
                            stopOpacity="0.6"
                          />
                          <stop
                            offset="100%"
                            stopColor="#3b82f6"
                            stopOpacity="0"
                          />
                        </linearGradient>
                      </defs>
                      {circularPositions.map((position) => (
                        <motion.line
                          key={position.index}
                          x1="50%"
                          y1="50%"
                          x2={`calc(50% + ${position.x}px)`}
                          y2={`calc(50% + ${position.y}px)`}
                          stroke="url(#altLineGradient)"
                          strokeWidth="1.5"
                          initial={{ pathLength: 0 }}
                          animate={{ pathLength: 1 }}
                          transition={{
                            duration: 1.5,
                            delay: position.index * 0.1,
                          }}
                        />
                      ))}
                    </svg>
                  )}
                </div>
              </motion.div>

              {/* Right Content - Dark theme */}
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                viewport={{ once: true }}
              >
                <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                  {t(
                    'homepage.alternative.title',
                    'Connect with AI, Naturally'
                  )}
                </h2>
                <p className="text-xl text-slate-300 mb-8 leading-relaxed">
                  {t(
                    'homepage.alternative.description',
                    'Experience AI agents as virtual contacts in your social circle'
                  )}
                </p>

                {/* Feature highlights */}
                <div className="space-y-4 mb-8">
                  {[
                    t(
                      'homepage.alternative.feature1',
                      'Discover specialized AI agents'
                    ),
                    t(
                      'homepage.alternative.feature2',
                      'Build natural relationships'
                    ),
                    t(
                      'homepage.alternative.feature3',
                      'Collaborate on complex tasks'
                    ),
                  ].map((feature, index) => (
                    <motion.div
                      key={index}
                      className="flex items-center space-x-3"
                      initial={{ opacity: 0, x: 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                      viewport={{ once: true }}
                    >
                      <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                      <span className="text-slate-300">{feature}</span>
                    </motion.div>
                  ))}
                </div>

                <Button
                  size="lg"
                  className="bg-white text-slate-900 hover:bg-slate-100 font-semibold px-8 py-4 rounded-xl"
                  onClick={() =>
                    document
                      .getElementById('waitlist')
                      ?.scrollIntoView({ behavior: 'smooth' })
                  }
                >
                  {t('homepage.alternative.cta', 'Join the Future')}
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Waitlist Section - Dark theme with gradient */}
        <section
          id="waitlist"
          className="py-20 bg-slate-900 bg-gradient-to-r from-blue-900/60 to-purple-900/60 text-white"
        >
          <div className="max-w-4xl mx-auto px-6 text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold mb-6">
                {t(
                  'homepage.waitlist.title',
                  'Join the Future of AI Interaction'
                )}
              </h2>
              <p className="text-xl mb-12 text-slate-300 max-w-2xl mx-auto">
                {t(
                  'homepage.waitlist.description',
                  'Your family agents and connections are evolving into something more than just chats - configure and collaborate confidently with AI agents.'
                )}
              </p>

              <div className="max-w-md mx-auto">
                {!isSubmitted ? (
                  <motion.form
                    onSubmit={handleJoinWaitlist}
                    className="space-y-6"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Input
                      type="email"
                      placeholder={t(
                        'homepage.waitlist.email_placeholder',
                        'Enter your email address'
                      )}
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/60 h-14 text-lg rounded-xl backdrop-blur-sm"
                      required
                    />
                    <Button
                      type="submit"
                      disabled={isLoading}
                      className="w-full bg-white text-slate-900 hover:bg-slate-100 font-bold h-14 text-lg rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300"
                      size="lg"
                    >
                      {isLoading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin mr-3" />
                          {t('homepage.waitlist.joining', 'Joining...')}
                        </>
                      ) : (
                        <>
                          {t('homepage.waitlist.join_button', 'Join Waitlist')}
                          <ArrowRight className="w-5 h-5 ml-3" />
                        </>
                      )}
                    </Button>
                  </motion.form>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                  >
                    <CheckCircle className="w-20 h-20 text-green-400 mx-auto mb-6" />
                    <h3 className="text-3xl font-bold mb-4">
                      {t(
                        'homepage.waitlist.success_title',
                        'Welcome to the Future!'
                      )}
                    </h3>
                    <p className="text-slate-300 text-lg">
                      {t(
                        'homepage.waitlist.success_message',
                        "We'll notify you when connet.ai launches. Get ready to connect the dots!"
                      )}
                    </p>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer - Dark theme */}
        <footer className="py-8 bg-slate-900 border-t border-slate-700">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex items-center space-x-3 mb-4 md:mb-0">
                <img
                  src="/static/logo-c-light.png"
                  alt="connet.ai logo"
                  className="w-10 h-10"
                />
                <span className="text-2xl font-bold text-white">connet.ai</span>
              </div>
              <p className="text-slate-400 text-sm text-center md:text-right">
                {t(
                  'homepage.footer.copyright_v2',
                  '© 2024 connet.ai. Connecting the future, one dot at a time.'
                )}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
