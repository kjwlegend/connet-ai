"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Search, FileText, Download, Share } from "lucide-react"
import { useTranslations } from "@/lib/i18n/client"

interface File {
  id: string
  name: string
  type: string
  size: string
  uploadedAt: string
  url: string
}

interface AllFilesDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  files: File[]
  onDownloadFile?: (file: File) => void
  onShareFile?: (file: File) => void
}

export function AllFilesDialog({
  open,
  onOpenChange,
  files,
  onDownloadFile,
  onShareFile
}: AllFilesDialogProps) {
  const t = useTranslations()
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

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

  const getFileTypeIcon = (type: string) => {
    // You can add more specific icons based on file types
    return <FileText className="h-4 w-4 text-muted-foreground" />
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

  // Filter and sort files
  const filteredAndSortedFiles = files
    .filter(file => 
      file.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'date':
          comparison = new Date(a.uploadedAt).getTime() - new Date(b.uploadedAt).getTime()
          break
        case 'size':
          // Simple size comparison - in real implementation, you'd parse the size properly
          const sizeA = parseFloat(a.size)
          const sizeB = parseFloat(b.size)
          comparison = sizeA - sizeB
          break
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-3xl max-h-[80vh] w-[90vw]">
        <DialogHeader>
          <DialogTitle className="text-lg">群文件 ({files.length})</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search and Sort */}
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索文件..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'date' | 'size')}
                className="px-3 py-2 text-sm border border-border rounded-md bg-background"
              >
                <option value="date">按时间排序</option>
                <option value="name">按名称排序</option>
                <option value="size">按大小排序</option>
              </select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-2"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </Button>
            </div>
          </div>

          {/* Files List */}
          <ScrollArea className="h-[400px]">
            <div className="space-y-2">
              {filteredAndSortedFiles.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">
                    {searchQuery ? `没有找到匹配 "${searchQuery}" 的文件` : '暂无文件'}
                  </p>
                </div>
              ) : (
                filteredAndSortedFiles.map((file) => (
                  <div key={file.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-colors border border-border/40">
                    <div className="flex-shrink-0">
                      {getFileTypeIcon(file.type)}
                    </div>
                    
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
                        className="h-8 w-8 p-0"
                        onClick={() => handleDownloadFile(file)}
                        title="下载文件"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-8 w-8 p-0"
                        onClick={() => handleShareFile(file)}
                        title="分享到对话"
                      >
                        <Share className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default AllFilesDialog