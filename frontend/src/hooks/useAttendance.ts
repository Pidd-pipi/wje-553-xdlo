import { storeToRefs } from 'pinia';
import { useAttendanceStore } from '../stores/attendanceStore';
import { useCorrectionStore } from '../stores/correctionStore';
export function useAttendance() {
  const store = useAttendanceStore();
  const correctionStore = useCorrectionStore();
  const { items } = storeToRefs(store);
  const { corrections } = storeToRefs(correctionStore);
  return {
    attendance: items,
    corrections,
    fetchAttendance: store.fetch,
    changeAttendanceStatus: store.changeStatus,
    fetchCorrections: correctionStore.fetch,
    submitCorrection: correctionStore.submit,
    approveCorrection: correctionStore.approve,
    rejectCorrection: correctionStore.reject,
  };
}
