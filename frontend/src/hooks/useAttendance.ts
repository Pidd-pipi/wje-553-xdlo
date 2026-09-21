import { storeToRefs } from 'pinia';
import { useAttendanceStore } from '../stores/attendanceStore';
export function useAttendance() {
  const store = useAttendanceStore();
  const { items, corrections } = storeToRefs(store);
  return {
    attendance: items,
    corrections,
    fetchAttendance: store.fetch,
    changeAttendanceStatus: store.changeStatus,
    fetchCorrections: store.fetchCorrections,
    submitCorrection: store.submitCorrection,
    approveCorrection: store.approveCorrection,
    rejectCorrection: store.rejectCorrection,
  };
}
