# CampusHub / wjecampus

校园培训管理系统，按 Vue 3 + TypeScript + Element Plus + Vite + Pinia + FastAPI + SQLAlchemy + PostgreSQL + JWT + Docker Compose 实现前后端分离结构。

## 端口

- 前端：http://localhost:38203
- 后端：http://localhost:38303
- 健康检查：http://localhost:38303/api/health

## 验证账号

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | admin | admin123 |
| 教师 | teacher | teacher123 |
| 学生 | student | student123 |

## 本地启动

后端本地默认使用 SQLite，便于无 PostgreSQL 时验证：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python seeds/seed_all.py
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 38303
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## Docker Compose 启动

```bash
docker compose up --build
docker compose down
```

Docker Compose 启动后会自动执行 `PYTHONPATH=. python seeds/seed_all.py` 初始化演示账号与课程数据。

## 架构链路

每个核心实体均拆分为 DB/Model/Service/Controller/API/Store/组件链路：

- Course：`backend/app/models/course.py` -> `backend/app/services/course_service.py` -> `backend/app/api/courses.py` -> `frontend/src/api/courses.ts` -> `frontend/src/stores/courseStore.ts` -> `frontend/src/pages/Courses.vue`、`frontend/src/pages/CourseDetail.vue`
- Student：`backend/app/models/student.py` -> `backend/app/services/student_service.py` -> `backend/app/api/students.py` -> `frontend/src/api/students.ts` -> `frontend/src/stores/studentStore.ts` -> `frontend/src/components/common/StudentAvatar.vue`
- Assignment：`backend/app/models/assignment.py` -> `backend/app/services/assignment_service.py` -> `backend/app/api/assignments.py` -> `frontend/src/api/assignments.ts` -> `frontend/src/stores/assignmentStore.ts` -> `frontend/src/pages/Assignments.vue`
- Attendance：`backend/app/models/attendance.py` -> `backend/app/services/attendance_service.py` -> `backend/app/api/attendance.py` -> `frontend/src/api/attendance.ts` -> `frontend/src/stores/attendanceStore.ts` -> `frontend/src/pages/Attendance.vue`
- AuditLog：`backend/app/models/audit_log.py` -> `backend/app/services/audit_service.py` -> `backend/app/api/audit.py` -> `frontend/src/api/audit.ts` -> `frontend/src/pages/AuditLog.vue`

## 枚举使用位置清单

| 枚举 | 使用位置 |
|---|---|
| `AssignmentType` | 后端: `app/core/enums.py`, `app/models/assignment.py`, `app/schemas/assignment_schema.py`, `app/services/assignment_service.py`, `app/api/assignments.py`; 前端: `src/constants/enums.ts`, `src/types/assignment.d.ts`, `src/api/assignments.ts`, `src/stores/assignmentStore.ts`, `src/pages/Assignments.vue`, `src/components/common/StatusTag.vue` |
| `AttendanceStatus` | 后端: `app/core/enums.py`, `app/models/attendance.py`, `app/schemas/attendance_schema.py`, `app/services/attendance_service.py`, `app/api/attendance.py`; 前端: `src/constants/enums.ts`, `src/types/attendance.d.ts`, `src/api/attendance.ts`, `src/stores/attendanceStore.ts`, `src/pages/Attendance.vue`, `src/components/common/StatusTag.vue` |
| `CourseStatus` | 后端: `app/core/enums.py`, `app/models/course.py`, `app/schemas/course_schema.py`, `app/services/course_service.py`, `app/api/courses.py`; 前端: `src/constants/enums.ts`, `src/types/course.d.ts`, `src/api/courses.ts`, `src/stores/courseStore.ts`, `src/pages/Courses.vue`, `src/pages/CourseDetail.vue`, `src/components/common/StatusTag.vue` |
| `UserRole` | 后端: `app/core/enums.py`, `app/models/user.py`, `app/core/permissions.py`, `app/middlewares/auth_middleware.py`, `app/services/auth_service.py`, `app/api/auth.py`; 前端: `src/constants/enums.ts`, `src/constants/permissions.ts`, `src/types/common.d.ts`, `src/stores/authStore.ts`, `src/hooks/useAuth.ts`, `src/router/index.ts`, `src/directives/v-permission.ts` |

## 说明

- 前端通过 `/api` 访问后端；Docker 环境由 Nginx 反向代理到 `backend:38303`。
- `docker-compose.yml` 未使用 `version:` 字段，顶层 `name: wjecampus`，容器名带 `${COMPOSE_PROJECT_NAME:-wjecampus}` 前缀。
- `.env.example` 可复制为 `.env` 后按部署环境调整。
