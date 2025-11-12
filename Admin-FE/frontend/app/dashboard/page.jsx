"use client"

import { useState, useEffect } from "react"
import { ChevronRight, Monitor, Settings, Shield, Target, Users, Bell, RefreshCw, LogOut, FileText, Sliders } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"
import { ThemeToggle } from "@/components/theme-toggle"
import { useTheme } from "next-themes"
import CommandCenterPage from "./command-center/page"
import AgentNetworkPage from "./agent-network/page"
import OperationsPage from "./operations/page"
import IntelligencePage from "./intelligence/page"
import SystemsPage from "./systems/page"
import LogsPage from "./logs/page"
import DetectionSettingsPage from "./detection-settings/page"

export default function TacticalDashboard() {
  const router = useRouter()
  const { logout } = useAuth()
  const { setTheme } = useTheme()
  const [activeSection, setActiveSection] = useState("overview")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // 대시보드 첫 진입 시에만 라이트 모드로 설정
  useEffect(() => {
    setTheme("light")
  }, []) // 빈 의존성 배열로 마운트 시 한 번만 실행

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={`${sidebarCollapsed ? "w-16" : "w-70"} bg-gradient-to-b from-yellow-900/20 via-background to-background border-r border-yellow-500/30 transition-all duration-300 fixed md:relative z-50 md:z-auto h-full md:h-auto ${!sidebarCollapsed ? "md:block" : ""}`}
      >
        <div className="p-4">
          <div className="flex items-center justify-between mb-8">
            <div className={`${sidebarCollapsed ? "hidden" : "block"}`}>
              <h1 className="bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 bg-clip-text text-transparent font-bold text-lg tracking-wider">DS MASKING AI</h1>
              <p className="text-gray-700 dark:text-gray-400 text-xs font-bold">v1.0.0 SECURE</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="text-gray-700 dark:text-gray-400 hover:text-amber-600"
            >
              <ChevronRight
                className={`w-4 h-4 sm:w-5 sm:h-5 transition-transform ${sidebarCollapsed ? "" : "rotate-180"}`}
              />
            </Button>
          </div>

          <nav className="space-y-2">
            {[
              { id: "overview", icon: Monitor, label: "대시보드" },
              { id: "logs", icon: FileText, label: "전체 로그 페이지" },
              { id: "detection", icon: Sliders, label: "탐지 기능 설정" },
              { id: "agents", icon: Users, label: "프로젝트 관리" },
              { id: "systems", icon: Settings, label: "시스템 설정" },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 p-3 rounded transition-colors ${
                  activeSection === item.id
                    ? "bg-gradient-to-r from-yellow-600 to-amber-600 text-white font-bold"
                    : "text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-yellow-900/30 font-semibold"
                }`}
              >
                <item.icon className="w-5 h-5 md:w-5 md:h-5 sm:w-6 sm:h-6" />
                {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
              </button>
            ))}
          </nav>

          {!sidebarCollapsed && (
            <div className="mt-8 p-4 bg-yellow-900/20 border border-yellow-500/30 rounded">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-gray-400 font-bold">SYSTEM ONLINE</span>
              </div>
              <div className="text-xs text-gray-400 font-semibold">
                <div>UPTIME: 72:14:33</div>
                <div>AGENTS: 847 ACTIVE</div>
                <div>MISSIONS: 23 ONGOING</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Overlay */}
      {!sidebarCollapsed && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarCollapsed(true)} />
      )}

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${!sidebarCollapsed ? "md:ml-0" : ""}`}>
        {/* Top Toolbar */}
        <div className="h-16 bg-gradient-to-r from-yellow-900/20 via-background to-amber-900/20 border-b border-yellow-500/30 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-700 dark:text-gray-400 font-semibold">
              TACTICAL COMMAND / <span className="bg-gradient-to-r from-amber-600 to-amber-700 bg-clip-text text-transparent font-bold">OVERVIEW</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-gray-700 dark:text-gray-500 font-semibold">LAST UPDATE: 05/06/2025 20:00 UTC</div>
            <Button variant="ghost" size="icon" className="text-gray-700 dark:text-gray-400 hover:text-amber-600">
              <Bell className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" className="text-gray-700 dark:text-gray-400 hover:text-amber-600">
              <RefreshCw className="w-4 h-4" />
            </Button>
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="text-gray-700 dark:text-gray-400 hover:text-amber-600"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto">
          {activeSection === "overview" && <CommandCenterPage />}
          {activeSection === "agents" && <AgentNetworkPage />}
          {activeSection === "operations" && <OperationsPage />}
          {activeSection === "intelligence" && <IntelligencePage />}
          {activeSection === "systems" && <SystemsPage />}
          {activeSection === "logs" && <LogsPage />}
          {activeSection === "detection" && <DetectionSettingsPage />}
        </div>
      </div>
    </div>
  )
}
