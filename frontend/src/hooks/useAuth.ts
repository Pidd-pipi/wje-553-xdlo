import { computed } from 'vue';
import { useAuthStore } from '../stores/authStore';
export function useAuth() { const store = useAuthStore(); return { user: computed(() => store.user), login: store.login, logout: store.logout, isAdmin: computed(() => store.isAdmin), isTeacher: computed(() => store.isTeacher), isStudent: computed(() => store.isStudent), can: (roles: string[]) => store.hasRole(roles) }; }
