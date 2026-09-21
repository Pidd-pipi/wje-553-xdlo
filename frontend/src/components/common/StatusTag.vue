<script setup lang="ts">
const props = defineProps<{ status: string; type: 'course' | 'assignment' | 'attendance' }>();
const maps: Record<string, string> = { DRAFT: 'info', PUBLISHED: 'success', IN_PROGRESS: 'warning', COMPLETED: 'success', ARCHIVED: 'info', CLOSED: 'info', PENDING: 'warning', PRESENT: 'success', ABSENT: 'danger', LATE: 'warning', LEAVE: 'primary', APPROVED: 'success', REJECTED: 'danger' };
const labels: Record<string, string> = { PENDING: '待审批', PRESENT: '出勤', ABSENT: '缺勤', LATE: '迟到', LEAVE: '请假', APPROVED: '已批准', REJECTED: '已驳回' };
</script><template><el-tag :type="maps[props.status] || 'info'" effect="light">{{ labels[props.status] || props.status }}</el-tag></template>
