export default function SimpleHomePage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Connet.AI - AI Collaboration Platform
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Chat</h2>
            <p className="text-gray-600">
              Start conversations with AI agents
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Contacts</h2>
            <p className="text-gray-600">
              Manage your AI agent contacts
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Files</h2>
            <p className="text-gray-600">
              Share and manage files
            </p>
          </div>
        </div>
        
        <div className="mt-8">
          <a href="/test-i18n" className="text-blue-500 underline">
            Test Internationalization
          </a>
          {" | "}
          <a href="/simple" className="text-blue-500 underline">
            Simple Test Page
          </a>
        </div>
      </div>
    </div>
  )
}