"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { fetchOverview, fetchByIp, fetchTimeline, fetchByPiiType } from "@/lib/api-client.dashboard"
import { fetchLogs } from "@/lib/api-client.logs"

export default function CommandCenterPage() {
  const [overview, setOverview] = useState(null)
  const [ipStats, setIpStats] = useState([])
  const [timeline, setTimeline] = useState([])
  const [piiTypes, setPiiTypes] = useState([])
  const [recentLogs, setRecentLogs] = useState([])
  const [recent5mTotal, setRecent5mTotal] = useState(0)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const end = new Date()
        const start = new Date(end.getTime() - 60 * 60 * 1000)
        const startISO = start.toISOString()
        const endISO = end.toISOString()
        const fiveMinStart = new Date(end.getTime() - 5 * 60 * 1000)
        const fiveMinStartISO = fiveMinStart.toISOString()
        const [ov, byIp, tl, byType, logsResp, logs5m] = await Promise.all([
          fetchOverview(),
          fetchByIp({ size: 20 }),
          fetchTimeline({ interval: '1h' }),
          fetchByPiiType({}),
          fetchLogs({ start_date: startISO, end_date: endISO, page_size: 10, sort: 'timestamp:desc' }),
          fetchLogs({ start_date: fiveMinStartISO, end_date: endISO, page_size: 1, sort: 'timestamp:desc' }),
        ])
        if (!mounted) return
        setOverview(ov)
        setIpStats(byIp?.statistics || [])
        setTimeline(tl?.timeline || [])
        setPiiTypes(byType?.statistics || [])
        setRecentLogs(logsResp?.logs || [])
        setRecent5mTotal(logs5m?.total || 0)
      } catch (e) {
        // ignore
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  const timelinePath = useMemo(() => {
    if (!timeline.length) return ''
    const w = 500, h = 280, padLeft = 60, padRight = 80, padTop = 20, padBottom = 60
    const xs = timeline.map((_, i) => i)
    const ys = timeline.map(p => p.total_requests || 0)
    const maxY = Math.max(1, ...ys)
    const minX = 0, maxX = xs.length - 1 || 1
    const sx = (x) => padLeft + (x - minX) / (maxX - minX) * (w - padLeft - padRight)
    const sy = (y) => (h - padBottom) - (y / maxY) * (h - padTop - padBottom)
    return xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${sx(x)},${sy(ys[i])}`).join(' ')
  }, [timeline])

  return (
    <div className="p-6 space-y-6 bg-background">
      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Detection Stats Overview */}
        <Card className="lg:col-span-4 bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">개인정보 탐지 현황</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 mb-6">
              {piiTypes.slice(0, 3).map((t, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-2xl font-bold text-foreground font-mono">{t.count ?? '-'}</div>
                  <div className="text-xs text-muted-foreground">{t.pii_type}</div>
                </div>
              ))}
              {piiTypes.length === 0 && (
                <>
                  <div className="text-center"><div className="text-2xl font-bold text-foreground font-mono">-</div><div className="text-xs text-muted-foreground">-</div></div>
                  <div className="text-center"><div className="text-2xl font-bold text-foreground font-mono">-</div><div className="text-xs text-muted-foreground">-</div></div>
                  <div className="text-center"><div className="text-2xl font-bold text-foreground font-mono">-</div><div className="text-xs text-muted-foreground">-</div></div>
                </>
              )}
            </div>

            <div className="space-y-2">
              {piiTypes.slice(3, 7).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-muted/50 rounded hover:bg-muted transition-colors cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                    <div>
                      <div className="text-xs text-foreground">{item.pii_type}</div>
                      <div className="text-xs text-muted-foreground">{item.count}건 탐지</div>
                    </div>
                  </div>
                </div>
              ))}
              {piiTypes.length <= 3 && (
                <div className="text-xs text-muted-foreground">추가 데이터 없음</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Privacy Detection Chart */}
        <Card className="lg:col-span-4 bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">개인정보 탐지 현황</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center">
              <div className="mb-4 text-center">
                <div className="text-3xl font-bold text-foreground font-mono">{overview?.detected_requests ?? '-'}</div>
                <div className="text-xs text-muted-foreground">탐지된 요청</div>
              </div>
              <div className="w-full space-y-2">
                {piiTypes.slice(0, 6).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-muted/50 rounded hover:bg-yellow-900/30 transition-colors">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-sm bg-yellow-400"></div>
                      <span className="text-xs text-foreground">{item.pii_type}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground">{item.count}건</span>
                      <span className="text-sm font-bold text-foreground font-mono w-12 text-right">{Math.round((item.percentage ?? 0) * 100) / 100}%</span>
                    </div>
                  </div>
                ))}
                {piiTypes.length === 0 && (
                  <div className="text-xs text-muted-foreground">데이터가 없습니다.</div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Detections */}
        <Card className="lg:col-span-4 bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">
              실시간 탐지 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="bg-muted/50 p-3 rounded border border-yellow-500/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-muted-foreground font-semibold">실시간 모니터링</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-400 font-bold">ACTIVE</span>
                  </div>
                </div>
                <div className="text-2xl font-bold text-foreground font-mono">{recent5mTotal}</div>
                <div className="text-xs text-muted-foreground">최근 5분 내 요청</div>
              </div>

              <div className="bg-muted/50 p-3 rounded border border-yellow-500/20">
                <div className="text-xs text-muted-foreground mb-2">최근 탐지 항목 (최근 1시간)</div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {recentLogs.length === 0 ? (
                    <div className="text-xs text-muted-foreground">데이터가 없습니다.</div>
                  ) : recentLogs.map((log, idx) => (
                    <div key={idx} className="flex justify-between text-xs">
                      <span className="text-foreground truncate max-w-[65%]">{(log.entity_types || []).join(', ') || (log.has_pii ? 'DETECTED' : 'CLEAN')}</span>
                      <span className="text-muted-foreground font-mono">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quarterly Leak Chart */}
        <Card className="lg:col-span-8 bg-card border-border">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CardTitle className="text-base font-semibold text-foreground">
                  분기별 탐지 통계
                </CardTitle>
                <div className="flex items-center gap-4 ml-6">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span className="text-xs text-foreground font-medium">차단된 항목</span>
                    <span className="text-xs text-muted-foreground font-mono ml-1">501건</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-xs text-muted-foreground font-medium">개인정보 탐지</span>
                    <span className="text-xs text-muted-foreground font-mono ml-1">548건</span>
                  </div>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64 relative pt-4 pb-10 px-2">
              {/* Chart Grid - 더 미세하고 깔끔하게 */}
              <div className="absolute inset-0 flex flex-col justify-between ml-14 mr-6 mt-4 mb-12">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="border-t border-border opacity-30"></div>
                ))}
              </div>

              {/* Chart */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 500 280" preserveAspectRatio="none">
                <defs>
                  {/* Gradient for 차단된 항목 (Blue) */}
                  <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.6" />
                    <stop offset="70%" stopColor="#3b82f6" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                  </linearGradient>
                  {/* Gradient for 개인정보 탐지 (Yellow) */}
                  <linearGradient id="yellowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#eab308" stopOpacity="0.4" />
                    <stop offset="70%" stopColor="#eab308" stopOpacity="0.15" />
                    <stop offset="100%" stopColor="#eab308" stopOpacity="0" />
                  </linearGradient>
                </defs>

                {/* 타임라인 - 실데이터 경로 */}
                <path d={timelinePath} fill="none" stroke="#eab308" strokeWidth="2.5" strokeLinecap="round" vectorEffect="non-scaling-stroke" opacity="0.9" />
              </svg>

              {/* Y-axis labels */}
              <div className="absolute left-0 top-4 bottom-12 flex flex-col justify-between text-xs text-muted-foreground">
                <span>600</span>
                <span>500</span>
                <span>400</span>
                <span>300</span>
                <span>200</span>
                <span>100</span>
              </div>

              {/* X-axis labels - 더 깔끔하게 */}
              <div className="absolute bottom-0 left-14 right-6 flex justify-between text-xs text-muted-foreground">
                <span>Q1</span>
                <span>Q2</span>
                <span>Q3</span>
                <span>Q4</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* IP Statistics */}
        <Card className="lg:col-span-4 bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">IP별 통계</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-80 overflow-y-auto glass-scroll">
              {ipStats.map((s, index) => (
                <div key={index} className="bg-muted/50 p-3 rounded border border-yellow-500/20 hover:bg-yellow-900/30 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                      <span className="text-sm text-amber-600 font-mono">{s.client_ip}</span>
                    </div>
                    <div className="text-lg font-bold text-foreground font-mono">{s.total_requests}</div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-yellow-400" style={{ width: `${Math.min(100, (s.detected_requests / Math.max(1, s.total_requests)) * 100)}%` }}></div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">탐지 건수 비율</div>
                </div>
              ))}
              {ipStats.length === 0 && (
                <div className="text-xs text-muted-foreground">데이터가 없습니다.</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Label Statistics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">라벨 통계</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 hover:bg-yellow-900/20 transition-colors cursor-pointer">
                  <div className="text-xs text-muted-foreground mb-1">총 차단횟수</div>
                  <div className="text-2xl font-bold text-foreground font-mono">1,234</div>
                  <div className="text-xs text-green-400 mt-1">↑ 15% vs 지난주</div>
                </div>
                <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 hover:bg-yellow-900/20 transition-colors cursor-pointer">
                  <div className="text-xs text-muted-foreground mb-1">IP 별 통계</div>
                  <div className="text-2xl font-bold text-foreground font-mono">567</div>
                  <div className="text-xs text-muted-foreground mt-1">고유 IP 주소</div>
                </div>
              </div>

              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 hover:bg-yellow-900/20 transition-colors">
                <div className="text-xs text-muted-foreground mb-1">오늘 차단횟수</div>
                <div className="text-2xl font-bold text-amber-600 font-mono">89</div>
                <div className="w-full bg-muted rounded-full h-1.5 mt-2">
                  <div className="bg-yellow-400 h-1.5 rounded-full" style={{ width: "67%" }}></div>
                </div>
                <div className="text-xs text-muted-foreground mt-1">일일 목표의 67%</div>
              </div>

              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20">
                <div className="text-xs text-muted-foreground mb-2 flex items-center justify-between">
                  <span>최근 알림 (위협 감지)</span>
                  <span className="text-red-400 font-mono">LIVE</span>
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto glass-scroll">
                  {[
                    { time: "2025-06-08 09:45", ip: "192.168.1.100", threat: "주민등록번호 탐지", severity: "high" },
                    { time: "2025-06-08 09:30", ip: "10.0.0.55", threat: "신용카드번호 탐지", severity: "high" },
                    { time: "2025-06-08 09:15", ip: "172.16.0.99", threat: "전화번호 탐지", severity: "medium" },
                  ].map((alert, idx) => (
                    <div key={idx} className="text-xs border-l-2 border-red-500 pl-2 hover:bg-yellow-900/20 rounded transition-colors p-1">
                      <div className="flex items-center justify-between">
                        <div className="text-muted-foreground font-mono">{alert.time}</div>
                        <div className={`w-2 h-2 rounded-full ${alert.severity === 'high' ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse`}></div>
                      </div>
                      <div className="text-foreground">
                        <span className="text-amber-600">{alert.ip}</span> - {alert.threat}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">
              시간, 전체 프로젝트, 탐지된 내역
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20">
                <div className="text-xs text-muted-foreground mb-2">상단 필터링 검색 기능</div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="검색..."
                    className="flex-1 bg-muted/50 border border-yellow-500/30 rounded px-3 py-2 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-yellow-400"
                  />
                  <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white text-sm rounded transition-colors">
                    검색
                  </button>
                </div>
              </div>

              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20">
                <div className="text-xs text-muted-foreground mb-2">정렬 기능</div>
                <div className="space-y-2 max-h-60 overflow-y-auto glass-scroll">
                  {[
                    { project: "고객관리시스템", time: "2025-06-08 09:50", detected: "전화번호", count: 15 },
                    { project: "의료기록시스템", time: "2025-06-08 09:40", detected: "주민등록번호", count: 8 },
                    { project: "전자상거래플랫폼", time: "2025-06-08 09:35", detected: "신용카드", count: 12 },
                    { project: "인사관리시스템", time: "2025-06-08 09:20", detected: "이메일", count: 45 },
                    { project: "교육플랫폼", time: "2025-06-08 09:10", detected: "계좌번호", count: 3 },
                  ].map((item, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center p-2 bg-muted/30 rounded hover:bg-yellow-900/30 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="text-xs text-amber-600 font-mono">{item.project}</div>
                        <div className="text-xs text-muted-foreground">{item.time}</div>
                      </div>
                      <div className="text-xs text-foreground">{item.detected}</div>
                      <div className="text-sm font-bold text-red-400 ml-4">{item.count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">라벨별 차단 여부</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[
                { label: "전화번호", blocked: 234, allowed: 12 },
                { label: "주민등록번호", blocked: 189, allowed: 8 },
                { label: "신용카드", blocked: 145, allowed: 5 },
                { label: "계좌번호", blocked: 98, allowed: 3 },
              ].map((item, idx) => (
                <div key={idx} className="bg-muted/50 p-3 rounded border border-yellow-500/20">
                  <div className="text-xs text-foreground mb-2">{item.label}</div>
                  <div className="flex justify-between text-xs">
                    <span className="text-red-400">차단: {item.blocked}</span>
                    <span className="text-green-400">허용: {item.allowed}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-foreground">요약 통계</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 text-center">
                <div className="text-xs text-muted-foreground mb-1">총 요청</div>
                <div className="text-2xl font-bold text-foreground font-mono">{overview?.total_requests ?? '-'}</div>
              </div>
              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 text-center">
                <div className="text-xs text-muted-foreground mb-1">탐지됨</div>
                <div className="text-2xl font-bold text-amber-600 font-mono">{overview?.detected_requests ?? '-'}</div>
              </div>
              <div className="bg-muted/50 p-4 rounded border border-yellow-500/20 text-center">
                <div className="text-xs text-muted-foreground mb-1">차단됨</div>
                <div className="text-2xl font-bold text-red-400 font-mono">{overview?.blocked_requests ?? '-'}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI 서비스별 카드 제거됨 */}
      </div>
    </div>
  )
}
