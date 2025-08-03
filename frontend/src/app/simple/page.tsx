export default function SimplePage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Simple Test Page</h1>
      <p>This is a simple page without any internationalization to test basic routing.</p>
      <div className="mt-4">
        <a href="/" className="text-blue-500 underline">Back to Home</a>
      </div>
    </div>
  )
}