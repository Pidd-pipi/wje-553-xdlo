import type { AttendanceStatus } from '../constants/enums';
export interface Attendance { id: string; course_id: string; student_id: string; course_name?: string; student_name?: string; date: string; status: AttendanceStatus; remark?: string; created_at: string; updated_at: string }
