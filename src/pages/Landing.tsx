import React from 'react'
import { Link } from 'react-router-dom'
import {
  HeartPulse,
  Sparkles,
  FileText,
  Activity,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Lock,
  ArrowRight,
  Stethoscope,
  Eye,
  Check,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { MedicalDisclaimer } from '../components/reports/MedicalDisclaimer'

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col selection:bg-sky-100 selection:text-sky-900">
      {/* Navigation Bar */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white shadow-xs">
              <HeartPulse className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg text-slate-900 tracking-tight">
              Health<span className="text-sky-600">Sense</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-600">
            <a href="#how-it-works" className="hover:text-slate-900 transition-colors">How It Works</a>
            <a href="#ai-reports" className="hover:text-slate-900 transition-colors">AI Reports</a>
            <a href="#tracking" className="hover:text-slate-900 transition-colors">Health Tracking</a>
            <a href="#privacy" className="hover:text-slate-900 transition-colors">Privacy & Security</a>

          </nav>

          <div className="flex items-center gap-3">
            <Link to="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/register">
              <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-28 overflow-hidden bg-gradient-to-b from-white via-sky-50/20 to-slate-50 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-50 border border-sky-200/80 text-sky-800 text-xs font-semibold shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-sky-600" />
              <span>AI-Assisted Diagnostic Literacy Platform</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.15]">
              Understand Your Health. <br />
              <span className="bg-gradient-to-r from-sky-600 via-sky-700 to-teal-600 bg-clip-text text-transparent">
                Make Better Decisions.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed font-normal">
              Health Sense helps you organize your health information, understand medical reports in plain language, and stay on top of your healthcare journey.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link to="/register" className="w-full sm:w-auto">
                <Button size="lg" variant="primary" className="w-full sm:w-auto shadow-md" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Get Started
                </Button>
              </Link>
              <a href="#how-it-works" className="w-full sm:w-auto">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Learn More
                </Button>
              </a>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 pt-4 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-1.5">
                <Check className="w-4 h-4 text-emerald-600" />
                Plain-Language Translations
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="w-4 h-4 text-emerald-600" />
                Structured Doctor Questions
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="w-4 h-4 text-emerald-600" />
                Zero Medical Jargon Confusion
              </span>
            </div>
          </div>

          {/* Hero Visual Preview: Polished Healthcare Dashboard & Report UI Mockup */}
          <div className="mt-12 sm:mt-16 max-w-5xl mx-auto rounded-3xl p-3 sm:p-4 bg-gradient-to-b from-sky-200/60 to-slate-200/40 border border-slate-200 shadow-2xl">
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
              {/* Fake App Bar */}
              <div className="h-11 bg-slate-50 border-b border-slate-200/80 px-4 flex items-center justify-between text-xs text-slate-600">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  <span className="ml-2 font-mono text-[11px] text-slate-600">app.healthsense.dev / dashboard</span>
                </div>
                <Badge variant="success" size="sm">
                  Active Patient Record
                </Badge>
              </div>

              {/* Preview UI Content */}
              <div className="p-6 sm:p-8 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-sky-600">
                      AI-Assisted Report Explanation
                    </span>
                    <h3 className="text-xl font-bold text-slate-900 mt-0.5">
                      Comprehensive Metabolic & Lipid Panel
                    </h3>
                  </div>
                  <Badge variant="info" size="md">
                    <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                    Educational Breakdown
                  </Badge>
                </div>

                {/* Preview Finding Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-slate-700">Hemoglobin</span>
                      <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full">
                        In Range
                      </span>
                    </div>
                    <span className="text-2xl font-extrabold text-slate-900">14.2</span>
                    <span className="text-xs text-slate-500 ml-1">g/dL</span>
                    <p className="text-[11px] text-slate-500 mt-2">Ref: 13.5 – 17.5 g/dL</p>
                  </div>

                  <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/40">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-slate-700">Fasting Glucose</span>
                      <span className="text-[10px] font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full">
                        Outside Range
                      </span>
                    </div>
                    <span className="text-2xl font-extrabold text-slate-900">106</span>
                    <span className="text-xs text-slate-500 ml-1">mg/dL</span>
                    <p className="text-[11px] text-slate-500 mt-2">Ref: 70 – 99 mg/dL</p>
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-slate-700">HDL Cholesterol</span>
                      <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full">
                        In Range
                      </span>
                    </div>
                    <span className="text-2xl font-extrabold text-slate-900">52</span>
                    <span className="text-xs text-slate-500 ml-1">mg/dL</span>
                    <p className="text-[11px] text-slate-500 mt-2">Ref: &gt; 40 mg/dL</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-sky-50/80 border border-sky-100 text-xs text-slate-700 flex items-center justify-between">
                  <span className="font-medium">
                    Plain-language summary and 4 physician talking points generated.
                  </span>
                  <Link to="/register" className="font-bold text-sky-700 hover:underline">
                    Explore live application →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 1: How Health Sense Works */}
      <section id="how-it-works" className="py-20 bg-white border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-sky-600 block mb-2">
              Simple 3-Step Flow
            </span>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              How Health Sense Works
            </h2>
            <p className="text-sm sm:text-base text-slate-600 mt-3">
              Transform confusing laboratory paperwork into clear, actionable health literacy in seconds.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 relative">
              <div className="w-12 h-12 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-lg mb-4">
                1
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Upload Your Medical Report</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Securely upload any PDF or image format of your blood test, diagnostic panel, or annual lab results.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 relative">
              <div className="w-12 h-12 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-lg mb-4">
                2
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">AI-Assisted Educational Parsing</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Health Sense extracts laboratory facts and translates medical reference intervals into clear, neutral explanations.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 relative">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-lg mb-4">
                3
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Discuss Informed with Your Doctor</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Bring structured questions and longitudinal trend lines to your physician consultation with complete confidence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: AI-Assisted Medical Reports */}
      <section id="ai-reports" className="py-20 bg-slate-50 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-600">
                Core Innovation
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
                Medical Reports Translated into Plain English.
              </h2>
              <p className="text-slate-600 leading-relaxed text-sm sm:text-base">
                Diagnostic reports are notorious for arcane acronyms, dense scientific notations, and confusing intervals. Health Sense structures every report into four distinct layers:
              </p>

              <div className="space-y-4 pt-2">
                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-emerald-100 text-emerald-700 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Extracted Facts Separation</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Never confuses numerical laboratory facts with predictive AI explanations.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-sky-100 text-sky-700 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Reference Interval Visualizations</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Instantly see where your metrics sit relative to the laboratory’s stated target bounds.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-teal-100 text-teal-700 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Tailored Doctor Prompts</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Generates specific questions to help you have a productive, collaborative appointment.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/90 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-900">Finding Card Example</span>
                <Badge variant="warning" size="sm">Outside Reference Range</Badge>
              </div>

              <div>
                <span className="text-xs text-slate-500 uppercase font-semibold">Biomarker</span>
                <h4 className="text-lg font-bold text-slate-900">25-Hydroxy Vitamin D</h4>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 flex items-baseline justify-between">
                <div>
                  <span className="text-3xl font-extrabold text-slate-900">22</span>
                  <span className="text-xs font-semibold text-slate-500 ml-1.5">ng/mL</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-semibold text-slate-600 block">Lab Reference</span>
                  <span className="text-xs font-bold text-slate-800">30 – 100 ng/mL</span>
                </div>
              </div>

              <div className="p-3.5 bg-teal-50/60 rounded-xl border border-teal-100 text-xs text-teal-950 leading-relaxed">
                <strong>AI Educational Context:</strong> Vitamin D synthesis is influenced by seasonal sunlight, dietary intake, and absorption. Discuss this result with your healthcare professional.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Health Tracking & Appointments */}
      <section id="tracking" className="py-20 bg-white border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-600 block mb-2">
              Continuous Care
            </span>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Health Tracking & Care Coordination
            </h2>
            <p className="text-sm sm:text-base text-slate-600 mt-3">
              One central hub for your vitals, appointment scheduling, and time-sensitive reminders.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card hoverEffect className="p-6">
              <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center mb-4">
                <Activity className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Vitals & Biomarker Trends</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Log heart rate, blood pressure, fasting glucose, weight, and temperature over time to visualize your personal baseline.
              </p>
            </Card>

            <Card hoverEffect className="p-6">
              <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center mb-4">
                <Calendar className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Appointment Coordination</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Track upcoming specialist visits, routine primary care reviews, and telehealth consultations with complete notes.
              </p>
            </Card>

            <Card hoverEffect className="p-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                <Stethoscope className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Healthcare Reminders</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Never miss a medication refill, 3-month follow-up lab test, or preventative annual health checkup.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Section 4 & 5: Privacy, Security & Responsible AI */}
      <section id="privacy" className="py-20 bg-slate-50 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto space-y-12">
            <div className="text-center space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-600">
                Integrity & Ethics
              </span>
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                Privacy &amp; Security
              </h2>
              <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                Built strictly around patient agency, transparent boundaries, and non-prescriptive educational assistance.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6" id="responsible-ai">
              <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3">
                <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
                  <Lock className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900">Data Minimization & Security</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Your diagnostic records are your personal property. We never sell medical data or train public commercial models on your private lab sheets.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3">
                <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900">Strict Non-Diagnostic Policy</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Health Sense is NOT a doctor. It does not diagnose disease, prescribe medicine, or replace clinical judgment. All insights serve educational empowerment.
                </p>
              </div>
            </div>

            {/* Mandatory Regulatory Disclaimer */}
            <MedicalDisclaimer />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200/80 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white">
              <HeartPulse className="w-4 h-4" />
            </div>
            <span className="font-bold text-base text-slate-900">
              Health<span className="text-sky-600">Sense</span>
            </span>
            <span className="text-xs text-slate-600 ml-2">
              © {new Date().getFullYear()} Health Sense. All rights reserved.
            </span>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-600">
            <Link to="/login" className="hover:text-slate-900 transition-colors">Sign In</Link>
            <Link to="/register" className="hover:text-slate-900 transition-colors">Register</Link>
            <a href="#privacy" className="hover:text-slate-900 transition-colors">Privacy Notice</a>

          </div>
        </div>
      </footer>
    </div>
  )
}
