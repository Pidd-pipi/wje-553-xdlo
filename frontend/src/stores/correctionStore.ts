import { defineStore } from 'pinia';
import { correctionApi } from '../api/corrections';
import type { AttendanceStatus, CorrectionStatus } from '../constants/enums';
import type { AttendanceCorrection } from '../types/correction';

export const useCorrectionStore = defineStore('correction', {
  state: () => ({ corrections: [] as AttendanceCorrection[] }),
  actions: {
    async fetch(status?: CorrectionStatus) {
      this.corrections = await correctionApi.list(status);
    },
    async submit(attendanceId: string, expectedStatus: AttendanceStatus, reason?: string) {
      return correctionApi.submit({ attendance_id: attendanceId, expected_status: expectedStatus, reason });
    },
    async approve(id: string, remark?: string) {
      return correctionApi.approve(id, remark);
    },
    async reject(id: string, reason: string) {
      return correctionApi.reject(id, reason);
    },
  },
});
