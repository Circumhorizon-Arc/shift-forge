export type ReminderPriority = 'low' | 'medium' | 'high'

export interface Reminder {
  id: string
  title: string
  dueText: string // e.g. "Today · 5:00 PM", "Tomorrow", "October 25"
  category: 'follow-up' | 'lab-test' | 'medication-refill' | 'checkup' | 'general'
  completed: boolean
  priority?: ReminderPriority
  relatedReportId?: string
  createdAt?: string
}
