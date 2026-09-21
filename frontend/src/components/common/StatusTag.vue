<script setup lang="ts">
const props = defineProps<{ status: string; type: 'course' | 'assignment' | 'attendance' }>();
const maps: Record<string, string> = { DRAFT: 'info', PUBLISHED: 'success', IN_PROGRESS: 'warning', COMPLETED: 'success', ARCHIVED: 'info', CLOSED: 'info', PENDING: 'info', PRESENT: 'success', ABSENT: 'danger', LATE: 'warning', LEAVE: 'primary' };
</script><template><el-tag :type="maps[props.status] || 'info'" effect="light">{{ props.status }}</el-tag></template>