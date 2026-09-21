<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import StatusTag from '../components/common/StatusTag.vue';
import { useAttendance } from '../hooks/useAttendance';
import { useAuth } from '../hooks/useAuth';
import { AttendanceStatus, CorrectionStatus } from '../constants/enums';
import type { Attendance, AttendanceCorrection } from '../types/attendance';

const { attendance, corrections, fetchAttendance, changeAttendanceStatus, fetchCorrections, submitCorrection, approveCorrection, rejectCorrection } = useAttendance();
const { user, isStudent, isTeacher, isAdmin } = useAuth();
const refresh = () => Promise.all([fetchAttendance(), fetchCorrections()]);
onMounted(refresh);

const pendingAttendanceIds = computed(() => new Set(corrections.value.filter(c => c.status === CorrectionStatus.PENDING).map(c => c.attendance_id)));
const withinWindow = (day: string) => { const days = (Date.now() - new Date(day + 'T00:00:00').getTime()) / 86400000; return days >= 0 && days <= 7; };
const canSubmit = (row: Attendance) => isStudent.value && !!user.value?.student_id && row.student_id === user.value.student_id && withinWindow(row.date) && !pendingAttendanceIds.value.has(row.id);

const submitDialog = ref(false);
const submitForm = reactive({ attendance_id: '', requested_status: AttendanceStatus.PRESENT as Attendance['status'], reason: '' });
const openSubmit = (row: Attendance) => { submitForm.attendance_id = row.id; submitForm.requested_status = AttendanceStatus.PRESENT; submitForm.reason = ''; submitDialog.value = true; };
const doSubmit = async () => {
  if (!submitForm.reason.trim()) { ElMessage.warning('请填写更正原因'); return; }
  await submitCorrection({ ...submitForm }); ElMessage.success('已提交，等待审批'); submitDialog.value = false;
};

const rejectDialog = ref(false);
const rejectForm = reactive({ id: '', review_comment: '' });
const openReject = (row: AttendanceCorrection) => { rejectForm.id = row.id; rejectForm.review_comment = ''; rejectDialog.value = true; };
const doReject = async () => {
  if (!rejectForm.review_comment.trim()) { ElMessage.warning('驳回必须填写原因'); return; }
  await rejectCorrection(rejectForm.id, rejectForm.review_comment); ElMessage.success('已驳回'); rejectDialog.value = false;
};
const doApprove = async (row: AttendanceCorrection) => { await approveCorrection(row.id); ElMessage.success('已批准，考勤状态已更新'); };
</script>

<template>
  <section class="page">
    <header><h2>考勤管理</h2><el-button v-permission="['ADMIN','TEACHER']" type="primary">一键全部出勤</el-button></header>
    <el-table :data="attendance">
      <el-table-column prop="course_name" label="课程"/>
      <el-table-column prop="student_name" label="学生"/>
      <el-table-column prop="date" label="日期"/>
      <el-table-column label="状态"><template #default="{row}"><StatusTag :status="row.status" type="attendance"/></template></el-table-column>
      <el-table-column prop="remark" label="备注"/>
      <el-table-column label="操作">
        <template #default="{row}">
          <el-button size="small" @click="changeAttendanceStatus(row.id,'PRESENT')" v-permission="['ADMIN','TEACHER']">出勤</el-button>
          <el-button size="small" @click="changeAttendanceStatus(row.id,'ABSENT')" v-permission="['ADMIN','TEACHER']">缺勤</el-button>
          <el-button v-if="canSubmit(row)" size="small" type="warning" @click="openSubmit(row)">申请更正</el-button>
        </template>
      </el-table-column>
    </el-table>

    <header style="margin-top:24px"><h2>考勤更正申请</h2></header>
    <el-table :data="corrections">
      <el-table-column prop="course_name" label="课程"/>
      <el-table-column prop="student_name" label="学生"/>
      <el-table-column prop="attendance_date" label="考勤日期"/>
      <el-table-column label="当前状态"><template #default="{row}"><StatusTag v-if="row.current_status" :status="row.current_status" type="attendance"/></template></el-table-column>
      <el-table-column label="申请改为"><template #default="{row}"><StatusTag :status="row.requested_status" type="attendance"/></template></el-table-column>
      <el-table-column prop="reason" label="申请原因" show-overflow-tooltip/>
      <el-table-column label="审批状态"><template #default="{row}"><StatusTag :status="row.status" type="correction"/></template></el-table-column>
      <el-table-column label="审批意见"><template #default="{row}"><span v-if="row.review_comment">{{ row.review_comment }}</span><span v-else-if="row.status==='REJECTED'" style="color:#f56c6c">原因缺失</span><span v-else>-</span></template></el-table-column>
      <el-table-column prop="reviewer_name" label="审批人"/>
      <el-table-column label="操作" v-if="isTeacher || isAdmin">
        <template #default="{row}">
          <template v-if="row.status==='PENDING'">
            <el-button size="small" type="success" @click="doApprove(row)">批准</el-button>
            <el-button size="small" type="danger" @click="openReject(row)">驳回</el-button>
          </template>
          <span v-else>-</span>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="submitDialog" title="申请考勤更正" width="420px">
      <el-form label-width="90px">
        <el-form-item label="更正为">
          <el-select v-model="submitForm.requested_status" style="width:100%">
            <el-option v-for="s in Object.values(AttendanceStatus)" :key="s" :label="s" :value="s"/>
          </el-select>
        </el-form-item>
        <el-form-item label="申请原因" required>
          <el-input v-model="submitForm.reason" type="textarea" :rows="3" maxlength="500" placeholder="请说明更正原因"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog=false">取消</el-button>
        <el-button type="primary" @click="doSubmit">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rejectDialog" title="驳回更正申请" width="420px">
      <el-form label-width="90px">
        <el-form-item label="驳回原因" required>
          <el-input v-model="rejectForm.review_comment" type="textarea" :rows="3" maxlength="500" placeholder="驳回必须填写原因"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialog=false">取消</el-button>
        <el-button type="danger" @click="doReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </section>
</template>
