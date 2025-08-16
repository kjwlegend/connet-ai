/**
 * Test script to verify error handling
 */

const API_BASE = 'http://localhost:8001';

async function testErrorHandling() {
  console.log('Testing BFF error handling...');
  
  try {
    // Test duplicate registration (should return 400 with detail message)
    const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: '56349014@qq.com', // Use the email that already exists
        password: 'password123',
        full_name: 'Test User',
        username: 'testuser'
      })
    });
    
    console.log(`Status: ${response.status}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.log('Error response:', JSON.stringify(errorData, null, 2));
      
      // Test our error message extraction logic
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        errorMessage = errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
      
      console.log('Extracted error message:', errorMessage);
    }
    
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}

testErrorHandling();