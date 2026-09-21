import { request } from '../utils/request';
import type { Course, CoursePayload } from '../types/course';
export const courseApi = {
  list: (params?: Record<string, string>) => request.get<unknown, Course[]>('/courses', { params }),
  get: (id: string) => request.get<unknown, Course>('/courses/' + id),
  create: (payload: CoursePayload) => request.post<unknown, Course>('/courses', payload),
  update: (id: string, payload: Partial<CoursePayload>) => request.patch<unknown, Course>('/courses/' + id, payload),
  enroll: (courseId: string, studentId: string) => request.post('/courses/' + courseId + '/enroll/' + studentId),
  drop: (courseId: string, studentId: string) => request.delete('/courses/' + courseId + '/enroll/' + studentId),
};
