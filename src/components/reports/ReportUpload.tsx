import React, { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  UploadCloud,
  FileCheck,
  File,
  AlertCircle,
  Sparkles,
  CheckCircle2,
  Clock,
  ArrowRight,
} from 'lucide-react'
import { Button } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { Card } from '../ui/Card'
import { reportService } from '../../services/reportService'
import { useToast } from '../../context/ToastContext'

type UploadStep = 'select' | 'uploading' | 'processing' | 'analyzing' | 'complete' | 'error'

export const ReportUpload: React.FC = () => {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [step, setStep] = useState<UploadStep>('select')
  const [progress, setProgress] = useState(0)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [createdReportId, setCreatedReportId] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const { success, error: toastError } = useToast()
  const navigate = useNavigate()

  const validTypes = ['application/pdf', 'image/jpeg', 'image/png']

  const validateAndSetFile = (file: File) => {
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Please upload a supported format: PDF, JPG, or PNG.')
      toastError('Unsupported file type. Please upload a PDF or image.')
      return
    }
    if (file.size > 25 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 25 MB limit.')
      toastError('File is too large (max 25 MB).')
      return
    }

    setErrorMessage(null)
    setSelectedFile(file)
    setStep('select')
  }

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0])
    }
  }

  const startUploadAndAnalysis = async () => {
    if (!selectedFile) return

    try {
      setStep('uploading')
      setProgress(10)

      // Service call
      const result = await reportService.uploadReport(selectedFile, (pct) => {
        setProgress(pct)
        if (pct >= 50 && pct < 85) {
          setStep('processing')
        } else if (pct >= 85) {
          setStep('analyzing')
        }
      })

      setStep('complete')
      setProgress(100)
      setCreatedReportId(result.report.id)
      success('Your report has been uploaded and analyzed successfully.')
    } catch (err: unknown) {
      setStep('error')
      const msg = err && typeof err === 'object' && 'message' in err
        ? String((err as { message: string }).message)
        : 'An error occurred during report upload and analysis.'
      setErrorMessage(msg)
      toastError(msg)
    }
  }

  const resetUpload = () => {
    setSelectedFile(null)
    setStep('select')
    setProgress(0)
    setErrorMessage(null)
    setCreatedReportId(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <Card className="max-w-2xl mx-auto p-6 sm:p-8">
      {/* Step 1 & Default: Select or Drag & Drop */}
      {step === 'select' && (
        <div className="space-y-6">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all duration-200 cursor-pointer flex flex-col items-center justify-center ${
              dragActive
                ? 'border-sky-500 bg-sky-50/60 scale-[1.01]'
                : selectedFile
                ? 'border-teal-400 bg-teal-50/40'
                : 'border-slate-300 hover:border-sky-400 hover:bg-slate-50/80 bg-slate-50/40'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              className="hidden"
              onChange={handleChange}
            />

            <div
              className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-colors ${
                selectedFile
                  ? 'bg-teal-100 text-teal-700'
                  : 'bg-sky-50 text-sky-600'
              }`}
            >
              {selectedFile ? <FileCheck className="w-8 h-8" /> : <UploadCloud className="w-8 h-8" />}
            </div>

            <h3 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight mb-1">
              {selectedFile ? 'Report Selected' : 'Drag and drop your medical report here'}
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 max-w-sm mb-4">
              {selectedFile
                ? 'Click or drop another file to replace'
                : 'Upload clinical lab reports, blood panels, or health summaries in plain PDF or image format.'}
            </p>

            <Button
              type="button"
              variant={selectedFile ? 'outline' : 'primary'}
              size="md"
              onClick={(e) => {
                e.stopPropagation()
                fileInputRef.current?.click()
              }}
            >
              Browse Files
            </Button>

            <span className="text-[11px] font-semibold text-slate-500 mt-4 uppercase tracking-wider">
              Supported Formats: PDF · JPG · PNG (Up to 25 MB)
            </span>
          </div>

          {/* Selected File Details Box */}
          {selectedFile && (
            <div className="p-4 rounded-xl border border-teal-200 bg-teal-50/30 flex items-center justify-between gap-3 animate-fade-in">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center flex-shrink-0">
                  <File className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-bold text-slate-900 truncate">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type || 'Document'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={resetUpload}>
                  Remove
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  onClick={startUploadAndAnalysis}
                  leftIcon={<Sparkles className="w-4 h-4" />}
                >
                  Start AI Analysis
                </Button>
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>
      )}

      {/* Dynamic Processing States: Uploading, Processing, AI Analysis */}
      {(step === 'uploading' || step === 'processing' || step === 'analyzing') && (
        <div className="py-8 px-4 text-center space-y-6 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto shadow-sm">
            <Clock className="w-8 h-8 animate-spin text-sky-600" />
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              {step === 'uploading' && 'Uploading Medical Report...'}
              {step === 'processing' && 'Extracting Diagnostic Observations...'}
              {step === 'analyzing' && 'Generating AI-Assisted Explanations...'}
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
              {step === 'uploading' && 'Securely transmitting document to processing engine.'}
              {step === 'processing' && 'Parsing biochemical parameters, reference ranges, and numerical indices.'}
              {step === 'analyzing' && 'Formulating plain-language summaries and questions to discuss with your doctor.'}
            </p>
          </div>

          <div className="max-w-md mx-auto space-y-2">
            <ProgressBar progress={progress} color="sky" height="md" showLabel />
            <div className="flex justify-between text-[11px] font-semibold text-slate-500 uppercase tracking-wider pt-2">
              <span className={step === 'uploading' ? 'text-sky-600' : 'text-slate-400'}>1. Upload</span>
              <span className={step === 'processing' ? 'text-sky-600' : 'text-slate-400'}>2. Extract Facts</span>
              <span className={step === 'analyzing' ? 'text-sky-600' : 'text-slate-400'}>3. Plain Language AI</span>
            </div>
          </div>
        </div>
      )}

      {/* State 5: Complete */}
      {step === 'complete' && (
        <div className="py-8 px-4 text-center space-y-6 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto shadow-sm">
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          </div>

          <div className="space-y-1.5">
            <h3 className="text-xl font-bold text-slate-900 tracking-tight">
              Report Analysis Ready
            </h3>
            <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
              Your report has been parsed successfully. Structured findings, educational explanations, and doctor discussion points are ready.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Button
              variant="primary"
              size="lg"
              onClick={() => {
                if (createdReportId) {
                  navigate(`/reports/${createdReportId}/analysis`)
                } else {
                  navigate('/reports')
                }
              }}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              View AI Explanation
            </Button>
            <Button variant="outline" size="lg" onClick={resetUpload}>
              Upload Another
            </Button>
          </div>
        </div>
      )}

      {/* State 6: Error */}
      {step === 'error' && (
        <div className="py-8 px-4 text-center space-y-6 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto shadow-sm">
            <AlertCircle className="w-8 h-8 text-rose-600" />
          </div>

          <div className="space-y-1.5">
            <h3 className="text-xl font-bold text-slate-900 tracking-tight">
              Upload Failed
            </h3>
            <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
              {errorMessage || 'We couldn’t process this report right now. Please verify the file and try again.'}
            </p>
          </div>

          <div className="flex items-center justify-center gap-3 pt-2">
            <Button variant="primary" size="md" onClick={resetUpload}>
              Try Again
            </Button>
            <Button variant="outline" size="md" onClick={() => navigate('/reports')}>
              Back to Reports
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}
