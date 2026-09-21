import { request } from '../utils/request';
export interface GradeSummary { average: number; highest: number; lowest: number; pass_rate: number; rows: unknown[] }
export const gradeApi = { summary: (course_id?: string) => request.get<unknown, GradeSummary>('/grades/summary', { params: { course_id } }) };
