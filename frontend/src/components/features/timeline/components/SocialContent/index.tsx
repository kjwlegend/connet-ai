'use client'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Heart,
  MessageCircle,
  Share,
  Plus,
  ImageIcon,
  Smile,
  MoreHorizontal,
  Send,
  Bot,
  Trash2,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useTheme } from 'next-themes'
import { useTranslations } from '@/lib/i18n/client'
import { mockSocialData, type SocialPost } from '../../data/mockSocialData'

interface SocialContentProps {
  category: string
}

export function SocialContent({ category }: SocialContentProps) {
  const { theme } = useTheme()
  const t = useTranslations()
  const [newPost, setNewPost] = useState('')
  const [showComposer, setShowComposer] = useState(false)
  const [postsData, setPostsData] = useState(mockSocialData)
  const [expandedComments, setExpandedComments] = useState<
    Record<string, boolean>
  >({})
  const [newComments, setNewComments] = useState<Record<string, string>>({})
  const [deletedPosts, setDeletedPosts] = useState<Set<string>>(new Set())

  const posts = (postsData[category as keyof typeof postsData] || []).filter(
    post => !deletedPosts.has(post.id)
  )
  const showPublishButton = category === 'my-circle'

  // Like 逻辑
  const handleLike = (postId: string) => {
    setPostsData((prevData) => {
      const newData = { ...prevData }
      const targetPost = Object.values(newData)
        .flat()
        .find((post) => post.id === postId)
      if (targetPost) {
        const isLiked = targetPost.likedBy.includes('user-1')
        if (isLiked) {
          targetPost.likedBy = targetPost.likedBy.filter(
            (id) => id !== 'user-1'
          )
          targetPost.likes -= 1
        } else {
          targetPost.likedBy.push('user-1')
          targetPost.likes += 1
        }
      }
      return newData
    })
  }

  // 分享逻辑
  const handleShare = (postId: string) => {
    setPostsData((prevData) => {
      const newData = { ...prevData }
      const targetPost = Object.values(newData)
        .flat()
        .find((post) => post.id === postId)
      if (targetPost) {
        targetPost.shares += 1
      }
      return newData
    })
    // TODO: 实际分享功能
    console.log('分享帖子:', postId)
  }

  // 评论相关逻辑
  const toggleComments = (postId: string) => {
    setExpandedComments((prev) => ({
      ...prev,
      [postId]: !prev[postId],
    }))
  }

  const handleAddComment = (postId: string) => {
    const comment = newComments[postId]?.trim()
    if (!comment) return

    setPostsData((prevData) => {
      const newData = { ...prevData }
      const targetPost = Object.values(newData)
        .flat()
        .find((post) => post.id === postId)
      if (targetPost) {
        const newComment = {
          id: `comment-${Date.now()}`,
          author: t('social.me'),
          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=me',
          content: comment,
          timestamp: t('social.justNow'),
        }
        targetPost.comments.push(newComment)
      }
      return newData
    })

    setNewComments((prev) => ({
      ...prev,
      [postId]: '',
    }))
  }

  const handleDeletePost = (postId: string) => {
    setDeletedPosts(prev => new Set(prev).add(postId))
  }

  const handlePublishPost = () => {
    if (!newPost.trim()) return

    const newPostData: SocialPost = {
      id: `my-post-${Date.now()}`,
      author: t('social.me'),
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=me',
      content: newPost,
      timestamp: t('social.justNow'),
      likes: 0,
      likedBy: [],
      comments: [],
      shares: 0,
    }

    setPostsData((prev) => ({
      ...prev,
      'my-circle': [newPostData, ...prev['my-circle']],
    }))

    setNewPost('')
    setShowComposer(false)
  }

  return (
    <div
      className={cn(
        'h-screen overflow-y-auto',
        theme === 'dark' ? 'bg-background' : 'bg-gray-50/50'
      )}
    >
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
      {/* Publish Composer - Only for My Circle */}
      {showPublishButton && (
        <Card
          className={cn(
            'border-border/40 shadow-sm',
            theme === 'dark'
              ? 'bg-card/50 backdrop-blur-sm'
              : 'bg-white/80 backdrop-blur-sm'
          )}
        >
          <CardContent className="p-4">
            {!showComposer ? (
              <div className="flex items-center space-x-3">
                <Avatar className="h-10 w-10">
                  <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=me" />
                  <AvatarFallback className="text-sm font-medium">
                    {t('social.me')[0]}
                  </AvatarFallback>
                </Avatar>
                <Button
                  variant="outline"
                  className={cn(
                    'flex-1 justify-start text-muted-foreground bg-muted/30 hover:bg-muted/50 border-border/40',
                    'transition-all duration-200 hover:border-primary/20'
                  )}
                  onClick={() => setShowComposer(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {t('social.composer.placeholder')}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex space-x-3">
                  <Avatar className="h-10 w-10 flex-shrink-0">
                    <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=me" />
                    <AvatarFallback className="text-sm font-medium">
                      {t('social.me')[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-3">
                    <Textarea
                      placeholder={t('social.composer.expandedPlaceholder')}
                      value={newPost}
                      onChange={(e) => setNewPost(e.target.value)}
                      className={cn(
                        'min-h-[120px] resize-none border-border/40 bg-muted/20 focus:bg-background',
                        'focus:border-primary/40 transition-all duration-200',
                        'placeholder:text-muted-foreground/60'
                      )}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-border/20">
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-muted-foreground hover:text-primary hover:bg-primary/10"
                    >
                      <ImageIcon className="h-4 w-4 mr-2" />
                      {t('social.composer.image')}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-muted-foreground hover:text-primary hover:bg-primary/10"
                    >
                      <Smile className="h-4 w-4 mr-2" />
                      {t('social.composer.emoji')}
                    </Button>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setShowComposer(false)
                        setNewPost('')
                      }}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      {t('social.composer.cancel')}
                    </Button>
                    <Button
                      size="sm"
                      disabled={!newPost.trim()}
                      onClick={handlePublishPost}
                      className="px-6"
                    >
                      {t('social.composer.publish')}
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Posts */}
      <div className="space-y-6">
        {posts.map((post) => {
          const isLiked = post.likedBy.includes('user-1')
          const showComments = expandedComments[post.id]

          return (
            <Card
              key={post.id}
              className={cn(
                'border-border/40 shadow-sm transition-all duration-200 hover:shadow-md',
                theme === 'dark'
                  ? 'bg-card/50 backdrop-blur-sm'
                  : 'bg-white/80 backdrop-blur-sm'
              )}
            >
              <CardContent className="p-6">
                <div className="flex space-x-4">
                  <Avatar className="h-12 w-12 flex-shrink-0">
                    <AvatarImage src={post.avatar || '/placeholder.svg'} />
                    <AvatarFallback className="text-sm font-medium">
                      {post.author[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    {/* Post Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-foreground">
                          {post.author}
                        </span>
                        {post.isAI && (
                          <Badge
                            variant="secondary"
                            className="h-5 px-1.5 text-xs"
                          >
                            <Bot className="h-3 w-3 mr-1" />
                            AI
                          </Badge>
                        )}
                        <span className="text-sm text-muted-foreground">
                          {post.timestamp}
                        </span>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent 
                          align="end"
                          className={cn(
                            "min-w-[160px]",
                            theme === 'dark' 
                              ? "bg-gray-800 border-gray-700" 
                              : "bg-white border-gray-200"
                          )}
                        >
                          <DropdownMenuItem
                            onClick={() => handleDeletePost(post.id)}
                            className="text-red-600 focus:text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            {t('ui.delete')}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    {/* Post Content */}
                    <p className="text-foreground/90 leading-relaxed mb-4 whitespace-pre-wrap text-[15px]">
                      {post.content}
                    </p>

                    {/* Images */}
                    {'images' in post &&
                      post.images &&
                      post.images.length > 0 && (
                        <div className="mb-4">
                          {post.images.length === 1 ? (
                            <div className="rounded-lg overflow-hidden border border-border/20">
                              <img
                                src={post.images[0]}
                                alt=""
                                className="w-full max-h-[500px] object-cover"
                              />
                            </div>
                          ) : post.images.length === 2 ? (
                            <div className="grid grid-cols-2 gap-3">
                              {post.images.map((image, index) => (
                                <div
                                  key={index}
                                  className="rounded-lg overflow-hidden border border-border/20"
                                >
                                  <img
                                    src={image}
                                    alt=""
                                    className="w-full h-64 object-cover"
                                  />
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="grid grid-cols-2 gap-3">
                              {post.images.slice(0, 4).map((image, index) => (
                                <div
                                  key={index}
                                  className="relative rounded-lg overflow-hidden border border-border/20"
                                >
                                  <img
                                    src={image}
                                    alt=""
                                    className="w-full h-56 object-cover"
                                  />
                                  {index === 3 && post.images!.length > 4 && (
                                    <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                                      <span className="text-white font-semibold text-2xl">
                                        +{post.images!.length - 4}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-4 border-t border-border/20">
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleLike(post.id)}
                          className={cn(
                            'text-muted-foreground hover:text-red-500 transition-colors',
                            isLiked && 'text-red-500 hover:text-red-600'
                          )}
                        >
                          <Heart
                            className={cn(
                              'h-4 w-4 mr-1.5',
                              isLiked && 'fill-current'
                            )}
                          />
                          <span className="font-medium">{post.likes}</span>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleComments(post.id)}
                          className="text-muted-foreground hover:text-blue-500 transition-colors"
                        >
                          <MessageCircle className="h-4 w-4 mr-1.5" />
                          <span className="font-medium">
                            {post.comments.length}
                          </span>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleShare(post.id)}
                          className="text-muted-foreground hover:text-green-500 transition-colors"
                        >
                          <Share className="h-4 w-4 mr-1.5" />
                          <span className="font-medium">{post.shares}</span>
                        </Button>
                      </div>

                    </div>

                    {/* Comments Section */}
                    {showComments && (
                      <div className="mt-4 pt-4 border-t border-border/20 space-y-3">
                        {/* Comments List */}
                        {post.comments.map((comment) => (
                          <div key={comment.id} className="flex space-x-3">
                            <Avatar className="h-8 w-8 flex-shrink-0">
                              <AvatarImage src={comment.avatar} />
                              <AvatarFallback className="text-xs">
                                {comment.author[0]}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div
                                className={cn(
                                  'rounded-xl px-3 py-2',
                                  theme === 'dark'
                                    ? 'bg-muted/40'
                                    : 'bg-gray-100/80'
                                )}
                              >
                                <span className="font-medium text-sm text-foreground mr-2">
                                  {comment.author}
                                </span>
                                <span className="text-sm text-foreground/90">
                                  {comment.content}
                                </span>
                              </div>
                              <div className="text-xs text-muted-foreground mt-1 ml-3">
                                {comment.timestamp}
                              </div>
                            </div>
                          </div>
                        ))}

                        {/* Add Comment */}
                        <div className="flex space-x-3 mt-4">
                          <Avatar className="h-8 w-8 flex-shrink-0">
                            <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=me" />
                            <AvatarFallback className="text-xs">
                              {t('social.me')[0]}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 flex space-x-2">
                            <Input
                              placeholder={t('social.comment.placeholder')}
                              value={newComments[post.id] || ''}
                              onChange={(e) =>
                                setNewComments((prev) => ({
                                  ...prev,
                                  [post.id]: e.target.value,
                                }))
                              }
                              onKeyPress={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                  e.preventDefault()
                                  handleAddComment(post.id)
                                }
                              }}
                              className="text-sm border-border/40"
                            />
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleAddComment(post.id)}
                              disabled={!newComments[post.id]?.trim()}
                              className="flex-shrink-0"
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Empty State */}
      {posts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">{t('social.emptyState')}</p>
        </div>
      )}
      </div>
    </div>
  )
}

export default SocialContent
