import type { UserRole } from '../constants/enums';
export interface User { id: string; username: string; full_name: string; role: UserRole }
export interface Page<T> { items: T[]; total: number }
export interface AuditLog { id: string; user_id?: string; action: string; target_type: string; target_id?: string; before_data?: Record<string, unknown>; after_data?: Record<string, unknown>; ip_address?: string; created_at: string }
