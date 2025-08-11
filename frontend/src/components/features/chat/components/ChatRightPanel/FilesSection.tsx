"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { FileText, ChevronDown, ChevronRight, Download, Share, MoreHorizontal } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"
import { AllFilesDialog } from "./AllFilesDialog"

interface File {
  id: string
  name: string
  type: string
  size: string
  uploadedAt: string
  url: string
}

interface FilesSectionProps {
  files?: File[]
  onDownloadFile?: (file: File) => void
  onShareFile?: (file: File) => void
}

// Mock data for files - Extended with more files to test the 5-item limit
const mockFiles: File[] = [
  {
    id: '1',
    name: 'project-proposal.pdf',
    type: 'application/pdf',
    size: '2.3 MB',
    uploadedAt: new Date(Date.now() - 3600000).toISOString(),
    url: '#'
  },
  {
    id: '2',
    name: 'code-review.md',
    type: 'text/markdown',
    size: '15 KB',
    uploadedAt: new Date(Date.now() - 7200000).toISOString(),
    url: '#'
  },
  {
    id: '3',
    name: 'analysis-report.xlsx',
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    size: '890 KB',
    uploadedAt: new Date(Date.now() - 86400000).toISOString(),
    url: '#'
  },
  {
    id: '4',
    name: 'meeting-notes.docx',
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    size: '45 KB',
    uploadedAt: new Date(Date.now() - 172800000).toISOString(),
    url: '#'
  },
  {
    id: '5',
    name: 'design-mockups.sketch',
    type: 'application/sketch',
    size: '5.2 MB',
    uploadedAt: new Date(Date.now() - 259200000).toISOString(),
    url: '#'
  },
  {
    id: '6',
    name: 'technical-specs.pdf',
    type: 'application/pdf',
    size: '1.8 MB',
    uploadedAt: new Date(Date.now() - 345600000).toISOString(),
    url: '#'
  },
  {
    id: '7',
    name: 'user-feedback.xlsx',
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    size: '234 KB',
    uploadedAt: new Date(Date.now() - 432000000).toISOString(),
    url: '#'
  },
  {
    id: '8',
    name: 'presentation.pptx',
    type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    size: '12.5 MB',
    uploadedAt: new Date(Date.now() - 518400000).toISOString(),
    url: '#'
  }
]

export function FilesSection({ 
  files = mockFiles, 
  onDownloadFile, 
  onShareFile 
}: FilesSectionProps) {
  const t = useTranslations()
  const [isFilesExpanded, setIsFilesExpanded] = useState(true)
  const [showAllFilesDialog, setShowAllFilesDialog] = useState(false)

  // Only show first 5 files in the list
  const displayedFiles = files.slice(0, 5)
  const hasMoreFiles = files.length > 5

  const formatFileSize = (size: string) => size

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffMs = now.getTime() - time.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffDays > 0) return `${diffDays}天前`
    if (diffHours > 0) return `${diffHours}小时前`
    return '刚刚'
  }

  const handleDownloadFile = (file: File) => {
    if (onDownloadFile) {
      onDownloadFile(file)
    } else {
      // Default download behavior
      console.log('Downloading file:', file.name)
      const link = document.createElement('a')
      link.href = file.url || '#'
      link.download = file.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleShareFile = (file: File) => {
    if (onShareFile) {
      onShareFile(file)
    } else {
      // Default share behavior
      console.log('Sharing file to conversation:', file.name)
    }
  }

  return (
    <div>
      <div 
        className="flex items-center justify-between mb-3 cursor-pointer"
        onClick={() => setIsFilesExpanded(!isFilesExpanded)}
      >
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium text-sm">{t('chat.rightPanel.files')} ({files.length})</span>
        </div>
        {isFilesExpanded ? (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
      </div>

      {isFilesExpanded && (
        <div className="space-y-2">
          {displayedFiles.map((file) => (
            <div key={file.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-accent/50 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {file.name}
                </p>
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <span>{formatFileSize(file.size)}</span>
                  <span>•</span>
                  <span>{formatTimeAgo(file.uploadedAt)}</span>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-7 w-7 p-0"
                  onClick={() => handleDownloadFile(file)}
                  title={t('chat.rightPanel.downloadFile')}
                >
                  <Download className="h-3 w-3" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-7 w-7 p-0"
                  onClick={() => handleShareFile(file)}
                  title={t('chat.rightPanel.shareToConversation')}
                >
                  <Share className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
          
          {/* Show more files button */}
          {hasMoreFiles && (
            <div className="pt-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setShowAllFilesDialog(true)}
                className="w-full h-8 text-muted-foreground hover:text-foreground"
              >
                <MoreHorizontal className="h-4 w-4 mr-2" />
                查看全部 {files.length} 个文件
              </Button>
            </div>
          )}
        </div>
      )}

      {/* All Files Dialog */}
      <AllFilesDialog
        open={showAllFilesDialog}
        onOpenChange={setShowAllFilesDialog}
        files={files}
        onDownloadFile={onDownloadFile}
        onShareFile={onShareFile}
      />
    </div>
  )
}

export default FilesSection