import { defineStore } from 'pinia';
import { loginApi } from '../api/auth';
import { UserRole } from '../constants/enums';
import type { User } from '../types/common';
import { storage } from '../utils/storage';

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: storage.getToken() || '', user: JSON.parse(localStorage.getItem('wjecampus_user') || 'null') as User | null }),
  getters: { isAdmin: s => s.user?.role === UserRole.ADMIN, isTeacher: s => s.user?.role === UserRole.TEACHER, isStudent: s => s.user?.role === UserRole.STUDENT },
  actions: {
    async login(username: string, password: string) { const res = await loginApi(username, password); this.token = res.access_token; this.user = res.user; storage.setToken(res.access_token); localStorage.setItem('wjecampus_user', JSON.stringify(res.user)); },
    logout() { this.token = ''; this.user = null; storage.clearToken(); localStorage.removeItem('wjecampus_user'); },
    hasRole(roles?: string[]) { return !roles?.length || !!this.user?.role && roles.includes(this.user.role); },
  },
});
