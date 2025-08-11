"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, ImageIcon, Download, Share } from "lucide-react"
import { cn } from "@/lib/utils"
interface FileItem {
  id: string
  name: string
  type: string
  size: string
  sharedBy: string
  timestamp: string
  category: string
}

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
  {
    id: "file-5",
    name: "API文档.md",
    type: "markdown",
    size: "156 KB",
    sharedBy: "AI 编程助手",
    timestamp: "2周前",
    category: "documents",
  },
  {
    id: "file-6",
    name: "用户调研报告.docx",
    type: "word",
    size: "3.2 MB",
    sharedBy: "AI 数据分析师",
    timestamp: "3周前",
    category: "documents",
  },
]

const categories = ["全部", "最近", "文档", "图片"]

interface FilesListCompactProps {
  selectedItem: string | null
  onItemSelect: (id: string) => void
}

export function FilesListCompact({ selectedItem, onItemSelect }: FilesListCompactProps) {
  const getFileIcon = (type: string) => {
    switch (type) {
      case "pdf":
      case "excel":
      case "word":
      case "markdown":
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
      case "word":
        return "bg-blue-100 text-blue-800"
      case "image":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div>
      {/* Category Filter */}
      <div className="p-3 border-b border-gray-100">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button key={category} variant="outline" size="sm" className="text-xs h-7 bg-transparent">
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Files Table */}
      <div className="divide-y divide-gray-100">
        {mockFiles.map((file) => {
          const FileIcon = getFileIcon(file.type)

          return (
            <div
              key={file.id}
              className={cn(
                "p-2 hover:bg-gray-50 cursor-pointer transition-colors",
                selectedItem === file.id && "bg-blue-50 border-r-2 border-blue-500",
              )}
              onClick={() => onItemSelect(file.id)}
            >
              <div className="flex items-center space-x-3">
                <FileIcon className="h-4 w-4 text-gray-500 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-medium text-sm text-gray-900 truncate">{file.name}</h3>
                    <Badge variant="secondary" className={cn("text-xs", getFileTypeColor(file.type))}>
                      {file.type.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{file.size}</span>
                    <span>•</span>
                    <span>{file.sharedBy}</span>
                    <span>•</span>
                    <span>{file.timestamp}</span>
                  </div>
                </div>
                <div className="flex space-x-1">
                  <Button size="sm" variant="ghost" className="p-1 h-6 w-6">
                    <Download className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="ghost" className="p-1 h-6 w-6">
                    <Share className="h-3 w-3" />
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
