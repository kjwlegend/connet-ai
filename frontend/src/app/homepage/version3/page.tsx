'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useTranslations } from '@/lib/i18n/client'
import { useWaitlist } from '@/hooks/legacy/useWaitlist'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  ArrowRight, 
  CheckCircle,
  User,
  Bot,
  CircleDot,
  Globe,
  Users,
  MessageSquare,
  Network
} from 'lucide-react'
import { LanguageToggle } from '@/components/ui/LanguageToggle'

export default function HomepageV3() {
  const t = useTranslations()
  const [email, setEmail] = useState('')
  
  // Use the enhanced waitlist hook
  const {
    isLoading,
    isSubmitted,
    error,
    waitlistData,
    joinWaitlist,
    clearError
  } = useWaitlist()

  // Fixed positions for network dots to avoid hydration mismatch
  const networkDots = useMemo(() => [
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
  ], [])

  const handleJoinWaitlist = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    
    await joinWaitlist(email, 'homepage_v3')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="relative z-50 bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <CircleDot className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">connet.ai</span>
            </div>
            <div className="flex items-center space-x-8">
              <a href="#home" className="text-slate-300 hover:text-white transition-colors font-medium">
                {t('homepage.nav.home', 'Home')}
              </a>
              <a href="#features" className="text-slate-300 hover:text-white transition-colors font-medium">
                {t('homepage.nav.features', 'Features')}
              </a>
              <a href="#about" className="text-slate-300 hover:text-white transition-colors font-medium">
                {t('homepage.nav.about', 'About')}
              </a>
              <a href="#contact" className="text-slate-300 hover:text-white transition-colors font-medium">
                {t('homepage.nav.contact', 'Contact')}
              </a>
              <LanguageToggle className="text-slate-300 hover:text-white" variant="ghost" />
              <Button 
                variant="default" 
                className="bg-white text-slate-900 hover:bg-slate-100 font-semibold px-6"
                onClick={() => document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' })}
              >
                {t('homepage.nav.join', 'JOIN WAITLIST')}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with VR Theme */}
      <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
        {/* Background Network Animation */}
        <div className="absolute inset-0">
          {/* Connection lines */}
          <svg className="absolute inset-0 w-full h-full opacity-30">
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
                    duration: 3, 
                    repeat: Infinity, 
                    delay: i * 0.5 
                  }}
                />
              )
            })}
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
              </linearGradient>
            </defs>
          </svg>

          {/* Floating network dots */}
          {networkDots.map((dot, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-blue-400 rounded-full shadow-lg shadow-blue-400/50"
              style={{
                left: dot.left,
                top: dot.top,
              }}
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [0.8, 1.2, 0.8],
                boxShadow: [
                  '0 0 10px rgba(59, 130, 246, 0.3)',
                  '0 0 20px rgba(59, 130, 246, 0.8)',
                  '0 0 10px rgba(59, 130, 246, 0.3)'
                ]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: dot.delay,
              }}
            />
          ))}
        </div>

        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
          {/* Left - VR Headset Visualization */}
          <motion.div 
            className="relative"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="relative">
              {/* VR Headset Silhouette */}
              <div className="relative w-80 h-80 mx-auto">
                {/* Head silhouette */}
                <motion.div
                  className="absolute inset-x-12 bottom-0 h-40 bg-gradient-to-t from-slate-600 to-slate-700 rounded-t-full opacity-80"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 0.8 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                />
                
                {/* VR Headset */}
                <motion.div
                  className="absolute inset-x-8 top-20 h-32 bg-gradient-to-br from-slate-700 to-slate-800 rounded-2xl shadow-2xl border border-slate-600"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                >
                  {/* VR Lens */}
                  <div className="absolute inset-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl">
                    <div className="absolute inset-2 bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-lg">
                      {/* Glowing effect */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-lg"
                        animate={{
                          opacity: [0.2, 0.8, 0.2],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                        }}
                      />
                    </div>
                  </div>
                  
                  {/* Head strap */}
                  <div className="absolute -left-4 top-4 w-4 h-24 bg-slate-600 rounded-l-lg" />
                  <div className="absolute -right-4 top-4 w-4 h-24 bg-slate-600 rounded-r-lg" />
                </motion.div>

                {/* Floating UI elements around headset */}
                {[...Array(6)].map((_, i) => {
                  const angle = (i * 60) * (Math.PI / 180)
                  const radius = 160
                  const x = Math.cos(angle) * radius
                  const y = Math.sin(angle) * radius
                  
                  return (
                    <motion.div
                      key={i}
                      className="absolute w-8 h-8 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-full flex items-center justify-center"
                      style={{
                        left: `calc(50% + ${x}px - 16px)`,
                        top: `calc(50% + ${y}px - 16px)`
                      }}
                      animate={{ 
                        y: [0, -10, 0],
                        opacity: [0.5, 1, 0.5]
                      }}
                      transition={{ 
                        duration: 2 + i * 0.3, 
                        repeat: Infinity,
                        delay: i * 0.5
                      }}
                    >
                      {i % 3 === 0 ? <User className="w-4 h-4 text-blue-400" /> :
                       i % 3 === 1 ? <Bot className="w-4 h-4 text-purple-400" /> :
                       <Globe className="w-4 h-4 text-green-400" />}
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </motion.div>

          {/* Right - Content */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.h1 
              className="text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              Experience the{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                Future
              </span>{' '}
              of Connection
            </motion.h1>
            
            <motion.p 
              className="text-xl text-slate-300 mb-8 leading-relaxed max-w-lg"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
            >
              {t('homepage.hero.vr_description', 'Immerse yourself in next-generation AI networking.')}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.8 }}
            >
              <Button 
                size="lg"
                className="bg-white text-slate-900 hover:bg-slate-100 font-bold px-8 py-4 text-lg rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300"
                onClick={() => document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' })}
              >
                {t('homepage.hero.join_waitlist', 'JOIN WAITLIST')}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-slate-800/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">
              {t('homepage.features.title', 'Next-Generation AI Collaboration')}
            </h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              {t('homepage.features.description', 'Step into the future of human-AI interaction through immersive virtual experiences')}
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Users className="w-8 h-8" />,
                title: t('homepage.features.immersive.title', 'Immersive Networking'),
                description: t('homepage.features.immersive.description', 'Connect with AI agents in virtual reality environments')
              },
              {
                icon: <MessageSquare className="w-8 h-8" />,
                title: t('homepage.features.natural.title', 'Natural Interactions'),
                description: t('homepage.features.natural.description', 'Communicate naturally using voice, gesture, and presence')
              },
              {
                icon: <Network className="w-8 h-8" />,
                title: t('homepage.features.collaborative.title', 'Collaborative Spaces'),
                description: t('homepage.features.collaborative.description', 'Work together in shared virtual environments')
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="relative group"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="h-full p-8 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-blue-500/50 transition-colors duration-300 group-hover:bg-slate-700/50">
                  <div className="text-blue-400 mb-6 flex justify-center">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4 text-center">
                    {feature.title}
                  </h3>
                  <p className="text-slate-300 leading-relaxed text-center">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist Section */}
      <section id="waitlist" className="py-20 bg-gradient-to-r from-blue-900/20 to-purple-900/20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
              {t('homepage.waitlist.title', 'Ready to Step Into the Future?')}
            </h2>
            <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
              {t('homepage.waitlist.vr_description', 'Be among the first to experience the next evolution of AI collaboration in virtual reality.')}
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
                    placeholder={t('homepage.waitlist.email_placeholder', 'Enter your email address')}
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
                        {t('homepage.waitlist.join_button', 'JOIN WAITLIST')}
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
                  <h3 className="text-3xl font-bold text-white mb-4">
                    {t('homepage.waitlist.success_title', 'Welcome to the Future!')}
                  </h3>
                  <p className="text-slate-300 text-lg">
                    {t('homepage.waitlist.success_message', 'You\'re on the list! Get ready to connect the dots in virtual reality.')}
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-slate-900 border-t border-slate-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <CircleDot className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">connet.ai</span>
            </div>
            <p className="text-slate-400 text-sm text-center md:text-right">
              {t('homepage.footer.copyright_v3', '© 2024 connet.ai. Experience the future of connection.')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}