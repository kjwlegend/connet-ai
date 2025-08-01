"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, ImageIcon, Download, Share } from "lucide-react"
import { cn } from "@/lib/utils"
import type { FileItem } from "@/types"

const mockFiles: FileItem[] = [
  {
    id: "file-1",
    name: "项目需求文档.pdf",
    type: "pdf",
    size: "2.3 MB",
    sharedBy: "AI 写作助手",
    timestamp: "2小时前",
    category: "documents",
  },
  {
    id: "file-2",
    name: "界面设计稿.fig",
    type: "figma",
    size: "15.7 MB",
    sharedBy: "AI 设计师",
    timestamp: "1天前",
    category: "images",
  },
  {
    id: "file-3",
    name: "数据分析报告.xlsx",
    type: "excel",
    size: "4.1 MB",
    sharedBy: "AI 数据分析师",
    timestamp: "3天前",
    category: "documents",
  },
  {
    id: "file-4",
    name: "代码架构图.png",
    type: "image",
    size: "890 KB",
    sharedBy: "AI 编程助手",
    timestamp: "1周前",
    category: "images",
  },
]

const categories = ["全部", "最近", "共享", "文档", "图片"]

interface FilesListProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function FilesList({ selectedItem, onItemSelect }: FilesListProps) {
  const getFileIcon = (type: string) => {
    switch (type) {
      case "pdf":
      case "excel":
      case "figma":
        return FileText
      case "image":
        return ImageIcon
      default:
        return FileText
    }
  }

  const getFileTypeColor = (type: string) => {
    switch (type) {
      case "pdf":
        return "bg-red-100 text-red-800"
      case "excel":
        return "bg-green-100 text-green-800"
      case "figma":
        return "bg-purple-100 text-purple-800"
      case "image":
        return "bg-blue-100 text-blue-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div>
      {/* Category Filter */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button key={category} variant="outline" size="sm" className="text-xs bg-transparent">
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Files List */}
      <div className="divide-y divide-gray-100">
        {mockFiles.map((file) => {
          const FileIcon = getFileIcon(file.type)

          return (
            <div
              key={file.id}
              className={cn(
                "p-4 hover:bg-gray-50 cursor-pointer transition-colors",
                selectedItem === file.id && "bg-blue-50 border-r-2 border-blue-500",
              )}
              onClick={() => onItemSelect(file.id)}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    <FileIcon className="h-5 w-5 text-gray-600" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate">{file.name}</h3>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge variant="secondary" className={cn("text-xs", getFileTypeColor(file.type))}>
                      {file.type.toUpperCase()}
                    </Badge>
                    <span className="text-xs text-gray-500">{file.size}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    由 {file.sharedBy} 分享 · {file.timestamp}
                  </p>
                </div>
                <div className="flex space-x-1">
                  <Button size="sm" variant="ghost" className="p-1">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="p-1">
                    <Share className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
