'use client'

import { useEffect } from "react"
import { useTheme } from "next-themes"
import { Hero } from "@/components/hero"
import { Header } from "@/components/header"

export default function Page() {
  const { setTheme } = useTheme()

  // 랜딩페이지는 항상 다크모드
  useEffect(() => {
    setTheme("dark")
  }, [])

  return (
    <>
      <Header />
      <Hero />
    </>
  )
}
