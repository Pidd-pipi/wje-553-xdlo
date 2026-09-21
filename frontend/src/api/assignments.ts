import { request } from '../utils/request';
import type { Assignment } from '../types/assignment';
export const assignmentApi = { list: (course_id?: string) => request.get<unknown, Assignment[]>('/assignments', { params: { course_id } }), update: (id: string, payload: Partial<Assignment>) => request.patch<unknown, Assignment>('/assignments/' + id, payload) };
