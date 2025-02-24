export interface Reminder {
  id: number;
  text: string;
  due_date: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ReminderFormData {
  text: string;
  due_date: string;
  is_active?: boolean;
}
