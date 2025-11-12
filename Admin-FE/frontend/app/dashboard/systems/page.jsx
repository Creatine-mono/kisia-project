"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Server,
  Database,
  Shield,
  Wifi,
  HardDrive,
  Cpu,
  Activity,
  AlertTriangle,
  CheckCircle,
  Settings,
} from "lucide-react"

export default function SystemsPage() {
  const [selectedSystem, setSelectedSystem] = useState(null)

  const systems = [
    {
      id: "SYS-001",
      name: "주 서버 ALPHA",
      type: "주 서버",
      status: "online",
      health: 98,
      cpu: 45,
      memory: 67,
      storage: 34,
      uptime: "247일",
      location: "데이터센터 1",
      lastMaintenance: "2025-05-15",
    },
    {
      id: "SYS-002",
      name: "데이터베이스 클러스터 BETA",
      type: "데이터베이스",
      status: "online",
      health: 95,
      cpu: 72,
      memory: 84,
      storage: 78,
      uptime: "189일",
      location: "데이터센터 2",
      lastMaintenance: "2025-06-01",
    },
    {
      id: "SYS-003",
      name: "보안 게이트웨이",
      type: "방화벽",
      status: "warning",
      health: 87,
      cpu: 23,
      memory: 45,
      storage: 12,
      uptime: "156일",
      location: "DMZ",
      lastMaintenance: "2025-04-20",
    },
    {
      id: "SYS-004",
      name: "통신 허브",
      type: "네트워크",
      status: "online",
      health: 92,
      cpu: 38,
      memory: 52,
      storage: 23,
      uptime: "203일",
      location: "네트워크 코어",
      lastMaintenance: "2025-05-28",
    },
    {
      id: "SYS-005",
      name: "백업 스토리지 어레이",
      type: "스토리지",
      status: "maintenance",
      health: 76,
      cpu: 15,
      memory: 28,
      storage: 89,
      uptime: "0일",
      location: "백업 시설",
      lastMaintenance: "2025-06-17",
    },
    {
      id: "SYS-006",
      name: "분석 엔진",
      type: "프로세싱",
      status: "online",
      health: 94,
      cpu: 89,
      memory: 76,
      storage: 45,
      uptime: "134일",
      location: "데이터센터 1",
      lastMaintenance: "2025-05-10",
    },
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case "online":
        return "bg-muted/50 text-foreground"
      case "warning":
        return "bg-yellow-500/20 text-amber-600"
      case "maintenance":
        return "bg-muted/50 text-muted-foreground"
      case "offline":
        return "bg-red-500/20 text-red-500"
      default:
        return "bg-muted/50 text-muted-foreground"
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case "online":
        return <CheckCircle className="w-4 h-4" />
      case "warning":
        return <AlertTriangle className="w-4 h-4" />
      case "maintenance":
        return <Settings className="w-4 h-4" />
      case "offline":
        return <AlertTriangle className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  const getSystemIcon = (type) => {
    switch (type) {
      case "주 서버":
        return <Server className="w-6 h-6" />
      case "데이터베이스":
        return <Database className="w-6 h-6" />
      case "방화벽":
        return <Shield className="w-6 h-6" />
      case "네트워크":
        return <Wifi className="w-6 h-6" />
      case "스토리지":
        return <HardDrive className="w-6 h-6" />
      case "프로세싱":
        return <Cpu className="w-6 h-6" />
      default:
        return <Server className="w-6 h-6" />
    }
  }

  const getHealthColor = (health) => {
    if (health >= 95) return "text-foreground"
    if (health >= 85) return "text-foreground"
    if (health >= 70) return "text-amber-600"
    return "text-red-500"
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-wider">시스템 모니터</h1>
          <p className="text-sm text-muted-foreground">인프라 상태 및 성능 모니터링</p>
        </div>
        <div className="flex gap-2">
          <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">시스템 스캔</Button>
          <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">유지보수 모드</Button>
        </div>
      </div>

      {/* System Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">온라인 시스템</p>
                <p className="text-2xl font-bold text-foreground font-mono">24/26</p>
              </div>
              <CheckCircle className="w-8 h-8 text-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">경고</p>
                <p className="text-2xl font-bold text-amber-600 font-mono">3</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">평균 가동 시간</p>
                <p className="text-2xl font-bold text-foreground font-mono">99.7%</p>
              </div>
              <Activity className="w-8 h-8 text-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">유지보수</p>
                <p className="text-2xl font-bold text-muted-foreground font-mono">1</p>
              </div>
              <Settings className="w-8 h-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Systems Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {systems.map((system) => (
          <Card
            key={system.id}
            className="bg-card border-border hover:border-yellow-500/50 transition-colors cursor-pointer"
            onClick={() => setSelectedSystem(system)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {getSystemIcon(system.type)}
                  <div>
                    <CardTitle className="text-sm font-bold text-foreground tracking-wider">{system.name}</CardTitle>
                    <p className="text-xs text-muted-foreground">{system.type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(system.status)}
                  <Badge className={getStatusColor(system.status)}>{system.status.toUpperCase()}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">시스템 상태</span>
                <span className={`text-sm font-bold font-mono ${getHealthColor(system.health)}`}>{system.health}%</span>
              </div>
              <Progress value={system.health} className="h-2" />

              <div className="grid grid-cols-3 gap-4 text-xs">
                <div>
                  <div className="text-muted-foreground mb-1">CPU</div>
                  <div className="text-foreground font-mono">{system.cpu}%</div>
                  <div className="w-full bg-muted/50 rounded-full h-1 mt-1">
                    <div
                      className="bg-yellow-500 h-1 rounded-full transition-all duration-300"
                      style={{ width: `${system.cpu}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">메모리</div>
                  <div className="text-foreground font-mono">{system.memory}%</div>
                  <div className="w-full bg-muted/50 rounded-full h-1 mt-1">
                    <div
                      className="bg-yellow-500 h-1 rounded-full transition-all duration-300"
                      style={{ width: `${system.memory}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">스토리지</div>
                  <div className="text-foreground font-mono">{system.storage}%</div>
                  <div className="w-full bg-muted/50 rounded-full h-1 mt-1">
                    <div
                      className="bg-yellow-500 h-1 rounded-full transition-all duration-300"
                      style={{ width: `${system.storage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="space-y-1 text-xs text-muted-foreground">
                <div className="flex justify-between">
                  <span>가동 시간:</span>
                  <span className="text-foreground font-mono">{system.uptime}</span>
                </div>
                <div className="flex justify-between">
                  <span>위치:</span>
                  <span className="text-foreground">{system.location}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* System Detail Modal */}
      {selectedSystem && (
        <div className="fixed inset-0 bg-muted/50 flex items-center justify-center p-4 z-50">
          <Card className="bg-card border-border w-full max-w-4xl max-h-[90vh] overflow-y-auto glass-scroll">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                {getSystemIcon(selectedSystem.type)}
                <div>
                  <CardTitle className="text-xl font-bold text-foreground tracking-wider">{selectedSystem.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {selectedSystem.id} • {selectedSystem.type}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                onClick={() => setSelectedSystem(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">시스템 상태</h3>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(selectedSystem.status)}
                      <Badge className={getStatusColor(selectedSystem.status)}>
                        {selectedSystem.status.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">시스템 정보</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">위치:</span>
                        <span className="text-foreground">{selectedSystem.location}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">가동 시간:</span>
                        <span className="text-foreground font-mono">{selectedSystem.uptime}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">최근 유지보수:</span>
                        <span className="text-foreground font-mono">{selectedSystem.lastMaintenance}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">상태 점수:</span>
                        <span className={`font-mono ${getHealthColor(selectedSystem.health)}`}>
                          {selectedSystem.health}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">리소스 사용량</h3>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">CPU 사용량</span>
                          <span className="text-foreground font-mono">{selectedSystem.cpu}%</span>
                        </div>
                        <div className="w-full bg-muted/50 rounded-full h-2">
                          <div
                            className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${selectedSystem.cpu}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">메모리 사용량</span>
                          <span className="text-foreground font-mono">{selectedSystem.memory}%</span>
                        </div>
                        <div className="w-full bg-muted/50 rounded-full h-2">
                          <div
                            className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${selectedSystem.memory}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">스토리지 사용량</span>
                          <span className="text-foreground font-mono">{selectedSystem.storage}%</span>
                        </div>
                        <div className="w-full bg-muted/50 rounded-full h-2">
                          <div
                            className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${selectedSystem.storage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t border-border">
                <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">시스템 재시작</Button>
                <Button
                  variant="outline"
                  className="border-border text-muted-foreground hover:bg-muted/50 hover:text-muted-foreground bg-transparent"
                >
                  로그 보기
                </Button>
                <Button
                  variant="outline"
                  className="border-border text-muted-foreground hover:bg-muted/50 hover:text-muted-foreground bg-transparent"
                >
                  유지보수 예약
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
