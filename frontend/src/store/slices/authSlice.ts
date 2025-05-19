// src/store/slices/authSlice.ts
import { StateCreator } from 'zustand'
import { StoreState } from '../types'

export interface User {
  id: string
  name: string
  email: string
  // Add other user properties as needed
}

export interface AuthSlice {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (userData: User, token: string) => void
  logout: () => void
  // Add other auth actions like register, loadUser, etc.
}

const createAuthSlice: StateCreator<StoreState, [], [], AuthSlice> = (set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: (userData, token) => {
    // In a real app, you might store the token in localStorage/sessionStorage
    // localStorage.setItem('token', token);
    set({ user: userData, token, isAuthenticated: true })
  },
  logout: () => {
    // localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false })
  },
})

export default createAuthSlice
