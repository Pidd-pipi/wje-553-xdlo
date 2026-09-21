<script setup lang="ts">
import type { Student } from '../../types/student';
defineProps<{ student: Pick<Student, 'name' | 'student_no' | 'class_name'> }>();
</script><template><div class="student"><el-avatar :size="32">{{ student.name.slice(0,1) }}</el-avatar><span><b>{{ student.name }}</b><small>{{ student.student_no }} · {{ student.class_name || '-' }}</small></span></div></template><style scoped>.student{display:flex;align-items:center;gap:10px}.student span{display:grid}.student small{color:#64748b}</style>