import { request } from '../utils/request';
import type { User } from '../types/common';
export function loginApi(username: string, password: string) { return request.post<unknown, { access_token: string; user: User }>('/auth/login', { username, password }); }
