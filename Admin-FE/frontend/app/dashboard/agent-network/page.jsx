"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Filter, MoreHorizontal, Edit, Trash2, Plus, AlertTriangle } from "lucide-react"

export default function AgentNetworkPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedProject, setSelectedProject] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)

  const projects = [
    {
      id: "PRJ-001",
      name: "고객관리시스템",
      status: "active",
      fileName: "customer_data.json",
      fileSize: "2.4 MB",
      detections: 245,
      lastActivity: "2 min ago",
      alerts: 3,
      risk: "high",
      contextRules: [1, 5], // 선택된 맥락 탐지 규칙 ID
    },
    {
      id: "PRJ-002",
      name: "의료기록시스템",
      status: "active",
      fileName: "medical_records.csv",
      fileSize: "5.8 MB",
      detections: 187,
      lastActivity: "15 min ago",
      alerts: 8,
      risk: "critical",
      contextRules: [1, 6],
    },
    {
      id: "PRJ-003",
      name: "전자상거래플랫폼",
      status: "active",
      fileName: "ecommerce_logs.txt",
      fileSize: "3.2 MB",
      detections: 412,
      lastActivity: "1 min ago",
      alerts: 2,
      risk: "medium",
      contextRules: [2, 5],
    },
    {
      id: "PRJ-004",
      name: "금융거래시스템",
      status: "paused",
      fileName: "transaction_data.xlsx",
      fileSize: "1.7 MB",
      detections: 89,
      lastActivity: "3 hours ago",
      alerts: 0,
      risk: "low",
      contextRules: [2],
    },
    {
      id: "PRJ-005",
      name: "인사관리시스템",
      status: "active",
      fileName: "employee_info.json",
      fileSize: "890 KB",
      detections: 156,
      lastActivity: "5 min ago",
      alerts: 1,
      risk: "medium",
      contextRules: [4],
    },
    {
      id: "PRJ-006",
      name: "교육플랫폼",
      status: "active",
      fileName: "student_records.csv",
      fileSize: "4.1 MB",
      detections: 298,
      lastActivity: "8 min ago",
      alerts: 5,
      risk: "high",
      contextRules: [5, 7],
    },
  ]

  // 맥락 탐지 규칙 목록
  const contextRules = [
    { id: 1, name: "의료 정보 관련 맥락", category: "산업별" },
    { id: 2, name: "금융 정보 관련 맥락", category: "산업별" },
    { id: 3, name: "계약서 및 법률 문서", category: "문서 유형" },
    { id: 4, name: "인사 정보 관련 맥락", category: "산업별" },
    { id: 5, name: "고객 상담 기록", category: "문서 유형" },
    { id: 6, name: "진단 및 처방 기록", category: "산업별" },
    { id: 7, name: "교육 및 평가 자료", category: "산업별" },
    { id: 8, name: "거래 내역서", category: "문서 유형" },
    { id: 9, name: "회의록 및 메모", category: "문서 유형" },
    { id: 10, name: "이메일 및 메시지", category: "문서 유형" },
  ]

  const filteredProjects = projects.filter(
    (project) =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.id.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="p-6 space-y-6 bg-background">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-600 to-amber-700 bg-clip-text text-transparent">
            프로젝트 관리
          </h1>
          <p className="text-sm text-muted-foreground">가입된 프로젝트 관리 및 모니터링</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setShowAddModal(true)}
            className="bg-yellow-600 hover:bg-yellow-500 text-white flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            새 프로젝트 추가
          </Button>
          <Button className="bg-yellow-900/30 border border-yellow-500/30 text-amber-600 hover:bg-yellow-900/50">
            <Filter className="w-4 h-4 mr-2" />
            필터
          </Button>
        </div>
      </div>

      {/* Search and Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-1 bg-card border-border">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="프로젝트 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-muted/50 border-yellow-500/20 text-foreground placeholder-muted-foreground"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">활성 프로젝트</p>
                <p className="text-2xl font-bold text-foreground font-mono">5</p>
              </div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-red-900/20 border-red-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">경고 알림</p>
                <p className="text-2xl font-bold text-red-400 font-mono">19</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">총 탐지 건수</p>
                <p className="text-2xl font-bold text-amber-600 font-mono">1,387</p>
              </div>
              <div className="text-xs text-green-400">↑ 23%</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Project List */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground tracking-wider">프로젝트 목록</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-yellow-500/30">
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">프로젝트 ID</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">프로젝트명</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">상태</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">탐지 건수</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">알림</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">위험도</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground tracking-wider">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredProjects.map((project, index) => (
                  <tr
                    key={project.id}
                    className={`border-b border-border hover:bg-yellow-900/30 transition-colors ${
                      index % 2 === 0 ? "bg-muted/30" : "bg-muted/50"
                    }`}
                  >
                    <td className="py-3 px-4 text-sm text-amber-600 font-mono">{project.id}</td>
                    <td className="py-3 px-4 text-sm text-foreground font-medium">{project.name}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            project.status === "active" ? "bg-green-400 animate-pulse" : "bg-muted"
                          }`}
                        ></div>
                        <span className="text-xs text-muted-foreground">
                          {project.status === "active" ? "활성" : "일시정지"}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-foreground font-mono">{project.detections}</td>
                    <td className="py-3 px-4">
                      {project.alerts > 0 ? (
                        <div className="flex items-center gap-1">
                          <AlertTriangle className="w-4 h-4 text-red-400" />
                          <span className="text-xs text-red-400 font-bold">{project.alerts}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          project.risk === "critical"
                            ? "bg-red-500/20 text-red-400"
                            : project.risk === "high"
                              ? "bg-yellow-500/20 text-amber-600"
                              : project.risk === "medium"
                                ? "bg-blue-500/20 text-blue-400"
                                : "bg-green-500/20 text-green-400"
                        }`}
                      >
                        {project.risk === "critical"
                          ? "위험"
                          : project.risk === "high"
                            ? "높음"
                            : project.risk === "medium"
                              ? "중간"
                              : "낮음"}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-muted-foreground hover:text-amber-600 h-8 w-8"
                          onClick={() => setSelectedProject(project)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-red-400 h-8 w-8">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Project Edit Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-background/70 flex items-center justify-center p-4 z-50">
          <Card className="bg-card border-border w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="flex flex-row items-center justify-between border-b border-border sticky top-0 bg-card z-10">
              <div>
                <CardTitle className="text-lg font-bold text-foreground">{selectedProject.name}</CardTitle>
                <p className="text-sm text-muted-foreground font-mono">{selectedProject.id}</p>
              </div>
              <Button
                variant="ghost"
                onClick={() => setSelectedProject(null)}
                className="text-muted-foreground hover:text-foreground h-8 w-8 p-0"
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-muted-foreground tracking-wider mb-2 block">프로젝트명</label>
                  <Input
                    defaultValue={selectedProject.name}
                    className="bg-muted/50 border-yellow-500/30 text-foreground"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-muted-foreground tracking-wider mb-2 block">상태</label>
                    <select className="w-full bg-muted/50 border border-yellow-500/30 rounded px-3 py-2 text-sm text-foreground focus:outline-none focus:border-yellow-400">
                      <option value="active">활성</option>
                      <option value="paused">일시정지</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground tracking-wider mb-2 block">위험도</label>
                    <span
                      className={`inline-block text-xs px-3 py-2 rounded ${
                        selectedProject.risk === "critical"
                          ? "bg-red-500/20 text-red-400"
                          : selectedProject.risk === "high"
                            ? "bg-yellow-500/20 text-amber-600"
                            : selectedProject.risk === "medium"
                              ? "bg-blue-500/20 text-blue-400"
                              : "bg-green-500/20 text-green-400"
                      }`}
                    >
                      {selectedProject.risk === "critical"
                        ? "위험"
                        : selectedProject.risk === "high"
                          ? "높음"
                          : selectedProject.risk === "medium"
                            ? "중간"
                            : "낮음"}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-muted/50 p-3 rounded border border-yellow-500/20">
                    <div className="text-xs text-muted-foreground mb-1">총 탐지 건수</div>
                    <div className="text-xl font-bold text-foreground font-mono">{selectedProject.detections}</div>
                  </div>
                  <div className="bg-muted/50 p-3 rounded border border-yellow-500/20">
                    <div className="text-xs text-muted-foreground mb-1">알림 수</div>
                    <div className="text-xl font-bold text-red-400 font-mono">{selectedProject.alerts}</div>
                  </div>
                </div>

                {/* 맥락 탐지 규칙 설정 */}
                <div className="bg-muted/50 p-4 rounded border border-yellow-500/20">
                  <div className="flex items-center justify-between mb-3">
                    <label className="text-sm text-foreground font-medium">맥락 탐지 규칙</label>
                    <span className="text-xs text-muted-foreground">
                      {selectedProject.contextRules?.length || 0}개 선택됨
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">
                    이 프로젝트에 적용할 맥락 기반 탐지 규칙을 선택하세요.
                  </p>

                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {/* 산업별 규칙 */}
                    <div>
                      <div className="text-xs text-amber-600 font-medium mb-2">산업별 규칙</div>
                      <div className="space-y-2">
                        {contextRules
                          .filter((rule) => rule.category === "산업별")
                          .map((rule) => (
                            <label
                              key={rule.id}
                              className="flex items-center gap-3 p-2 bg-muted/30 rounded hover:bg-yellow-900/20 cursor-pointer transition-colors"
                            >
                              <input
                                type="checkbox"
                                defaultChecked={selectedProject.contextRules?.includes(rule.id)}
                                className="w-4 h-4 rounded border-yellow-500/30 bg-muted/50 text-yellow-600 focus:ring-yellow-500 focus:ring-offset-0"
                              />
                              <span className="text-sm text-foreground">{rule.name}</span>
                            </label>
                          ))}
                      </div>
                    </div>

                    {/* 문서 유형별 규칙 */}
                    <div>
                      <div className="text-xs text-amber-600 font-medium mb-2">문서 유형별 규칙</div>
                      <div className="space-y-2">
                        {contextRules
                          .filter((rule) => rule.category === "문서 유형")
                          .map((rule) => (
                            <label
                              key={rule.id}
                              className="flex items-center gap-3 p-2 bg-muted/30 rounded hover:bg-yellow-900/20 cursor-pointer transition-colors"
                            >
                              <input
                                type="checkbox"
                                defaultChecked={selectedProject.contextRules?.includes(rule.id)}
                                className="w-4 h-4 rounded border-yellow-500/30 bg-muted/50 text-yellow-600 focus:ring-yellow-500 focus:ring-offset-0"
                              />
                              <span className="text-sm text-foreground">{rule.name}</span>
                            </label>
                          ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 pt-4 border-t border-yellow-500/30">
                <Button className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white">
                  <Edit className="w-4 h-4 mr-2" />
                  저장
                </Button>
                <Button
                  variant="outline"
                  className="border-yellow-500/30 text-muted-foreground hover:bg-yellow-900/30 hover:text-foreground bg-transparent"
                  onClick={() => setSelectedProject(null)}
                >
                  취소
                </Button>
                <Button variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-900/30 bg-transparent">
                  <Trash2 className="w-4 h-4 mr-2" />
                  삭제
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Add Project Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-background/70 flex items-center justify-center p-4 z-50">
          <Card className="bg-card border-border w-full max-w-2xl">
            <CardHeader className="flex flex-row items-center justify-between border-b border-border">
              <div>
                <CardTitle className="text-lg font-bold text-foreground">새 프로젝트 추가</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">프로젝트 정보를 입력하고 설정 파일을 업로드하세요</p>
              </div>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowAddModal(false)
                  setUploadedFile(null)
                }}
                className="text-muted-foreground hover:text-foreground h-8 w-8 p-0"
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-muted-foreground tracking-wider mb-2 block">프로젝트명 *</label>
                  <Input
                    placeholder="프로젝트 이름을 입력하세요"
                    className="bg-muted/50 border-yellow-500/30 text-foreground"
                  />
                </div>

                <div>
                  <label className="text-xs text-muted-foreground tracking-wider mb-2 block">프로젝트 설명</label>
                  <textarea
                    placeholder="프로젝트에 대한 간단한 설명을 입력하세요"
                    className="w-full bg-muted/50 border border-yellow-500/30 rounded px-3 py-2 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-yellow-400 min-h-20"
                  />
                </div>

                <div>
                  <label className="text-xs text-muted-foreground tracking-wider mb-2 block">프로젝트 유형 *</label>
                  <select className="w-full bg-muted/50 border border-yellow-500/30 rounded px-3 py-2 text-sm text-foreground focus:outline-none focus:border-yellow-400">
                    <option value="">선택하세요</option>
                    <option value="customer">고객관리시스템</option>
                    <option value="medical">의료기록시스템</option>
                    <option value="ecommerce">전자상거래플랫폼</option>
                    <option value="finance">금융거래시스템</option>
                    <option value="hr">인사관리시스템</option>
                    <option value="education">교육플랫폼</option>
                    <option value="other">기타</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs text-muted-foreground tracking-wider mb-2 block">설정 파일 업로드</label>
                  <div className="bg-muted/50 border-2 border-dashed border-yellow-500/30 rounded p-6 text-center hover:border-yellow-400 transition-colors">
                    <input
                      type="file"
                      id="file-upload"
                      accept=".json,.yaml,.yml,.config"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setUploadedFile(e.target.files[0])
                        }
                      }}
                      className="hidden"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      {uploadedFile ? (
                        <div className="space-y-2">
                          <div className="text-sm text-foreground">✓ {uploadedFile.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {(uploadedFile.size / 1024).toFixed(2)} KB
                          </div>
                          <button
                            onClick={(e) => {
                              e.preventDefault()
                              setUploadedFile(null)
                            }}
                            className="text-xs text-red-400 hover:text-red-300"
                          >
                            파일 제거
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <div className="text-amber-600 text-3xl">📁</div>
                          <div className="text-sm text-foreground">클릭하여 파일 선택</div>
                          <div className="text-xs text-muted-foreground">
                            JSON, YAML, Config 파일 지원
                          </div>
                        </div>
                      )}
                    </label>
                  </div>
                </div>

              </div>

              <div className="flex gap-2 pt-4 border-t border-yellow-500/30">
                <Button className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  프로젝트 생성
                </Button>
                <Button
                  variant="outline"
                  className="border-yellow-500/30 text-muted-foreground hover:bg-yellow-900/30 hover:text-foreground bg-transparent"
                  onClick={() => {
                    setShowAddModal(false)
                    setUploadedFile(null)
                  }}
                >
                  취소
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
