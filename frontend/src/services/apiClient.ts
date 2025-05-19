// src/services/apiClient.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api/py', // Adjust to your backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
})

// You can add interceptors for request/response handling (e.g., adding auth tokens)
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('token'); // Or get from your auth state
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

export default apiClient
