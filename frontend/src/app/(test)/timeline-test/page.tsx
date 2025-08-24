'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'

export default function TimelineTestPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [testData, setTestData] = useState({
    // Timeline filter settings
    category: 'friends_circle',
    authorType: 'all',
    limit: 20,
    skip: 0,
    
    // Post creation
    postContent: 'This is a test timeline post created via API testing',
    postType: 'text',
    visibility: 'public',
    tags: 'test,api,demo',
    attachmentUrl: '',
    postId: '',
    
    // Comment creation
    commentContent: 'This is a test comment on the timeline post',
    commentPostId: '',
    
    // Like/Unlike
    likePostId: '',
  })

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev])
  }

  const testGetTimelinePosts = async () => {
    try {
      addLog('Testing get timeline posts...')
      
      const params = new URLSearchParams({
        category: testData.category,
        skip: testData.skip.toString(),
        limit: testData.limit.toString(),
        ...(testData.authorType !== 'all' && { author_type: testData.authorType })
      })

      const response = await fetch(`/api/v1/timeline/posts?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Timeline posts retrieved: ${JSON.stringify(data, null, 2)}`)
        
        // Auto-populate post ID from first post for testing
        if (data.length > 0) {
          setTestData(prev => ({ 
            ...prev, 
            postId: data[0].id,
            commentPostId: data[0].id,
            likePostId: data[0].id
          }))
        }
      } else {
        const error = await response.text()
        addLog(`Get timeline posts failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get timeline posts error: ${error.message}`)
    }
  }

  const testCreatePost = async () => {
    try {
      addLog('Testing create timeline post...')
      
      const response = await fetch('/api/v1/timeline/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          content: testData.postContent,
          post_type: testData.postType,
          visibility: testData.visibility,
          tags: testData.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0),
          ...(testData.attachmentUrl && { attachment_url: testData.attachmentUrl })
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Timeline post created: ${JSON.stringify(data, null, 2)}`)
        setTestData(prev => ({ 
          ...prev, 
          postId: data.id,
          commentPostId: data.id,
          likePostId: data.id
        }))
      } else {
        const error = await response.text()
        addLog(`Create timeline post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Create timeline post error: ${error.message}`)
    }
  }

  const testGetPost = async () => {
    try {
      if (!testData.postId) {
        addLog('Error: No post ID provided')
        return
      }

      addLog('Testing get single timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.postId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Timeline post retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get timeline post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get timeline post error: ${error.message}`)
    }
  }

  const testUpdatePost = async () => {
    try {
      if (!testData.postId) {
        addLog('Error: No post ID provided')
        return
      }

      addLog('Testing update timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.postId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          content: testData.postContent + ' (Updated via API test)',
          post_type: testData.postType,
          visibility: testData.visibility,
          tags: testData.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Timeline post updated: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Update timeline post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Update timeline post error: ${error.message}`)
    }
  }

  const testDeletePost = async () => {
    try {
      if (!testData.postId) {
        addLog('Error: No post ID provided')
        return
      }

      addLog('Testing delete timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        addLog(`Timeline post deleted successfully`)
        setTestData(prev => ({ ...prev, postId: '', commentPostId: '', likePostId: '' }))
      } else {
        const error = await response.text()
        addLog(`Delete timeline post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Delete timeline post error: ${error.message}`)
    }
  }

  const testCreateComment = async () => {
    try {
      if (!testData.commentPostId) {
        addLog('Error: No post ID provided for comment')
        return
      }

      addLog('Testing create comment on timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.commentPostId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          content: testData.commentContent,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Comment created: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Create comment failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Create comment error: ${error.message}`)
    }
  }

  const testGetComments = async () => {
    try {
      if (!testData.commentPostId) {
        addLog('Error: No post ID provided')
        return
      }

      addLog('Testing get comments for timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.commentPostId}/comments?limit=20`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Comments retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get comments failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get comments error: ${error.message}`)
    }
  }

  const testLikePost = async () => {
    try {
      if (!testData.likePostId) {
        addLog('Error: No post ID provided for like')
        return
      }

      addLog('Testing like timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.likePostId}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Post liked: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Like post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Like post error: ${error.message}`)
    }
  }

  const testUnlikePost = async () => {
    try {
      if (!testData.likePostId) {
        addLog('Error: No post ID provided for unlike')
        return
      }

      addLog('Testing unlike timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.likePostId}/like`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        addLog(`Post unliked successfully`)
      } else {
        const error = await response.text()
        addLog(`Unlike post failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Unlike post error: ${error.message}`)
    }
  }

  const testGetLikes = async () => {
    try {
      if (!testData.likePostId) {
        addLog('Error: No post ID provided')
        return
      }

      addLog('Testing get likes for timeline post...')
      
      const response = await fetch(`/api/v1/timeline/posts/${testData.likePostId}/likes?limit=20`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        addLog(`Likes retrieved: ${JSON.stringify(data, null, 2)}`)
      } else {
        const error = await response.text()
        addLog(`Get likes failed: ${response.status} - ${error}`)
      }
    } catch (error: any) {
      addLog(`Get likes error: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Timeline/Social API Test</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Timeline Filter Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Category</label>
                  <Select
                    value={testData.category}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, category: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="friends_circle">Friends Circle</SelectItem>
                      <SelectItem value="public_square">Public Square</SelectItem>
                      <SelectItem value="my_circle">My Circle</SelectItem>
                      <SelectItem value="favorites">Favorites</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Author Type</label>
                  <Select
                    value={testData.authorType}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, authorType: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="user">Users Only</SelectItem>
                      <SelectItem value="agent">Agents Only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Limit</label>
                  <Input
                    type="number"
                    value={testData.limit}
                    onChange={(e) => setTestData(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Skip</label>
                  <Input
                    type="number"
                    value={testData.skip}
                    onChange={(e) => setTestData(prev => ({ ...prev, skip: parseInt(e.target.value) }))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Post Creation Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Post Content</label>
                <Textarea
                  value={testData.postContent}
                  onChange={(e) => setTestData(prev => ({ ...prev, postContent: e.target.value }))}
                  placeholder="Enter post content"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Post Type</label>
                  <Select
                    value={testData.postType}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, postType: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Text</SelectItem>
                      <SelectItem value="image">Image</SelectItem>
                      <SelectItem value="video">Video</SelectItem>
                      <SelectItem value="link">Link</SelectItem>
                      <SelectItem value="poll">Poll</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Visibility</label>
                  <Select
                    value={testData.visibility}
                    onValueChange={(value) => setTestData(prev => ({ ...prev, visibility: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">Public</SelectItem>
                      <SelectItem value="friends">Friends Only</SelectItem>
                      <SelectItem value="private">Private</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Tags (comma-separated)</label>
                <Input
                  value={testData.tags}
                  onChange={(e) => setTestData(prev => ({ ...prev, tags: e.target.value }))}
                  placeholder="tag1, tag2, tag3"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Attachment URL (optional)</label>
                <Input
                  value={testData.attachmentUrl}
                  onChange={(e) => setTestData(prev => ({ ...prev, attachmentUrl: e.target.value }))}
                  placeholder="https://example.com/image.jpg"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Post Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Post ID</label>
                <Input
                  value={testData.postId}
                  onChange={(e) => setTestData(prev => ({ ...prev, postId: e.target.value }))}
                  placeholder="Enter post ID for management"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Comment Content</label>
                <Textarea
                  value={testData.commentContent}
                  onChange={(e) => setTestData(prev => ({ ...prev, commentContent: e.target.value }))}
                  placeholder="Enter comment content"
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Timeline Test Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button onClick={testGetTimelinePosts} className="w-full" variant="default">
                Get Timeline Posts
              </Button>
              
              <Button onClick={testCreatePost} className="w-full" variant="outline">
                Create Timeline Post
              </Button>
              
              <Button onClick={testGetPost} className="w-full" variant="outline">
                Get Single Post
              </Button>
              
              <Button onClick={testUpdatePost} className="w-full" variant="outline">
                Update Post
              </Button>
              
              <div className="grid grid-cols-2 gap-2">
                <Button onClick={testCreateComment} variant="outline">
                  Add Comment
                </Button>
                <Button onClick={testGetComments} variant="outline">
                  Get Comments
                </Button>
              </div>
              
              <div className="grid grid-cols-3 gap-2">
                <Button onClick={testLikePost} variant="outline">
                  Like Post
                </Button>
                <Button onClick={testUnlikePost} variant="outline">
                  Unlike Post
                </Button>
                <Button onClick={testGetLikes} variant="outline">
                  Get Likes
                </Button>
              </div>
              
              <Button onClick={testDeletePost} className="w-full" variant="destructive">
                Delete Post
              </Button>
              
              <Button onClick={() => setLogs([])} className="w-full" variant="secondary">
                Clear Logs
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Timeline Test Results</CardTitle>
            <p className="text-sm text-gray-500">
              Tests social timeline functionality including posts, comments, and likes
            </p>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No test results yet</p>
                  <p className="text-xs mt-2">
                    Start with "Get Timeline Posts" to see available posts
                  </p>
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="text-sm font-mono mb-2 break-all">
                    {log}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}