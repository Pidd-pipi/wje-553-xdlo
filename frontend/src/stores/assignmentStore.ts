import { defineStore } from 'pinia';
import { assignmentApi } from '../api/assignments';
import type { Assignment } from '../types/assignment';
export const useAssignmentStore = defineStore('assignments', { state: () => ({ items: [] as Assignment[] }), actions: { async fetch(courseId?: string) { this.items = await assignmentApi.list(courseId); }, async publish(id: string) { await assignmentApi.update(id, { status: 'PUBLISHED' as Assignment['status'] }); await this.fetch(); } } });
