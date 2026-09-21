import { request } from '../utils/request';
import type { Attendance } from '../types/attendance';
export const attendanceApi = { list: (params?: Record<string, string>) => request.get<unknown, Attendance[]>('/attendance', { params }), update: (id: string, payload: Partial<Attendance>) => request.patch<unknown, Attendance>('/attendance/' + id, payload) };
