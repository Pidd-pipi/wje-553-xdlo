import { request } from '../utils/request';
import type { AuditLog } from '../types/common';
export const auditApi = { list: () => request.get<unknown, AuditLog[]>('/audit/logs') };
