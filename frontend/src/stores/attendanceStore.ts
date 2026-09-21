import { defineStore } from 'pinia';
import { attendanceApi } from '../api/attendance';
import type { Attendance } from '../types/attendance';
export const useAttendanceStore = defineStore('attendance', { state: () => ({ items: [] as Attendance[] }), actions: { async fetch(params?: Record<string,string>) { this.items = await attendanceApi.list(params); }, async changeStatus(id: string, status: Attendance['status']) { await attendanceApi.update(id, { status }); await this.fetch(); } } });
