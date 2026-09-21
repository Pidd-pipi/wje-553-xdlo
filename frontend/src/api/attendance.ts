import { request } from '../utils/request';
import type { Attendance, AttendanceCorrection } from '../types/attendance';
export const attendanceApi = {
  list: (params?: Record<string, string>) => request.get<unknown, Attendance[]>('/attendance', { params }),
  update: (id: string, payload: Partial<Attendance>) => request.patch<unknown, Attendance>('/attendance/' + id, payload),
  listCorrections: (params?: Record<string, string>) => request.get<unknown, AttendanceCorrection[]>('/attendance/corrections', { params }),
  submitCorrection: (payload: { attendance_id: string; requested_status: Attendance['status']; reason: string }) => request.post<unknown, AttendanceCorrection>('/attendance/corrections', payload),
  approveCorrection: (id: string, review_comment?: string) => request.post<unknown, AttendanceCorrection>('/attendance/corrections/' + id + '/approve', review_comment ? { review_comment } : {}),
  rejectCorrection: (id: string, review_comment: string) => request.post<unknown, AttendanceCorrection>('/attendance/corrections/' + id + '/reject', { review_comment }),
};
