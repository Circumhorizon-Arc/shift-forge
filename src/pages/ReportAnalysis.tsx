import React, { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Sparkles,
  Download,
  Share2,
  FileText,
  Building,
  CheckCircle2,
  Clock,
  Printer,
  Copy,
  Info,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Modal } from '../components/ui/Modal'
import { Skeleton } from '../components/ui/Skeleton'
import { ReportSummary } from '../components/reports/ReportSummary'
import { FindingCard } from '../components/reports/FindingCard'
import { DoctorQuestions } from '../components/reports/DoctorQuestions'
import { MedicalDisclaimer } from '../components/reports/MedicalDisclaimer'
import { reportService } from '../services/reportService'
import { ReportAnalysis } from '../types'
import { useToast } from '../context/ToastContext'

export const ReportAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { success } = useToast()

  const [analysis, setAnalysis] = useState<ReportAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [shareModalOpen, setShareModalOpen] = useState(false)
  const [copiedLink, setCopiedLink] = useState(false)

  useEffect(() => {
    let mounted = true
    const loadAnalysis = async () => {
      setIsLoading(true)
      try {
        const data = await reportService.getReportAnalysis(id || 'rep-001')
        if (mounted) {
          setAnalysis(data)
        }
      } catch (err) {
        console.error('Failed to load analysis', err)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    loadAnalysis()
    return () => {
      mounted = false
    }
  }, [id])

  const handleDownloadSummary = () => {
    if (!analysis) return

    // Generate formatted educational report text
    const text = [
      `HEALTH SENSE — CLINICAL REPORT EXPLANATION`,
      `Report: ${analysis.reportName}`,
      `Date: ${analysis.reportDate}`,
      `Facility: ${analysis.labName || 'Diagnostic Facility'}`,
      `Generated: ${analysis.analyzedAt || 'Recent'}`,
      `==================================================`,
      `\nPLAIN-LANGUAGE SUMMARY:`,
      analysis.summary,
      `\n==================================================`,
      `\nKEY EXTRACTED FINDINGS:`,
      ...analysis.findings.map(
        (f) =>
          `• ${f.testName}: ${f.value} ${f.unit} (Reference: ${f.referenceRange || 'N/A'}) [${
            f.interpretation === 'within-range' ? 'Within Range' : 'Outside Reference Range'
          }]`
      ),
      `\n==================================================`,
      `\nAI-GENERATED EDUCATIONAL EXPLANATIONS:`,
      ...analysis.explanations.map((exp, i) => `${i + 1}. ${exp}`),
      `\n==================================================`,
      `\nQUESTIONS TO DISCUSS WITH YOUR HEALTHCARE PROFESSIONAL:`,
      ...analysis.doctorQuestions.map((q, i) => `[ ] ${i + 1}. ${q}`),
      `\n==================================================`,
      `\nIMPORTANT HEALTHCARE NOTICE:`,
      analysis.disclaimer,
    ].join('\n')

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `HealthSense_Summary_${analysis.reportId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    success('Educational summary downloaded successfully.')
  }

  const handlePrint = () => {
    window.print()
  }

  const copyShareableLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopiedLink(true)
      success('Link copied to clipboard!')
      setTimeout(() => setCopiedLink(false), 2000)
    } catch {
      // fallback
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-8">
        <div className="flex items-center gap-3">
          <Skeleton className="h-6 w-24 rounded-lg" />
          <Skeleton className="h-6 w-36 rounded-lg" />
        </div>
        <Skeleton className="h-32 w-full rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-44 rounded-2xl" />
          <Skeleton className="h-44 rounded-2xl" />
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="text-center py-16 space-y-4 max-w-md mx-auto">
        <h3 className="text-xl font-bold text-slate-900">Analysis Not Found</h3>
        <p className="text-sm text-slate-500">
          The requested medical report analysis could not be retrieved.
        </p>
        <Button variant="primary" onClick={() => navigate('/reports')}>
          Back to Reports
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in pb-16 max-w-5xl mx-auto">
      {/* Top Breadcrumb & Action Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80">
        <div className="space-y-1">
          <Link
            to="/reports"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Reports</span>
          </Link>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-950 tracking-tight">
              {analysis.reportName}
            </h1>
            <Badge variant="success" size="md">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>AI Analysis Ready</span>
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
            <span>Report Date: {analysis.reportDate}</span>
            {analysis.labName && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Building className="w-3 h-3 text-slate-400" />
                  {analysis.labName}
                </span>
              </>
            )}
            {analysis.analyzedAt && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  Parsed at {analysis.analyzedAt}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start sm:self-auto flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrint}
            leftIcon={<Printer className="w-4 h-4 text-slate-500" />}
            title="Print report explanation"
          >
            Print
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadSummary}
            leftIcon={<Download className="w-4 h-4 text-slate-500" />}
            title="Download formatted clinical explanation"
          >
            Download Summary
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShareModalOpen(true)}
            leftIcon={<Share2 className="w-4 h-4" />}
          >
            Share with Doctor
          </Button>
        </div>
      </div>

      {/* SECTION 5 (Prominent Safety Notice at top) */}
      <MedicalDisclaimer />

      {/* SECTION 1 — SUMMARY */}
      <section>
        <ReportSummary
          summary={analysis.summary}
          extractedFactsCount={analysis.findings.length}
          labName={analysis.labName}
          reportDate={analysis.reportDate}
        />
      </section>

      {/* SECTION 2 — KEY FINDINGS */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <FileText className="w-5 h-5 text-sky-600" />
              <span>Key Extracted Findings</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Numerical values and intervals accurately parsed from your original lab document.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold">
            <span className="flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              {analysis.findings.filter((f) => f.interpretation === 'within-range').length} In Reference
            </span>
            <span className="flex items-center gap-1 text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              {analysis.findings.filter((f) => f.interpretation === 'outside-range').length} Outside Reference
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysis.findings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} />
          ))}
        </div>
      </section>

      {/* SECTION 3 — WHAT DOES THIS MEAN? */}
      <section className="space-y-4">
        <Card className="p-6">
          <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-slate-100 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                <Info className="w-4 h-4" />
              </div>
              <div>
                <CardTitle>What Does This Mean?</CardTitle>
                <span className="text-[11px] text-slate-500">
                  Contextual insights explained in plain, accessible terms
                </span>
              </div>
            </div>

            <Badge variant="primary" size="sm" className="self-start sm:self-auto bg-teal-50 text-teal-800 border-teal-200">
              <Sparkles className="w-3 h-3 text-teal-600" />
              <span>AI-generated educational explanation</span>
            </Badge>
          </CardHeader>

          <div className="space-y-3.5">
            {analysis.explanations.map((explanation, index) => (
              <div
                key={index}
                className="p-4 rounded-xl bg-slate-50/70 border border-slate-100 flex items-start gap-3.5"
              >
                <div className="w-6 h-6 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                  {index + 1}
                </div>
                <p className="text-sm text-slate-700 leading-relaxed font-normal">
                  {explanation}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      {/* SECTION 4 — QUESTIONS TO ASK YOUR DOCTOR */}
      <section>
        <DoctorQuestions questions={analysis.doctorQuestions} />
      </section>

      {/* BOTTOM ACTIONS BAR */}
      <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
        <Link to="/reports">
          <Button variant="outline" size="md" leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Back to Medical Reports
          </Button>
        </Link>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Button
            variant="outline"
            size="md"
            onClick={handleDownloadSummary}
            leftIcon={<Download className="w-4 h-4" />}
            className="flex-1 sm:flex-initial"
          >
            Download Summary
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => setShareModalOpen(true)}
            leftIcon={<Share2 className="w-4 h-4" />}
            className="flex-1 sm:flex-initial"
          >
            Share with Doctor
          </Button>
        </div>
      </div>

      {/* Share with Doctor Modal */}
      <Modal
        isOpen={shareModalOpen}
        onClose={() => setShareModalOpen(false)}
        title="Share Report Explanation"
        description="Share a secure summary view with your physician or healthcare clinic."
      >
        <div className="space-y-4">
          <div className="p-3.5 bg-sky-50 rounded-xl border border-sky-100 text-xs text-sky-900 leading-relaxed">
            This provides your clinician with a streamlined view of extracted parameters and your selected preparation questions.
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide mb-1.5">
              Secure Consultation Link
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={window.location.href}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 select-all"
              />
              <Button
                variant="primary"
                size="sm"
                onClick={copyShareableLink}
                leftIcon={<Copy className="w-3.5 h-3.5" />}
              >
                {copiedLink ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-end">
            <Button variant="outline" size="md" onClick={() => setShareModalOpen(false)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
