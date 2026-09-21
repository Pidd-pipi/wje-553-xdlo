import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
const routes = [
  { path: '/', redirect: '/courses' },
  { path: '/login', component: () => import('../pages/Login.vue') },
  { path: '/courses', component: () => import('../pages/Courses.vue'), meta: { requiredRole: ['ADMIN','TEACHER','STUDENT'] } },
  { path: '/courses/:id', component: () => import('../pages/CourseDetail.vue'), meta: { requiredRole: ['ADMIN','TEACHER','STUDENT'] } },
  { path: '/assignments', component: () => import('../pages/Assignments.vue'), meta: { requiredRole: ['ADMIN','TEACHER','STUDENT'] } },
  { path: '/grades', component: () => import('../pages/Grades.vue'), meta: { requiredRole: ['ADMIN','TEACHER','STUDENT'] } },
  { path: '/attendance', component: () => import('../pages/Attendance.vue'), meta: { requiredRole: ['ADMIN','TEACHER','STUDENT'] } },
  { path: '/audit-log', component: () => import('../pages/AuditLog.vue'), meta: { requiredRole: ['ADMIN'] } },
];
export const router = createRouter({ history: createWebHistory(), routes });
router.beforeEach((to) => { const auth = useAuthStore(); const roles = to.meta.requiredRole as string[] | undefined; if (to.path !== '/login' && !auth.token) return '/login'; if (roles && !auth.hasRole(roles)) return '/courses'; return true; });
