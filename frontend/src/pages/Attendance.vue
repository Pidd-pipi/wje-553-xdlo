<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import StatusTag from '../components/common/StatusTag.vue';
import { useAuth } from '../hooks/useAuth';
import { useAttendance } from '../hooks/useAttendance';
import { AttendanceStatus, CorrectionStatus, type AttendanceStatus as TAttendanceStatus } from '../constants/enums';
import { formatDate } from '../utils/format';
import type { Attendance } from '../types/attendance';

const { isAdmin, isTeacher, isStudent } = useAuth();
const canReview = computed(() => isAdmin.value || isTeacher.value);
const {
  attendance, corrections, fetchAttendance, changeAttendanceStatus,
  fetchCorrections, submitCorrection, approveCorrection, rejectCorrection,
} = useAttendance();

const statusOptions = [
  { label: '出勤', value: AttendanceStatus.PRESENT },
  { label: '缺勤', value: AttendanceStatus.ABSENT },
  { label: '迟到', value: AttendanceStatus.LATE },
  { label: '请假', value: AttendanceStatus.LEAVE },
];

const pendingCorrections = computed(() => corrections.value.filter((c) => c.status === CorrectionStatus.PENDING));
const handledCorrections = computed(() => corrections.value.filter((c) => c.status !== CorrectionStatus.PENDING));

async function refresh() {
  await Promise.all([fetchAttendance(), fetchCorrections()]);
}
onMounted(refresh);

// ---------- 学生：提交更正 ----------
const dialogVisible = ref(false);
const submitting = ref(false);
const form = reactive<{ attendanceId: string; expectedStatus: TAttendanceStatus | ''; reason: string }>({
  attendanceId: '', expectedStatus: '', reason: '',
});
const targetRow = ref<Attendance | null>(null);

function openCorrection(row: Attendance) {
  targetRow.value = row;
  form.attendanceId = row.id;
  form.expectedStatus = row.status === AttendanceStatus.ABSENT ? AttendanceStatus.PRESENT : '';
  form.reason = '';
  dialogVisible.value = true;
}

async function confirmSubmit() {
  if (!form.expectedStatus) {
    ElMessage.warning('请选择更正后的状态');
    return;
  }
  submitting.value = true;
  try {
    await submitCorrection(form.attendanceId, form.expectedStatus as TAttendanceStatus, form.reason || undefined);
    ElMessage.success('更正申请已提交，等待审批');
    dialogVisible.value = false;
    await refresh();
  } catch {
    /* 错误提示已由拦截器统一处理 */
  } finally {
    submitting.value = false;
  }
}

// ---------- 教师/管理员：批准 / 驳回 ----------
async function approve(id: string) {
  try {
    const { value } = await ElMessageBox.prompt('可填写审批备注（选填）', '批准考勤更正', {
      confirmButtonText: '确认批准', cancelButtonText: '取消', inputType: 'textarea', inputValue: '',
    });
    await approveCorrection(id, value || undefined);
    ElMessage.success('已批准，考勤状态已更新');
    await refresh();
  } catch (err) {
    if (err !== 'cancel' && err !== 'close') ElMessage.error('批准失败');
  }
}

async function reject(id: string) {
  try {
    const { value } = await ElMessageBox.prompt('驳回必须填写原因', '驳回考勤更正', {
      confirmButtonText: '确认驳回', cancelButtonText: '取消', inputType: 'textarea',
      inputPlaceholder: '请输入驳回原因',
      inputValidator: (v: string) => (v && v.trim() ? true : '驳回必须填写原因'),
    });
    await rejectCorrection(id, value.trim());
    ElMessage.success('已驳回，原因已保留');
    await refresh();
  } catch (err) {
    if (err !== 'cancel' && err !== 'close') ElMessage.error('驳回失败');
  }
}

async function markPresent(row: Attendance) {
  await changeAttendanceStatus(row.id, AttendanceStatus.PRESENT);
  await refresh();
}
async function markAbsent(row: Attendance) {
  await changeAttendanceStatus(row.id, AttendanceStatus.ABSENT);
  await refresh();
}
</script>

