"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, FileText, Eye, Download, Filter, Globe, Shield, AlertTriangle } from "lucide-react"

export default function IntelligencePage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedReport, setSelectedReport] = useState(null)

  const reports = [
    {
      id: "INT-2025-001",
      title: "CYBERCRIME NETWORK ANALYSIS",
      classification: "TOP SECRET",
      source: "SIGINT",
      location: "Eastern Europe",
      date: "2025-06-17",
      status: "verified",
      threat: "high",
      summary: "Detailed analysis of emerging cybercrime syndicate operating across multiple jurisdictions",
      tags: ["cybercrime", "international", "financial"],
    },
    {
      id: "INT-2025-002",
      title: "ROGUE AGENT COMMUNICATIONS",
      classification: "SECRET",
      source: "HUMINT",
      location: "Berlin",
      date: "2025-06-16",
      status: "pending",
      threat: "critical",
      summary: "Intercepted communications suggesting potential security breach in European operations",
      tags: ["internal", "security", "communications"],
    },
    {
      id: "INT-2025-003",
      title: "ARMS TRAFFICKING ROUTES",
      classification: "CONFIDENTIAL",
      source: "OSINT",
      location: "Middle East",
      date: "2025-06-15",
      status: "verified",
      threat: "medium",
      summary: "Updated intelligence on weapons smuggling corridors through Mediterranean region",
      tags: ["trafficking", "weapons", "maritime"],
    },
    {
      id: "INT-2025-004",
      title: "TERRORIST CELL SURVEILLANCE",
      classification: "TOP SECRET",
      source: "HUMINT",
      location: "North Africa",
      date: "2025-06-14",
      status: "active",
      threat: "critical",
      summary: "Ongoing surveillance of suspected terrorist cell planning coordinated attacks",
      tags: ["terrorism", "surveillance", "coordinated"],
    },
    {
      id: "INT-2025-005",
      title: "DIPLOMATIC INTELLIGENCE BRIEF",
      classification: "SECRET",
      source: "DIPLOMATIC",
      location: "Asia Pacific",
      date: "2025-06-13",
      status: "verified",
      threat: "low",
      summary: "Political developments affecting regional security and operational considerations",
      tags: ["diplomatic", "political", "regional"],
    },
  ]

  const getClassificationColor = (classification) => {
    switch (classification) {
      case "TOP SECRET":
        return "bg-red-500/20 text-red-500"
      case "SECRET":
        return "bg-yellow-500/20 text-amber-600"
      case "CONFIDENTIAL":
        return "bg-muted/50 text-muted-foreground"
      default:
        return "bg-muted/50 text-foreground"
    }
  }

  const getThreatColor = (threat) => {
    switch (threat) {
      case "critical":
        return "bg-red-500/20 text-red-500"
      case "high":
        return "bg-yellow-500/20 text-amber-600"
      case "medium":
        return "bg-muted/50 text-muted-foreground"
      case "low":
        return "bg-muted/50 text-foreground"
      default:
        return "bg-muted/50 text-muted-foreground"
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case "verified":
        return "bg-muted/50 text-foreground"
      case "pending":
        return "bg-yellow-500/20 text-amber-600"
      case "active":
        return "bg-muted/50 text-foreground"
      default:
        return "bg-muted/50 text-muted-foreground"
    }
  }

  const filteredReports = reports.filter(
    (report) =>
      report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase())),
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-wider">INTELLIGENCE CENTER</h1>
          <p className="text-sm text-muted-foreground">Classified reports and threat analysis</p>
        </div>
        <div className="flex gap-2">
          <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">New Report</Button>
          <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      {/* Stats and Search */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <Card className="lg:col-span-2 bg-card border-border">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search intelligence reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-muted/50 border-border text-foreground placeholder-muted-foreground"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">TOTAL REPORTS</p>
                <p className="text-2xl font-bold text-foreground font-mono">1,247</p>
              </div>
              <FileText className="w-8 h-8 text-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">CRITICAL THREATS</p>
                <p className="text-2xl font-bold text-red-500 font-mono">12</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground tracking-wider">ACTIVE SOURCES</p>
                <p className="text-2xl font-bold text-foreground font-mono">89</p>
              </div>
              <Globe className="w-8 h-8 text-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Intelligence Reports */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground tracking-wider">INTELLIGENCE REPORTS</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="border border-border rounded p-4 hover:border-yellow-500/50 transition-colors cursor-pointer"
                onClick={() => setSelectedReport(report)}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start gap-3">
                      <FileText className="w-5 h-5 text-muted-foreground mt-0.5" />
                      <div className="flex-1">
                        <h3 className="text-sm font-bold text-foreground tracking-wider">{report.title}</h3>
                        <p className="text-xs text-muted-foreground font-mono">{report.id}</p>
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground ml-8">{report.summary}</p>

                    <div className="flex flex-wrap gap-2 ml-8">
                      {report.tags.map((tag) => (
                        <Badge key={tag} className="bg-muted/50 text-muted-foreground text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col sm:items-end gap-2">
                    <div className="flex flex-wrap gap-2">
                      <Badge className={getClassificationColor(report.classification)}>{report.classification}</Badge>
                      <Badge className={getThreatColor(report.threat)}>{report.threat.toUpperCase()}</Badge>
                      <Badge className={getStatusColor(report.status)}>{report.status.toUpperCase()}</Badge>
                    </div>

                    <div className="text-xs text-muted-foreground space-y-1">
                      <div className="flex items-center gap-2">
                        <Globe className="w-3 h-3" />
                        <span>{report.location}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Shield className="w-3 h-3" />
                        <span>{report.source}</span>
                      </div>
                      <div className="font-mono">{report.date}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Report Detail Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-muted/50 flex items-center justify-center p-4 z-50">
          <Card className="bg-card border-border w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-foreground tracking-wider">{selectedReport.title}</CardTitle>
                <p className="text-sm text-muted-foreground font-mono">{selectedReport.id}</p>
              </div>
              <Button
                variant="ghost"
                onClick={() => setSelectedReport(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">CLASSIFICATION</h3>
                    <div className="flex gap-2">
                      <Badge className={getClassificationColor(selectedReport.classification)}>
                        {selectedReport.classification}
                      </Badge>
                      <Badge className={getThreatColor(selectedReport.threat)}>
                        THREAT: {selectedReport.threat.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">SOURCE DETAILS</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Source Type:</span>
                        <span className="text-foreground font-mono">{selectedReport.source}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Location:</span>
                        <span className="text-foreground">{selectedReport.location}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Date:</span>
                        <span className="text-foreground font-mono">{selectedReport.date}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <Badge className={getStatusColor(selectedReport.status)}>
                          {selectedReport.status.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">TAGS</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.tags.map((tag) => (
                        <Badge key={tag} className="bg-muted/50 text-muted-foreground">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">THREAT ASSESSMENT</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Threat Level</span>
                        <Badge className={getThreatColor(selectedReport.threat)}>
                          {selectedReport.threat.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="w-full bg-muted/50 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            selectedReport.threat === "critical"
                              ? "bg-red-500 w-full"
                              : selectedReport.threat === "high"
                                ? "bg-yellow-500 w-3/4"
                                : selectedReport.threat === "medium"
                                  ? "bg-muted w-1/2"
                                  : "bg-foreground w-1/4"
                          }`}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-muted-foreground tracking-wider mb-2">EXECUTIVE SUMMARY</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{selectedReport.summary}</p>
              </div>

              <div className="flex gap-2 pt-4 border-t border-border">
                <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">
                  <Eye className="w-4 h-4 mr-2" />
                  View Full Report
                </Button>
                <Button
                  variant="outline"
                  className="border-border text-muted-foreground hover:bg-muted/50 hover:text-muted-foreground bg-transparent"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button
                  variant="outline"
                  className="border-border text-muted-foreground hover:bg-muted/50 hover:text-muted-foreground bg-transparent"
                >
                  Share Intel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
