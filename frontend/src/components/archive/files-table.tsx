"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { FileText, Download, Share, Database, MoreHorizontal } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

const mockFiles = [
  {
    id: "file-1",
    name: "项目需求文档.pdf",
    type: "pdf",
    size: "2.3 MB",
    sharedBy: "AI 写作助手",
    timestamp: "2024-01-15 14:30",
    category: "documents",
  },
  {
    id: "file-2",
    name: "界面设计稿.fig",
    type: "figma",
    size: "15.7 MB",
    sharedBy: "AI 设计师",
    timestamp: "2024-01-14 16:45",
    category: "design",
  },
  {
    id: "file-3",
    name: "数据分析报告.xlsx",
    type: "excel",
    size: "4.1 MB",
    sharedBy: "AI 数据分析师",
    timestamp: "2024-01-13 10:20",
    category: "data",
  },
  {
    id: "file-4",
    name: "代码架构图.png",
    type: "image",
    size: "890 KB",
    sharedBy: "AI 编程助手",
    timestamp: "2024-01-12 09:15",
    category: "technical",
  },
  {
    id: "file-5",
    name: "API文档.md",
    type: "markdown",
    size: "156 KB",
    sharedBy: "AI 编程助手",
    timestamp: "2024-01-11 15:30",
    category: "technical",
  },
]

interface FilesTableProps {
  category: string
}

export function FilesTable({ category }: FilesTableProps) {
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
      case "markdown":
        return "bg-gray-100 text-gray-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const title = category === "knowledge" ? "知识库文件" : "文件列表"

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>文件名</TableHead>
                <TableHead>类型</TableHead>
                <TableHead>大小</TableHead>
                <TableHead>分享者</TableHead>
                <TableHead>时间</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockFiles.map((file) => (
                <TableRow key={file.id}>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4 text-gray-500" />
                      <span className="font-medium">{file.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className={getFileTypeColor(file.type)}>
                      {file.type.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>{file.size}</TableCell>
                  <TableCell>{file.sharedBy}</TableCell>
                  <TableCell>{file.timestamp}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-1">
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <Share className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <Database className="h-4 w-4" />
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Download className="h-4 w-4 mr-2" />
                            下载
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Share className="h-4 w-4 mr-2" />
                            分享
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Database className="h-4 w-4 mr-2" />
                            导入知识库
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
