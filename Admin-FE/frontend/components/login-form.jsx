"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useAuth } from "@/contexts/AuthContext"
import { apiJson, apiConfig } from "@/lib/api-config"
import { SplineScene } from "@/components/spline-scene"


export function LoginForm({ className, onSuccess, onSwitchToSignup, ...props }) {
  const router = useRouter()
  const { loginWithToken } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    try {
      // OpenAPI: x-www-form-urlencoded
      const body = new URLSearchParams({ username: email, password })
      const res = await fetch(
        `${apiConfig.baseURL}${apiConfig.endpoints.auth.login}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body,
        }
      )
      if (!res.ok) {
        throw new Error("로그인 실패")
      }
      const data = await res.json()
      const token = data?.access_token
      if (!token) throw new Error("토큰이 없습니다")
      loginWithToken(token)
      if (onSuccess) onSuccess()
      // 로그인 후 대시보드로 이동을 원하면 아래 라인 주석 해제
      // router.push('/dashboard')
    } catch (err) {
      setError("아이디 또는 비밀번호가 올바르지 않습니다.")
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <div className="grid md:grid-cols-2">
        <form className="p-6 md:p-8" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="flex flex-col items-center text-center">
                <h1 className="text-2xl font-bold">Welcome back</h1>
                <p className="text-balance text-muted-foreground">Login to your Acme Inc account</p>
              </div>
              {error && (
                <div className="text-sm text-red-500 text-center">{error}</div>
              )}
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="text"
                  placeholder="admin"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a href="#" className="ml-auto text-sm underline-offset-2 hover:underline">
                    Forgot your password?
                  </a>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full">
                Login
              </Button>
              <div className="text-center text-sm">
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  onClick={onSwitchToSignup}
                  className="underline underline-offset-4 hover:text-primary"
                >
                  Sign up
                </button>
              </div>
            </div>
          </form>
          <div className="relative hidden bg-black md:block">
            <SplineScene
              scene="https://prod.spline.design/UbM7F-HZcyTbZ4y3/scene.splinecode"
              className="w-full h-full"
            />
          </div>
        </div>
      <div className="text-balance text-center text-xs text-muted-foreground [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary">
        By clicking continue, you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
      </div>
    </div>
  )
}
