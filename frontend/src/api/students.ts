import { request } from '../utils/request';
import type { Student } from '../types/student';
export const studentApi = { list: () => request.get<unknown, Student[]>('/students') };
