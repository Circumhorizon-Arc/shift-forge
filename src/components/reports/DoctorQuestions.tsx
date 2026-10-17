import React, { useState } from 'react'
import { Card, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { MessageSquareText, Copy, Check, Stethoscope } from 'lucide-react'
import { useToast } from '../../context/ToastContext'

interface DoctorQuestionsProps {
  questions: string[]
}

export const DoctorQuestions: React.FC<DoctorQuestionsProps> = ({ questions }) => {
  const [copied, setCopied] = useState(false)
  const [checkedIndices, setCheckedIndices] = useState<Record<number, boolean>>({})
  const { success } = useToast()

  const toggleCheck = (idx: number) => {
    setCheckedIndices((prev) => ({ ...prev, [idx]: !prev[idx] }))
  }

  const copyAll = async () => {
    const textToCopy = questions.map((q, i) => `${i + 1}. ${q}`).join('\n')
    try {
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      success('Suggested doctor questions copied to clipboard!')
      setTimeout(() => setCopied(false), 2500)
    } catch {
      // fallback
    }
  }

  return (
    <Card className="p-6">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-slate-100 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
            <Stethoscope className="w-4 h-4" />
          </div>
          <div>
            <CardTitle>Questions to Ask Your Doctor</CardTitle>
            <span className="text-[11px] text-slate-500">
              Personalized prompts designed to prepare you for your next clinical consultation
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="primary" size="sm">
            <MessageSquareText className="w-3 h-3 text-teal-600" />
            <span>Discussion Prompts</span>
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={copyAll}
            leftIcon={copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          >
            {copied ? 'Copied' : 'Copy All'}
          </Button>
        </div>
      </CardHeader>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mt-4">
        {questions.map((question, index) => {
          const isChecked = !!checkedIndices[index]
          return (
            <div
              key={index}
              onClick={() => toggleCheck(index)}
              className={`p-4 rounded-xl border transition-all duration-150 cursor-pointer flex items-start gap-3 select-none ${
                isChecked
                  ? 'bg-teal-50/50 border-teal-200 text-teal-900 shadow-2xs'
                  : 'bg-white border-slate-200/90 text-slate-800 hover:border-slate-300 hover:bg-slate-50/50'
              }`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => {}} // handled by parent div
                className="mt-1 h-4 w-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
              />
              <div className="flex-1">
                <span className="text-[11px] font-bold text-teal-700 uppercase tracking-wider block mb-1">
                  Question {index + 1}
                </span>
                <p className="text-sm font-medium leading-relaxed">{question}</p>
              </div>
            </div>
          )
        })}
      </div>

      <p className="text-xs text-slate-500 mt-4 italic">
        Tip: Check the boxes for the questions you would like to ask your physician during your next visit.
      </p>
    </Card>
  )
}
