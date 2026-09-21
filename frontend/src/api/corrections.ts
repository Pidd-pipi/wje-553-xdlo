import { request } from '../utils/request';
import type { AttendanceStatus, CorrectionStatus } from '../constants/enums';
import type { AttendanceCorrection } from '../types/correction';

export const correctionApi = {
  list: (status?: CorrectionStatus) =>
    request.get<unknown, AttendanceCorrection[]>('/attendance/corrections', { params: status ? { status } : {} }),
  submit: (payload: { attendance_id: string; expected_status: AttendanceStatus; reason?: string }) =>
    request.post<unknown, AttendanceCorrection>('/attendance/corrections', payload),
  approve: (id: string, remark?: string) =>
    request.post<unknown, AttendanceCorrection>(`/attendance/corrections/${id}/approve`, { remark: remark || null }),
  reject: (id: string, reason: string) =>
    request.post<unknown, AttendanceCorrection>(`/attendance/corrections/${id}/reject`, { reason }),
};
