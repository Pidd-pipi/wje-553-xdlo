import type { CourseStatus } from '../constants/enums';
export interface Course { id: string; name: string; code: string; teacher_id: string; teacher_name?: string; description?: string; max_students: number; semester?: string; status: CourseStatus; enrolled_count: number; created_at: string; updated_at: string }
export type CoursePayload = Omit<Course, 'id'|'teacher_name'|'enrolled_count'|'created_at'|'updated_at'>;
