import { Reminder } from '../../types'

export const initialMockReminders: Reminder[] = [
  {
    id: 'rem-001',
    title: 'Follow up with Dr. Sarah Sharma on lab panel',
    dueText: 'Today · 5:00 PM',
    category: 'follow-up',
    completed: false,
    priority: 'high',
    relatedReportId: 'rep-001',
    createdAt: '2026-10-15',
  },
  {
    id: 'rem-002',
    title: 'Review complete blood count results in portal',
    dueText: 'Tomorrow · 10:00 AM',
    category: 'lab-test',
    completed: false,
    priority: 'medium',
    relatedReportId: 'rep-002',
    createdAt: '2026-10-16',
  },
  {
    id: 'rem-003',
    title: 'Schedule annual comprehensive dental examination',
    dueText: 'October 25, 2026',
    category: 'checkup',
    completed: false,
    priority: 'low',
    createdAt: '2026-10-10',
  },
  {
    id: 'rem-004',
    title: 'Morning fasting blood glucose check',
    dueText: 'Completed yesterday',
    category: 'lab-test',
    completed: true,
    priority: 'medium',
    createdAt: '2026-10-14',
  },
]
