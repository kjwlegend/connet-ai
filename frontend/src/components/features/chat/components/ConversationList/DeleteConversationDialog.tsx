"use client"

import { useState } from "react"
import { Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useTranslations } from "@/lib/i18n/client"

interface DeleteConversationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  conversationTitle: string
  onConfirm: () => void
}

export function DeleteConversationDialog({
  open,
  onOpenChange,
  conversationTitle,
  onConfirm,
}: DeleteConversationDialogProps) {
  const t = useTranslations()
  const [isDeleting, setIsDeleting] = useState(false)

  const handleConfirm = async () => {
    setIsDeleting(true)
    try {
      await onConfirm()
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <Trash2 className="h-5 w-5" />
            {t('chat.contextMenu.delete')}
          </DialogTitle>
          <DialogDescription className="text-left">
            {t('chat.contextMenu.confirmDelete')}
            <br />
            <span className="font-medium text-foreground mt-2 block">
              "{conversationTitle}"
            </span>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
          >
            {t('ui.cancel')}
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isDeleting}
            className="gap-2"
          >
            {isDeleting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                {t('ui.loading')}
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                {t('ui.delete')}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}