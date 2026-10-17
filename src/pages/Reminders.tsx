import React, { useEffect, useState } from 'react'
import {
  BellRing,
  Plus,
  CheckCircle2,
  Trash2,
  Calendar,
  AlertCircle,
  Tag,
  Clock,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { Input } from '../components/ui/Input'
import { Select } from '../components/ui/Select'
import { EmptyState } from '../components/ui/EmptyState'
import { Skeleton } from '../components/ui/Skeleton'
import { reminderService } from '../services/reminderService'
import { Reminder, ReminderPriority } from '../types'
import { useToast } from '../context/ToastContext'

export const RemindersPage: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  // Form states
  const [title, setTitle] = useState('')
  const [dueText, setDueText] = useState('')
  const [category, setCategory] = useState<Reminder['category']>('follow-up')
  const [priority, setPriority] = useState<ReminderPriority>('medium')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { success, error: toastError } = useToast()

  const loadReminders = async () => {
    setIsLoading(true)
    try {
      const data = await reminderService.getReminders()
      setReminders(data)
    } catch {
      toastError('Could not load reminders.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadReminders()
  }, [])

  const handleToggleComplete = async (id: string, currentCompleted: boolean) => {
    try {
      const updated = await reminderService.completeReminder(id, !currentCompleted)
      setReminders((prev) => prev.map((r) => (r.id === id ? updated : r)))
      success(updated.completed ? 'Reminder completed.' : 'Reminder reopened.')
    } catch {
      toastError('Failed to update reminder.')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await reminderService.deleteReminder(id)
      setReminders((prev) => prev.filter((r) => r.id !== id))
      success('Reminder removed.')
    } catch {
      toastError('Failed to delete reminder.')
    }
  }

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !dueText.trim()) {
      toastError('Please fill in title and due date.')
      return
    }

    setIsSubmitting(true)
    try {
      const created = await reminderService.createReminder({
        title: title.trim(),
        dueText: dueText.trim(),
        category,
        priority,
        completed: false,
      })

      setReminders((prev) => [created, ...prev])
      success('Reminder added.')
      setIsAddModalOpen(false)
      setTitle('')
      setDueText('')
    } catch {
      toastError('Failed to create reminder.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const pending = reminders.filter((r) => !r.completed)
  const completed = reminders.filter((r) => r.completed)

  return (
    <div className="space-y-6 animate-fade-in pb-12 max-w-4xl mx-auto">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Healthcare Reminders
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Stay on track with physician follow-ups, test reviews, and prescription schedules.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={() => setIsAddModalOpen(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          + Add Reminder
        </Button>
      </div>

      {/* Pending Reminders List */}
      <Card className="p-6">
        <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-slate-100 mb-2">
          <div className="flex items-center gap-2">
            <CardTitle>Active Reminders</CardTitle>
            <Badge variant="warning" size="sm">
              {pending.length} pending
            </Badge>
          </div>
        </CardHeader>

        {isLoading ? (
          <div className="space-y-3 py-3">
            <Skeleton className="h-16 rounded-xl" />
            <Skeleton className="h-16 rounded-xl" />
          </div>
        ) : pending.length === 0 ? (
          <EmptyState
            icon={<BellRing className="w-8 h-8" />}
            title="All caught up!"
            description="You have no pending healthcare tasks or reminders at this time."
            actionLabel="Add Reminder"
            onAction={() => setIsAddModalOpen(true)}
            className="my-3 border-0 bg-transparent p-4"
          />
        ) : (
          <div className="divide-y divide-slate-100">
            {pending.map((rem) => (
              <div
                key={rem.id}
                className="py-3.5 flex items-start justify-between gap-3 group hover:bg-slate-50/70 p-2.5 rounded-xl transition-colors"
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleComplete(rem.id, rem.completed)}
                    className="mt-0.5 w-5 h-5 rounded-md border border-slate-300 hover:border-sky-500 flex items-center justify-center transition-colors text-transparent hover:text-sky-500"
                    title="Mark as complete"
                    aria-label="Mark complete"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                  </button>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                      {rem.title}
                    </h4>
                    <div className="flex flex-wrap items-center gap-2.5 mt-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1 font-medium text-sky-700">
                        <Clock className="w-3.5 h-3.5 text-sky-600" />
                        {rem.dueText}
                      </span>
                      <span>•</span>
                      <span className="capitalize">{rem.category.replace('-', ' ')}</span>
                      {rem.priority === 'high' && (
                        <>
                          <span>•</span>
                          <span className="text-rose-600 font-bold uppercase text-[10px]">High Priority</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(rem.id)}
                  className="opacity-60 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all"
                  title="Delete reminder"
                  aria-label="Delete reminder"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Completed Reminders */}
      {completed.length > 0 && (
        <Card className="p-6 opacity-85">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-slate-100 mb-2">
            <CardTitle className="text-sm text-slate-500">Completed ({completed.length})</CardTitle>
          </CardHeader>

          <div className="divide-y divide-slate-100">
            {completed.map((rem) => (
              <div
                key={rem.id}
                className="py-3 flex items-start justify-between gap-3 text-slate-400 p-2 rounded-xl"
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleComplete(rem.id, rem.completed)}
                    className="mt-0.5 text-emerald-600 hover:text-slate-400"
                    title="Re-open reminder"
                    aria-label="Re-open reminder"
                  >
                    <CheckCircle2 className="w-5 h-5 fill-emerald-100" />
                  </button>
                  <div>
                    <p className="text-sm font-medium line-through text-slate-500">{rem.title}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{rem.dueText}</p>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(rem.id)}
                  className="p-1 rounded text-slate-300 hover:text-rose-600"
                  title="Remove reminder"
                  aria-label="Delete reminder"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Add Reminder Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Healthcare Reminder"
        description="Set a prompt for appointments, follow-ups, or lab result reviews."
      >
        <form onSubmit={handleCreateReminder} className="space-y-4">
          <Input
            label="Reminder Title"
            placeholder="e.g. Follow up with Dr. Sharma regarding metabolic panel"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          <Input
            label="Due Timing / Date"
            placeholder="e.g. Today · 5:00 PM, Tomorrow, or October 25"
            value={dueText}
            onChange={(e) => setDueText(e.target.value)}
            required
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Select
              label="Category"
              value={category}
              onChange={(e) => setCategory(e.target.value as Reminder['category'])}
              options={[
                { value: 'follow-up', label: 'Doctor Follow-Up' },
                { value: 'lab-test', label: 'Lab Test Review' },
                { value: 'checkup', label: 'Annual Checkup' },
                { value: 'medication-refill', label: 'Medication / Supplements' },
                { value: 'general', label: 'General Health' },
              ]}
            />

            <Select
              label="Priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as ReminderPriority)}
              options={[
                { value: 'low', label: 'Low' },
                { value: 'medium', label: 'Medium' },
                { value: 'high', label: 'High' },
              ]}
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <Button type="button" variant="outline" size="md" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="md" isLoading={isSubmitting}>
              Create Reminder
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
