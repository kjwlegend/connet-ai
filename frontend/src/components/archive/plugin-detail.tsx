"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Star, Download, Settings, Play, Code } from "lucide-react"

interface PluginDetailProps {
  selectedItem: string
}

export function PluginDetail({ selectedItem }: PluginDetailProps) {
  return (
    <div className="p-6 space-y-6">
      {/* Plugin Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 bg-linear-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-3xl text-white">
              🔧
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <CardTitle className="text-2xl">代码生成器</CardTitle>
                <Badge variant="secondary">开发工具</Badge>
                <Badge variant="outline" className="text-green-600">
                  已安装
                </Badge>
              </div>
              <p className="text-gray-600 mt-2">基于需求自动生成高质量代码，支持多种编程语言和框架</p>
              <div className="flex items-center space-x-4 mt-3">
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  <span className="font-medium">4.8</span>
                  <span className="text-gray-500">(1,234 评价)</span>
                </div>
                <span className="text-gray-500">•</span>
                <span className="text-gray-500">15,678 次下载</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button>
                <Play className="h-4 w-4 mr-2" />
                启动插件
              </Button>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                配置
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Plugin Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">概览</TabsTrigger>
          <TabsTrigger value="features">功能特性</TabsTrigger>
          <TabsTrigger value="examples">使用示例</TabsTrigger>
          <TabsTrigger value="reviews">用户评价</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>插件介绍</CardTitle>
            </CardHeader>
            <CardContent className="prose max-w-none">
              <p>
                代码生成器是一个强大的AI驱动开发工具，能够根据自然语言描述自动生成高质量的代码。
                无论你是初学者还是经验丰富的开发者，这个插件都能显著提升你的开发效率。
              </p>

              <h4>主要优势：</h4>
              <ul>
                <li>支持20+种编程语言</li>
                <li>智能理解需求描述</li>
                <li>生成符合最佳实践的代码</li>
                <li>自动添加注释和文档</li>
                <li>支持代码重构和优化</li>
              </ul>

              <h4>适用场景：</h4>
              <ul>
                <li>快速原型开发</li>
                <li>重复性代码生成</li>
                <li>API接口实现</li>
                <li>数据库操作代码</li>
                <li>单元测试编写</li>
              </ul>
            </CardContent>
          </Card>

          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <Code className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">20+</div>
                <p className="text-sm text-gray-600">支持语言</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <Download className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">15K+</div>
                <p className="text-sm text-gray-600">下载量</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <Star className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">4.8</div>
                <p className="text-sm text-gray-600">用户评分</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="features" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">智能代码生成</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">基于先进的AI模型，理解自然语言需求，生成符合规范的代码</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">多语言支持</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">支持JavaScript、Python、Java、Go等20多种主流编程语言</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">代码优化</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">自动优化代码性能，遵循最佳实践，提供重构建议</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">测试生成</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">自动生成单元测试和集成测试，确保代码质量</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="examples" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>使用示例</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h4 className="font-medium mb-2">示例1: 创建React组件</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-2">输入描述：</p>
                    <p className="text-sm bg-blue-50 p-2 rounded">"创建一个用户卡片组件，显示头像、姓名、邮箱和状态"</p>
                    <p className="text-sm text-gray-600 mt-3 mb-2">生成代码：</p>
                    <pre className="text-xs bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
                      {`const UserCard = ({ user }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <img 
        src={user.avatar || "/placeholder.svg"} 
        alt={user.name}
        className="w-16 h-16 rounded-full mx-auto mb-4"
      />
      <h3 className="text-lg font-semibold text-center">{user.name}</h3>
      <p className="text-gray-600 text-center">{user.email}</p>
      <span className={\`inline-block px-2 py-1 rounded-full text-xs \${
        user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
      }\`}>
        {user.status}
      </span>
    </div>
  );
};`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">示例2: API接口实现</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-2">输入描述：</p>
                    <p className="text-sm bg-blue-50 p-2 rounded">"创建一个用户管理的REST API，包含增删改查功能"</p>
                    <p className="text-sm text-gray-600 mt-3 mb-2">生成代码：</p>
                    <pre className="text-xs bg-gray-800 text-green-400 p-3 rounded overflow-x-auto">
                      {`// GET /api/users
app.get('/api/users', async (req, res) => {
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/users
app.post('/api/users', async (req, res) => {
  try {
    const user = await User.create(req.body);
    res.status(201).json(user);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});`}
                    </pre>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reviews" className="space-y-4">
          <div className="space-y-4">
            {[
              {
                name: "张开发",
                avatar: "/placeholder.svg?height=40&width=40",
                rating: 5,
                comment: "非常好用的插件！大大提升了我的开发效率，生成的代码质量很高。",
                time: "2天前",
              },
              {
                name: "李程序员",
                avatar: "/placeholder.svg?height=40&width=40",
                rating: 5,
                comment: "支持的语言很全面，AI理解能力很强，推荐给所有开发者！",
                time: "1周前",
              },
              {
                name: "王工程师",
                avatar: "/placeholder.svg?height=40&width=40",
                rating: 4,
                comment: "整体很不错，偶尔生成的代码需要微调，但已经节省了很多时间。",
                time: "2周前",
              },
            ].map((review, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={review.avatar || "/placeholder.svg"} />
                      <AvatarFallback>{review.name[0]}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{review.name}</span>
                        <div className="flex">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              className={`h-4 w-4 ${
                                star <= review.rating ? "text-yellow-400 fill-current" : "text-gray-300"
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-gray-500">{review.time}</span>
                      </div>
                      <p className="text-gray-700 mt-1">{review.comment}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
