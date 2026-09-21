import { UserRole } from './enums';
export const RoutePermissions = {
  courses: [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
  assignments: [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
  grades: [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
  attendance: [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
  audit: [UserRole.ADMIN],
} as const;
export const ButtonPermissions = {
  createCourse: [UserRole.ADMIN, UserRole.TEACHER],
  changeAttendance: [UserRole.ADMIN, UserRole.TEACHER],
  modifyGrade: [UserRole.ADMIN, UserRole.TEACHER],
  enrollCourse: [UserRole.STUDENT],
} as const;
