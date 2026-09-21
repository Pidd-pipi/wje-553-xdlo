import type { AttendanceStatus, CorrectionStatus } from '../constants/enums';
export interface AttendanceCorrection {
  id: string;
  attendance_id: string;
  requester_id: string;
  requester_name?: string;
  expected_status: AttendanceStatus;
  reason?: string | null;
  status: CorrectionStatus;
  reviewer_id?: string | null;
  reviewer_name?: string | null;
  review_remark?: string | null;
  reviewed_at?: string | null;
  course_id?: string;
  course_name?: string;
  student_id?: string;
  student_name?: string;
  attendance_date?: string;
  current_status?: AttendanceStatus;
  created_at: string;
  updated_at: string;
}
