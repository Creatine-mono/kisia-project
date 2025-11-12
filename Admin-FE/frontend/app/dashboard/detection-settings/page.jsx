"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Save, RotateCcw, AlertCircle, CheckCircle2, Info } from "lucide-react"
import { fetchAllSettings, updateSetting } from "@/lib/api-client.settings"

export default function DetectionSettingsPage() {
  const [serverSettings, setServerSettings] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState(null)
  const [hasChanges, setHasChanges] = useState(false)
  const [originalSettings, setOriginalSettings] = useState([])

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const data = await fetchAllSettings()
      console.log('API 응답 전체:', data)
      console.log('API 응답 타입:', typeof data)
      console.log('settings 배열:', data?.settings)

      const settings = data?.settings || []
      console.log('최종 settings:', settings)
      console.log('settings 길이:', settings.length)

      if (settings.length > 0) {
        console.log('첫 번째 설정:', settings[0])
      }

      setServerSettings(settings)
      setOriginalSettings(JSON.parse(JSON.stringify(settings)))
      setHasChanges(false)

      if (settings.length === 0) {
        setSaveMessage({ type: 'info', text: 'API에서 설정 데이터를 받아오지 못했습니다.' })
      }
    } catch (error) {
      console.error('설정 로드 에러:', error)
      setSaveMessage({ type: 'error', text: `설정을 불러오는데 실패했습니다: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  // 설정 변경 핸들러
  const handleToggleEnabled = (id) => {
    setServerSettings(prev =>
      prev.map(setting =>
        setting.id === id ? { ...setting, enabled: !setting.enabled } : setting
      )
    )
    setHasChanges(true)
  }

  const handleThresholdChange = (id, value) => {
    setServerSettings(prev =>
      prev.map(setting =>
        setting.id === id ? { ...setting, threshold: parseInt(value) } : setting
      )
    )
    setHasChanges(true)
  }

  // 저장 핸들러
  const handleSave = async () => {
    setSaving(true)
    setSaveMessage(null)

    try {
      // 변경된 설정만 찾아서 업데이트
      const changedSettings = serverSettings.filter((setting, index) => {
        const original = originalSettings[index]
        return original && (
          setting.enabled !== original.enabled ||
          setting.threshold !== original.threshold
        )
      })

      if (changedSettings.length === 0) {
        setSaveMessage({ type: 'info', text: '변경된 설정이 없습니다.' })
        setSaving(false)
        return
      }

      // 모든 변경사항을 병렬로 업데이트
      await Promise.all(
        changedSettings.map(setting =>
          updateSetting(setting.entity_type, {
            enabled: setting.enabled,
            threshold: setting.threshold
          })
        )
      )

      setSaveMessage({ type: 'success', text: `${changedSettings.length}개 설정이 성공적으로 저장되었습니다.` })
      setHasChanges(false)

      // 저장 후 설정 다시 로드
      await loadSettings()

      // 3초 후 메시지 제거
      setTimeout(() => setSaveMessage(null), 3000)
    } catch (error) {
      setSaveMessage({ type: 'error', text: '설정 저장 중 오류가 발생했습니다.' })
    } finally {
      setSaving(false)
    }
  }

  // 초기화 핸들러
  const handleReset = () => {
    setServerSettings(JSON.parse(JSON.stringify(originalSettings)))
    setHasChanges(false)
    setSaveMessage({ type: 'info', text: '변경사항이 초기화되었습니다.' })
    setTimeout(() => setSaveMessage(null), 2000)
  }

  // 민감도 레벨 표시
  const getSensitivityLabel = (threshold) => {
    if (threshold >= 75) return { label: '높음', color: 'text-red-500' }
    if (threshold >= 40) return { label: '중간', color: 'text-yellow-500' }
    return { label: '낮음', color: 'text-green-500' }
  }

  return (
    <div className="p-6 space-y-6 bg-background">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-600 to-amber-700 bg-clip-text text-transparent">
            개인정보 탐지 설정
          </h1>
          <p className="text-sm text-muted-foreground mt-1">PII 엔티티별 탐지 활성화 및 민감도 설정</p>
        </div>
        <div className="flex gap-2 items-center">
          {hasChanges && (
            <span className="text-xs text-yellow-600 bg-yellow-600/10 px-3 py-2 rounded border border-yellow-600/20">
              저장되지 않은 변경사항이 있습니다
            </span>
          )}
          <button
            onClick={handleReset}
            disabled={!hasChanges || saving}
            className="px-4 py-2 bg-card/50 border border-border text-amber-600 rounded hover:bg-card transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RotateCcw className="w-4 h-4" />
            초기화
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            {saving ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>

      {/* Save Message */}
      {saveMessage && (
        <div className={`flex items-center gap-2 p-3 rounded border ${
          saveMessage.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-600' :
          saveMessage.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-600' :
          'bg-blue-500/10 border-blue-500/20 text-blue-600'
        }`}>
          {saveMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> :
           saveMessage.type === 'error' ? <AlertCircle className="w-4 h-4" /> :
           <Info className="w-4 h-4" />}
          <span className="text-sm">{saveMessage.text}</span>
        </div>
      )}

      {/* PII Settings */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold text-foreground">PII 탐지 설정</CardTitle>
              <p className="text-xs text-muted-foreground mt-1">
                각 개인정보 유형별로 탐지 활성화 여부와 민감도(0-100)를 설정할 수 있습니다.
              </p>
            </div>
            {!loading && serverSettings.length > 0 && (
              <div className="text-xs text-muted-foreground">
                총 {serverSettings.length}개 항목 / 활성화: {serverSettings.filter(s => s.enabled).length}개
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-sm text-muted-foreground">설정을 불러오는 중...</div>
            </div>
          ) : (
            <div className="space-y-3">
              {serverSettings.length === 0 ? (
                <div className="text-center py-8">
                  <AlertCircle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">설정 항목이 없습니다.</p>
                </div>
              ) : (
                serverSettings.map((setting) => {
                  const sensitivity = getSensitivityLabel(setting.threshold)
                  return (
                    <div
                      key={setting.id}
                      className={`p-4 rounded-lg border transition-all ${
                        setting.enabled
                          ? 'bg-muted/30 border-border hover:border-yellow-600/50'
                          : 'bg-muted/10 border-border/50 opacity-75'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        {/* Left: Entity Info */}
                        <div className="flex items-start gap-4 flex-1">
                          <label className="relative inline-flex items-center cursor-pointer mt-1">
                            <input
                              type="checkbox"
                              checked={setting.enabled}
                              onChange={() => handleToggleEnabled(setting.id)}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-muted rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-muted after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-600"></div>
                          </label>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="text-sm font-semibold text-foreground">{setting.entity_type}</h3>
                              <span className={`text-xs px-2 py-0.5 rounded ${sensitivity.color} bg-current/10`}>
                                {sensitivity.label}
                              </span>
                            </div>
                            {setting.description && (
                              <p className="text-xs text-muted-foreground">{setting.description}</p>
                            )}
                          </div>
                        </div>

                        {/* Right: Threshold Control */}
                        <div className="w-80">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-muted-foreground">탐지 민감도</span>
                            <span className="text-sm text-amber-600 font-mono font-semibold min-w-[3rem] text-right">
                              {setting.threshold}
                            </span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={setting.threshold}
                            onChange={(e) => handleThresholdChange(setting.id, e.target.value)}
                            disabled={!setting.enabled}
                            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed"
                          />
                          <div className="flex justify-between text-xs text-muted-foreground mt-1">
                            <span>0</span>
                            <span>50</span>
                            <span>100</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground tracking-wider">
            <Info className="w-4 h-4 inline mr-2" />
            설정 안내
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-xs text-muted-foreground">
            <div className="flex gap-2">
              <span className="text-amber-600">•</span>
              <span><strong>민감도 (Threshold):</strong> 0-100 사이의 값으로, 높을수록 더 엄격하게 탐지합니다.</span>
            </div>
            <div className="flex gap-2">
              <span className="text-amber-600">•</span>
              <span><strong>낮음 (0-39):</strong> 명확한 개인정보만 탐지합니다.</span>
            </div>
            <div className="flex gap-2">
              <span className="text-amber-600">•</span>
              <span><strong>중간 (40-74):</strong> 일반적인 탐지 수준입니다.</span>
            </div>
            <div className="flex gap-2">
              <span className="text-amber-600">•</span>
              <span><strong>높음 (75-100):</strong> 의심스러운 패턴도 적극적으로 탐지합니다.</span>
            </div>
            <div className="flex gap-2">
              <span className="text-amber-600">•</span>
              <span>설정 변경 후 반드시 <strong className="text-yellow-600">저장</strong> 버튼을 클릭해야 적용됩니다.</span>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  )
}
