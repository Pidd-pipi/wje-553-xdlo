import { storeToRefs } from 'pinia';
import { useCourseStore } from '../stores/courseStore';
export function useCourses() { const store = useCourseStore(); const { items, current, loading } = storeToRefs(store); return { courses: items, current, loading, fetchCourses: store.fetch, enrollCourse: store.enroll, dropCourse: store.drop, changeCourseStatus: store.updateStatus }; }
