"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Download, Share, Edit, Eye } from "lucide-react"

interface FilePreviewProps {
  selectedItem: string
}

export function FilePreview({ selectedItem }: FilePreviewProps) {
  return (
    <div className="p-6 space-y-6">
      {/* File Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">项目需求文档.pdf</CardTitle>
              <p className="text-gray-600 mt-1">由 AI 写作助手 分享 · 2小时前</p>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                预览
              </Button>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                编辑
              </Button>
              <Button variant="outline">
                <Share className="h-4 w-4 mr-2" />
                分享
              </Button>
              <Button>
                <Download className="h-4 w-4 mr-2" />
                下载
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Badge variant="secondary" className="bg-red-100 text-red-800">
              PDF
            </Badge>
            <span className="text-sm text-gray-600">2.3 MB</span>
            <span className="text-sm text-gray-600">15 页</span>
            <span className="text-sm text-gray-600">最后修改: 2024-01-15</span>
          </div>
        </CardContent>
      </Card>

      {/* File Preview */}
      <Card>
        <CardHeader>
          <CardTitle>文档预览</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 rounded-lg p-6 min-h-[400px]">
            <div className="bg-white rounded shadow-sm p-6 max-w-4xl mx-auto">
              <h1 className="text-2xl font-bold mb-4">AI协作平台项目需求文档</h1>

              <h2 className="text-lg font-semibold mb-3">1. 项目概述</h2>
              <p className="text-gray-700 mb-4">
                本项目旨在构建一个创新的AI协作平台，通过社交化的交互设计，
                让用户能够像使用微信、Slack等社交工具一样自然地与多个AI智能体进行协作。
              </p>

              <h2 className="text-lg font-semibold mb-3">2. 核心功能</h2>
              <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
                <li>智能联系人系统 - AI Agent作为虚拟联系人</li>
                <li>多模态对话交互 - 支持文本、图片、文件等</li>
                <li>群组协作功能 - 多AI智能体协同工作</li>
                <li>内容分享生态 - AI朋友圈和知识沉淀</li>
                <li>插件工具生态 - 可扩展的工具市场</li>
              </ul>

              <h2 className="text-lg font-semibold mb-3">3. 技术架构</h2>
              <p className="text-gray-700 mb-4">
                采用现代化的前端技术栈，包括React、Next.js、TypeScript等，
                后端使用Node.js和云原生架构，确保系统的可扩展性和稳定性。
              </p>

              <div className="text-center text-gray-500 mt-8">
                <p>... 文档内容继续 ...</p>
                <p className="text-sm mt-2">显示第 1 页，共 15 页</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Info */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">文件信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">文件大小:</span>
              <span>2.3 MB</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">页数:</span>
              <span>15 页</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">创建时间:</span>
              <span>2024-01-15 14:30</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">修改时间:</span>
              <span>2024-01-15 16:45</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">协作信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">创建者:</span>
              <span>AI 写作助手</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">共享给:</span>
              <span>项目团队</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">访问权限:</span>
              <span>可编辑</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">下载次数:</span>
              <span>12 次</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
