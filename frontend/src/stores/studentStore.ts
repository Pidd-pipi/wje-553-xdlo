import { defineStore } from 'pinia';
import { studentApi } from '../api/students';
import type { Student } from '../types/student';
export const useStudentStore = defineStore('students', { state: () => ({ items: [] as Student[] }), actions: { async fetch() { this.items = await studentApi.list(); } } });
