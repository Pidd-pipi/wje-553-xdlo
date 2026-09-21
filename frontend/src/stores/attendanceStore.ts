import { defineStore } from 'pinia';
import { attendanceApi } from '../api/attendance';
import type { Attendance, AttendanceCorrection } from '../types/attendance';
export const useAttendanceStore = defineStore('attendance', {
  state: () => ({ items: [] as Attendance[], corrections: [] as AttendanceCorrection[] }),
  actions: {
    async fetch(params?: Record<string,string>) { this.items = await attendanceApi.list(params); },
    async changeStatus(id: string, status: Attendance['status']) { await attendanceApi.update(id, { status }); await this.fetch(); },
    async fetchCorrections(params?: Record<string,string>) { this.corrections = await attendanceApi.listCorrections(params); },
    async submitCorrection(payload: { attendance_id: string; requested_status: Attendance['status']; reason: string }) { await attendanceApi.submitCorrection(payload); await Promise.all([this.fetch(), this.fetchCorrections()]); },
    async approveCorrection(id: string, review_comment?: string) { await attendanceApi.approveCorrection(id, review_comment); await Promise.all([this.fetch(), this.fetchCorrections()]); },
    async rejectCorrection(id: string, review_comment: string) { await attendanceApi.rejectCorrection(id, review_comment); await Promise.all([this.fetch(), this.fetchCorrections()]); },
  },
});
