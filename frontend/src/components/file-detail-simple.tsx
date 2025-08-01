"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Download, Share, Edit, Eye, FileText } from "lucide-react"

interface FileDetailSimpleProps {
  selectedItem: string
}

export function FileDetailSimple({ selectedItem }: FileDetailSimpleProps) {
  return (
    <div className="p-6 space-y-4">
      {/* File Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-gray-500" />
              <div>
                <CardTitle className="text-lg">项目需求文档.pdf</CardTitle>
                <p className="text-sm text-gray-600">由 AI 写作助手 分享 · 2小时前</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-1" />
                预览
              </Button>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-1" />
                编辑
              </Button>
              <Button variant="outline" size="sm">
                <Share className="h-4 w-4 mr-1" />
                分享
              </Button>
              <Button size="sm">
                <Download className="h-4 w-4 mr-1" />
                下载
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <Badge variant="secondary" className="bg-red-100 text-red-800">
              PDF
            </Badge>
            <span>2.3 MB</span>
            <span>15 页</span>
            <span>最后修改: 2024-01-15</span>
          </div>
        </CardContent>
      </Card>

      {/* File List Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">相关文件</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[
              { name: "项目需求文档_v2.pdf", size: "2.5 MB", time: "1小时前" },
              { name: "技术方案.docx", size: "1.8 MB", time: "3小时前" },
              { name: "原型设计.fig", size: "12.3 MB", time: "1天前" },
              { name: "数据库设计.sql", size: "45 KB", time: "2天前" },
            ].map((file, index) => (
              <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {file.size} • {file.time}
                    </div>
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
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
