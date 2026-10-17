import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, ShieldCheck, FileCheck2, HelpCircle } from 'lucide-react'
import { ReportUpload } from '../components/reports/ReportUpload'
import { MedicalDisclaimer } from '../components/reports/MedicalDisclaimer'

export const UploadReportPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in pb-12 max-w-4xl mx-auto">
      {/* Back Link & Header */}
      <div>
        <Link
          to="/reports"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Medical Reports</span>
        </Link>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Upload Medical Report
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload laboratory test results to extract structured findings and AI-assisted educational explanations.
        </p>
      </div>

      {/* Safety Notice */}
      <MedicalDisclaimer compact />

      {/* Upload Drag & Drop Component */}
      <ReportUpload />

      {/* Privacy and Verification Guidance */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
        <div className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-2xs flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div className="text-xs space-y-1">
            <h4 className="font-bold text-slate-900">Confidential Processing</h4>
            <p className="text-slate-500 leading-relaxed">
              Files are processed in an isolated environment. Health data is never sold or utilized for training public commercial LLMs.
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200/80 shadow-2xs flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center flex-shrink-0">
            <FileCheck2 className="w-4 h-4" />
          </div>
          <div className="text-xs space-y-1">
            <h4 className="font-bold text-slate-900">Supported Report Types</h4>
            <p className="text-slate-500 leading-relaxed">
              Complete Blood Count (CBC), Comprehensive Metabolic Panels (CMP), Lipid Profiles, Thyroid Panels, and urinalysis summaries.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