<template>
  <section class="page">
    <header>
      <h2>考勤管理</h2>
    </header>

    <!-- 考勤记录 -->
    <el-table :data="attendance" border>
      <el-table-column prop="course_name" label="课程" min-width="160" />
      <el-table-column prop="student_name" label="学生" min-width="100" />
      <el-table-column label="日期" min-width="110">
        <template #default="{ row }">{{ formatDate(row.date) }}</template>
      </el-table-column>
      <el-table-column label="考勤状态" min-width="100">
        <template #default="{ row }"><StatusTag :status="row.status" type="attendance" /></template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
      <el-table-column label="更正申请" min-width="120">
        <template #default="{ row }">
          <el-tag v-if="!row.correction_status" type="info" effect="plain">未申请</el-tag>
          <StatusTag v-else :status="row.correction_status" type="attendance" />
        </template>
      </el-table-column>
      <el-table-column v-if="isStudent" label="我的操作" min-width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small" type="primary"
            :disabled="row.correction_status === 'PENDING'"
            @click="openCorrection(row)"
          >
            {{ row.correction_status === 'PENDING' ? '待审批中' : '申请更正' }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column v-if="canReview" label="教师操作" min-width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="markPresent(row)">出勤</el-button>
          <el-button size="small" type="danger" plain @click="markAbsent(row)">缺勤</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 学生：最近申请结果 -->
    <template v-if="isStudent">
      <el-card v-for="c in corrections" :key="c.id" class="correction-card" shadow="never">
        <div class="correction-line">
          <strong>{{ c.course_name }}</strong>
          <span>{{ formatDate(c.attendance_date) }}</span>
          <StatusTag :status="c.status" type="attendance" />
          <span>申请状态：<StatusTag :status="c.expected_status" type="attendance" /></span>
        </div>
        <p class="muted">申请理由：{{ c.reason || '（未填写）' }}</p>
        <p v-if="c.status === 'REJECTED'" class="reject-text">驳回原因：{{ c.review_remark }}</p>
        <p v-if="c.status === 'APPROVED'" class="approve-text">审批备注：{{ c.review_remark || '（无）' }}，当前考勤状态：{{ c.current_status }}</p>
      </el-card>
    </template>

    <!-- 教师/管理员：审批面板 -->
    <template v-if="canReview">
      <h3>待审批更正（{{ pendingCorrections.length }}）</h3>
      <el-table :data="pendingCorrections" border>
        <el-table-column prop="course_name" label="课程" min-width="150" />
        <el-table-column prop="student_name" label="学生" min-width="90" />
        <el-table-column label="考勤日期" min-width="110">
          <template #default="{ row }">{{ formatDate(row.attendance_date) }}</template>
        </el-table-column>
        <el-table-column label="当前状态" min-width="90">
          <template #default="{ row }"><StatusTag :status="row.current_status" type="attendance" /></template>
        </el-table-column>
        <el-table-column label="期望状态" min-width="90">
          <template #default="{ row }"><StatusTag :status="row.expected_status" type="attendance" /></template>
        </el-table-column>
        <el-table-column prop="reason" label="申请理由" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" min-width="170" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="approve(row.id)">批准</el-button>
            <el-button size="small" type="danger" @click="reject(row.id)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>

      <h3>已处理申请</h3>
      <el-table :data="handledCorrections" border>
        <el-table-column prop="course_name" label="课程" min-width="150" />
        <el-table-column prop="student_name" label="学生" min-width="90" />
        <el-table-column label="结果" min-width="100">
          <template #default="{ row }"><StatusTag :status="row.status" type="attendance" /></template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="审批人" min-width="90" />
        <el-table-column prop="review_remark" label="审批备注 / 驳回原因" min-width="200" show-overflow-tooltip />
      </el-table>
    </template>

    <!-- 学生提交弹窗 -->
    <el-dialog v-model="dialogVisible" title="申请考勤更正" width="440px">
      <el-form label-width="92px">
        <el-form-item label="课程日期">
          <span>{{ targetRow?.course_name }} · {{ formatDate(targetRow?.date) }}（当前：{{ targetRow?.status }}）</span>
        </el-form-item>
        <el-form-item label="更正为" required>
          <el-select v-model="form.expectedStatus" placeholder="选择期望状态" style="width: 100%">
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="更正理由">
          <el-input v-model="form.reason" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="请说明更正原因（选填）" />
        </el-form-item>
        <p class="muted">规则：考勤后 7 天内仅可提交一次，已有待审申请时不能重复提交。</p>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmSubmit">提交申请</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.correction-card { margin-top: 12px; }
.correction-line { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.muted { color: #64756f; font-size: 13px; margin: 8px 0 0; }
.reject-text { color: #c45656; margin: 6px 0 0; }
.approve-text { color: #3b8c6e; margin: 6px 0 0; }
h3 { margin: 22px 0 10px; }
</style>
