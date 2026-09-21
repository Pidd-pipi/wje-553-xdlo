import { storeToRefs } from 'pinia';
import { useAttendanceStore } from '../stores/attendanceStore';
export function useAttendance() { const store = useAttendanceStore(); const { items } = storeToRefs(store); return { attendance: items, fetchAttendance: store.fetch, changeAttendanceStatus: store.changeStatus }; }
