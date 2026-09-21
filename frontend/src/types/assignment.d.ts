import type { AssignmentStatus, AssignmentType } from '../constants/enums';
export interface Assignment { id: string; course_id: string; course_name?: string; title: string; type: AssignmentType; description?: string; deadline: string; total_score: number; weight?: number; status: AssignmentStatus; submissions_count: number; created_at: string; updated_at: string }
