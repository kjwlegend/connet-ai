'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useTranslations } from '@/lib/i18n/client'
import { useWaitlist } from '@/hooks/useWaitlist'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { 
  Brain, 
  Users, 
  MessageCircle, 
  Zap, 
  Network, 
  Sparkles, 
  ArrowRight, 
  CheckCircle, 
  Globe,
  Bot,
  Circle
} from 'lucide-react'

export default function HomepageV1() {
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

  const handleJoinWaitlist = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    
    await joinWaitlist(email, 'homepage_v1')
  }

  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  }

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-lg bg-white/80 dark:bg-slate-900/80 border-b border-slate-200/50 dark:border-slate-700/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Circle className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900 dark:text-white">connet.ai</span>
            </div>
            <div className="flex items-center space-x-6">
              <a href="#features" className="text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-colors">
                {t('homepage.nav.features', 'Features')}
              </a>
              <a href="#how-it-works" className="text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-colors">
                {t('homepage.nav.how', 'How It Works')}
              </a>
              <Button variant="default" size="sm" onClick={() => document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' })}>
                {t('homepage.nav.join', 'Join Waitlist')}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-20">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center max-w-4xl mx-auto"
            initial="initial"
            animate="animate"
            variants={staggerChildren}
          >
            <motion.div variants={fadeInUp} className="mb-8">
              <Badge variant="secondary" className="mb-4 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                <Sparkles className="w-4 h-4 mr-2" />
                {t('homepage.hero.badge', 'The Future of AI Collaboration')}
              </Badge>
              <h1 className="text-5xl md:text-7xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">
                {t('homepage.hero.title.line1', 'Connect')} <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">{t('homepage.hero.title.line2', 'Dots')}</span>
                <br />
                {t('homepage.hero.title.line3', 'in Virtual Reality')}
              </h1>
              <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                {t('homepage.hero.description', 'Experience AI agents as virtual contacts in your social circle. Build, collaborate, and innovate in a seamless human-AI ecosystem.')}
              </p>
            </motion.div>

            <motion.div variants={fadeInUp} className="mb-12">
              <form onSubmit={handleJoinWaitlist} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                <Input
                  type="email"
                  placeholder={t('homepage.hero.email_placeholder', 'Enter your email')}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1"
                  required
                />
                <Button type="submit" disabled={isLoading || isSubmitted}>
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  ) : isSubmitted ? (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  ) : (
                    <ArrowRight className="w-4 h-4 mr-2" />
                  )}
                  {isSubmitted 
                    ? t('homepage.hero.joined', 'Joined!') 
                    : t('homepage.hero.join_waitlist', 'Join Waitlist')
                  }
                </Button>
              </form>
              {isSubmitted && (
                <motion.p 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-green-600 dark:text-green-400 mt-4"
                >
                  {t('homepage.hero.success_message', 'Thank you! We\'ll notify you when we launch.')}
                </motion.p>
              )}
            </motion.div>

            {/* Floating Network Animation */}
            <motion.div 
              variants={fadeInUp}
              className="relative h-64 mb-20"
            >
              <div className="absolute inset-0 flex items-center justify-center">
                {/* Central Hub */}
                <motion.div
                  className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg"
                  animate={{ 
                    scale: [1, 1.1, 1],
                    rotate: [0, 360]
                  }}
                  transition={{ 
                    scale: { duration: 3, repeat: Infinity },
                    rotate: { duration: 20, repeat: Infinity, ease: "linear" }
                  }}
                >
                  <Network className="w-8 h-8 text-white" />
                </motion.div>

                {/* Floating Nodes */}
                {[...Array(8)].map((_, i) => {
                  const angle = (i * 45) * (Math.PI / 180)
                  const radius = 120
                  const x = Math.cos(angle) * radius
                  const y = Math.sin(angle) * radius
                  
                  return (
                    <motion.div
                      key={i}
                      className="absolute w-12 h-12 bg-white dark:bg-slate-800 rounded-full shadow-lg flex items-center justify-center border-2 border-slate-200 dark:border-slate-600"
                      style={{
                        left: `calc(50% + ${x}px - 24px)`,
                        top: `calc(50% + ${y}px - 24px)`
                      }}
                      animate={{ 
                        y: [0, -10, 0],
                        rotate: [0, 5, -5, 0]
                      }}
                      transition={{ 
                        duration: 3 + i * 0.2, 
                        repeat: Infinity,
                        delay: i * 0.3
                      }}
                    >
                      {i % 3 === 0 ? <Users className="w-6 h-6 text-blue-500" /> :
                       i % 3 === 1 ? <Bot className="w-6 h-6 text-purple-500" /> :
                       <Brain className="w-6 h-6 text-green-500" />}
                    </motion.div>
                  )
                })}

                {/* Connection Lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {[...Array(8)].map((_, i) => {
                    const angle = (i * 45) * (Math.PI / 180)
                    const radius = 120
                    const x = Math.cos(angle) * radius
                    const y = Math.sin(angle) * radius
                    
                    return (
                      <motion.line
                        key={i}
                        x1="50%"
                        y1="50%"
                        x2={`calc(50% + ${x}px)`}
                        y2={`calc(50% + ${y}px)`}
                        stroke="currentColor"
                        strokeWidth="1"
                        className="text-slate-300 dark:text-slate-600"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: 2, delay: i * 0.1 }}
                      />
                    )
                  })}
                </svg>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              {t('homepage.features.title', 'Virtual Reality Meets AI')}
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              {t('homepage.features.description', 'Experience the future of human-AI collaboration through immersive virtual connections')}
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Users className="w-8 h-8" />,
                title: t('homepage.features.social.title', 'Social AI Network'),
                description: t('homepage.features.social.description', 'AI agents become part of your social circle, with personalities, skills, and memories')
              },
              {
                icon: <MessageCircle className="w-8 h-8" />,
                title: t('homepage.features.natural.title', 'Natural Conversations'),
                description: t('homepage.features.natural.description', '@mention AI agents naturally in conversations, just like chatting with friends')
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: t('homepage.features.collaborative.title', 'Collaborative Intelligence'),
                description: t('homepage.features.collaborative.description', 'Multiple AI agents work together on complex tasks, sharing context and knowledge')
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="p-8 h-full text-center hover:shadow-lg transition-shadow bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-slate-200/50 dark:border-slate-700/50">
                  <div className="text-blue-600 dark:text-blue-400 mb-4 flex justify-center">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              {t('homepage.how.title', 'Connect Dots, Create Magic')}
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              {t('homepage.how.description', 'Three simple steps to enter the future of AI collaboration')}
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            {[
              {
                step: '01',
                title: t('homepage.how.step1.title', 'Discover AI Agents'),
                description: t('homepage.how.step1.description', 'Browse and connect with specialized AI agents tailored to your needs')
              },
              {
                step: '02', 
                title: t('homepage.how.step2.title', 'Build Your Network'),
                description: t('homepage.how.step2.description', 'Add AI agents to your virtual contact list and start natural conversations')
              },
              {
                step: '03',
                title: t('homepage.how.step3.title', 'Collaborate & Create'),
                description: t('homepage.how.step3.description', 'Work together with AI agents on projects, tasks, and creative endeavors')
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                className="flex flex-col md:flex-row items-center gap-8 mb-12 last:mb-0"
                initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
              >
                <div className={`flex-1 ${index % 2 === 1 ? 'md:order-2' : ''}`}>
                  <div className="text-4xl font-bold text-blue-600/20 dark:text-blue-400/20 mb-2">
                    {item.step}
                  </div>
                  <h3 className="text-2xl font-semibold text-slate-900 dark:text-white mb-3">
                    {item.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {item.description}
                  </p>
                </div>
                <div className={`w-64 h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-2xl flex items-center justify-center ${index % 2 === 1 ? 'md:order-1' : ''}`}>
                  <div className="text-6xl text-blue-600/30 dark:text-blue-400/30">
                    {index === 0 ? <Globe /> : index === 1 ? <Users /> : <Sparkles />}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="waitlist" className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold mb-4">
              {t('homepage.cta.title', 'Ready to Connect the Dots?')}
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
              {t('homepage.cta.description', 'Join thousands of early adopters shaping the future of AI collaboration')}
            </p>
            <form onSubmit={handleJoinWaitlist} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <Input
                type="email"
                placeholder={t('homepage.cta.email_placeholder', 'Your email address')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/60"
                required
              />
              <Button type="submit" variant="secondary" disabled={isLoading || isSubmitted}>
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin mr-2" />
                ) : isSubmitted ? (
                  <CheckCircle className="w-4 h-4 mr-2" />
                ) : (
                  <ArrowRight className="w-4 h-4 mr-2" />
                )}
                {isSubmitted 
                  ? t('homepage.cta.joined', 'Welcome!') 
                  : t('homepage.cta.join_waitlist', 'Get Early Access')
                }
              </Button>
            </form>
            {isSubmitted && (
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-white/80 mt-4"
              >
                {t('homepage.cta.success_message', 'You\'re on the list! We\'ll be in touch soon.')}
              </motion.p>
            )}
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-white">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Circle className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">connet.ai</span>
            </div>
            <p className="text-slate-400 text-center md:text-right">
              {t('homepage.footer.copyright', '© 2024 connet.ai. Connecting the future, one dot at a time.')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}