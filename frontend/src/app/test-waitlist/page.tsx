'use client'

import { useState } from 'react'

export default function TestWaitlist() {
  const [email, setEmail] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const testJoinWaitlist = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/waitlist/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          source: 'test_page'
        })
      })
      const data = await response.json()
      setResult({ status: response.status, data })
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  const testStats = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/waitlist/stats')
      const data = await response.json()
      setResult({ status: response.status, data })
    } catch (error) {
      setResult({ error: error.message })
    }
    setLoading(false)
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Waitlist API Test</h1>
      
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="test@example.com"
          />
        </div>
        
        <div className="flex gap-4">
          <button
            onClick={testJoinWaitlist}
            disabled={loading || !email}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Test Join Waitlist
          </button>
          
          <button
            onClick={testStats}
            disabled={loading}
            className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
          >
            Test Stats
          </button>
        </div>
      </div>

      {loading && <div className="text-blue-500">Loading...</div>}
      
      {result && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Result:</h3>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}