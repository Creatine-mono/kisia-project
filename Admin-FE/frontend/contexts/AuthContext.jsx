"use client"

import { createContext, useContext, useState, useEffect } from "react"

const AuthContext = createContext(undefined)

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null)
  const isLoggedIn = !!accessToken

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (token) {
      setAccessToken(token)
    }
  }, [])

  const loginWithToken = (token) => {
    setAccessToken(token)
    localStorage.setItem('access_token', token)
  }

  const logout = () => {
    setAccessToken(null)
    localStorage.removeItem('access_token')
  }

  return (
    <AuthContext.Provider value={{ isLoggedIn, accessToken, loginWithToken, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
