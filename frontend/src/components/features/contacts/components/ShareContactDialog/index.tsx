'use client'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useTranslations } from '@/lib/i18n/client'
import { MessageCircle, Link2, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import { AIAgent } from '@/types/contact'

interface ShareContactDialogProps {
  isOpen: boolean
  onClose: () => void
  contact: AIAgent | null
  onShareToConversation: (contactId: string) => void
  onGenerateShareLink: (contactId: string) => Promise<string>
}

export function ShareContactDialog({
  isOpen,
  onClose,
  contact,
  onShareToConversation,
  onGenerateShareLink,
}: ShareContactDialogProps) {
  const t = useTranslations()
  const [shareLink, setShareLink] = useState<string>('')
  const [isGeneratingLink, setIsGeneratingLink] = useState(false)
  const [isCopied, setIsCopied] = useState(false)

  if (!contact) return null

  const handleGenerateLink = async () => {
    setIsGeneratingLink(true)
    try {
      const link = await onGenerateShareLink(contact.id)
      setShareLink(link)
    } catch (error) {
      console.error('Failed to generate share link:', error)
    } finally {
      setIsGeneratingLink(false)
    }
  }

  const handleCopyLink = async () => {
    if (shareLink) {
      await navigator.clipboard.writeText(shareLink)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    }
  }

  const handleShareToConversation = () => {
    onShareToConversation(contact.id)
    onClose()
  }

  const handleClose = () => {
    setShareLink('')
    setIsCopied(false)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t('contacts.shareContactTitle')}</DialogTitle>
          <DialogDescription>
            {t('contacts.shareContactDesc')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Contact Info */}
          <div className="flex items-center space-x-3 p-3 bg-muted/30 rounded-lg">
            <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
              <span className="font-medium text-primary">
                {(contact.displayName || contact.name)[0]}
              </span>
            </div>
            <div>
              <div className="font-medium">
                {contact.displayName || contact.name}
              </div>
              <div className="text-sm text-muted-foreground">@{contact.id}</div>
            </div>
          </div>

          {/* Share Options */}
          <div className="space-y-3">
            {/* Share to Conversation */}
            <Button
              onClick={handleShareToConversation}
              className="w-full justify-start h-12"
              variant="outline"
            >
              <MessageCircle className="h-4 w-4 mr-3" />
              <div className="text-left">
                <div className="font-medium">
                  {t('contacts.shareToConversation')}
                </div>
                <div className="text-xs text-muted-foreground">
                  {t('contacts.shareContactDesc')}
                </div>
              </div>
            </Button>

            {/* Generate Share Link */}
            <div className="space-y-2">
              <Button
                onClick={handleGenerateLink}
                className="w-full justify-start h-12"
                variant="outline"
                disabled={isGeneratingLink}
              >
                <Link2 className="h-4 w-4 mr-3" />
                <div className="text-left">
                  <div className="font-medium">
                    {t('contacts.generateShareLink')}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Create a unique link to share this contact
                  </div>
                </div>
              </Button>

              {shareLink && (
                <div className="space-y-2">
                  <Label htmlFor="share-link" className="text-sm">
                    Share Link
                  </Label>
                  <div className="flex space-x-2">
                    <Input
                      id="share-link"
                      value={shareLink}
                      readOnly
                      className="flex-1"
                    />
                    <Button
                      onClick={handleCopyLink}
                      variant="outline"
                      size="sm"
                      className="px-3"
                    >
                      {isCopied ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            {t('contacts.cancel')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ShareContactDialog
