"""
端到端实测：考勤更正审批
运行方式：
  PYTHONPATH=. python tests/test_correction_flow.py
覆盖：重复提交、越权（他人考勤/学生审批/跨课程教师）、7 天窗口、并发审批、重复处理、驳回原因、刷新一致性。
"""
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

DB_PATH = "/tmp/correction_e2e.db"
BASE = "http://127.0.0.1:38313/api"

# ---------- 结果收集 ----------
results = []
def report(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))

# ---------- HTTP ----------
def http(method, path, token=None, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = None
        return e.code, payload

def login(username, password):
    _, data = http("POST", "/auth/login", body={"username": username, "password": password})
    return data["access_token"]

# ---------- 准备独立数据库与种子 ----------
def seed_database():
    if Path(DB_PATH).exists():
        Path(DB_PATH).unlink()
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.core.database import Base, SessionLocal, engine  # noqa
    from app.core.enums import AttendanceStatus, CourseStatus, UserRole  # noqa
    from app.core.security import hash_password  # noqa
    from app import models  # noqa
    from app.models.attendance import Attendance
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.student import Student
    from app.models.user import User

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin = User(username="admin", password_hash=hash_password("admin123"), full_name="管理员", role=UserRole.ADMIN)
    teacher = User(username="teacher", password_hash=hash_password("teacher123"), full_name="林老师", role=UserRole.TEACHER)
    teacher2 = User(username="teacher2", password_hash=hash_password("teacher123"), full_name="王老师", role=UserRole.TEACHER)
    stu = User(username="student", password_hash=hash_password("student123"), full_name="陈同学", role=UserRole.STUDENT)
    db.add_all([admin, teacher, teacher2, stu]); db.flush()
    s1 = Student(student_no="S1", name="陈同学", user_id=stu.id)
    s2 = Student(student_no="S2", name="周同学")
    c1 = Course(name="Python", code="C1", teacher_id=teacher.id, status=CourseStatus.PUBLISHED)
    c2 = Course(name="Web", code="C2", teacher_id=teacher2.id, status=CourseStatus.PUBLISHED)
    db.add_all([s1, s2, c1, c2]); db.flush()
    db.add(Enrollment(course_id=c1.id, student_id=s1.id))
    own = Attendance(course_id=c1.id, student_id=s1.id, date=date.today(), status=AttendanceStatus.ABSENT, remark="原始缺勤")
    old = Attendance(course_id=c1.id, student_id=s1.id, date=date.today()-timedelta(days=10), status=AttendanceStatus.ABSENT, remark="超窗")
    other = Attendance(course_id=c1.id, student_id=s2.id, date=date.today(), status=AttendanceStatus.ABSENT, remark="他人")
    cross = Attendance(course_id=c2.id, student_id=s1.id, date=date.today(), status=AttendanceStatus.LATE, remark="外课")
    db.add_all([own, old, other, cross]); db.commit()
    ids = {
        "own": str(own.id), "old": str(old.id), "other": str(other.id), "cross": str(cross.id),
        "student_id": str(s1.id), "other_student_id": str(s2.id),
    }
    db.close()
    return ids

def wait_for_port(host, port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False

def main():
    ids = seed_database()
    env = dict(os.environ)
    env["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "38313"],
        cwd=env["PYTHONPATH"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_port("127.0.0.1", 38313):
            print("server failed to start"); return 2
        run_cases(ids)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n==== {passed}/{len(results)} passed ====")
    return 0 if passed == len(results) else 1

def run_cases(ids):
    student = login("student", "student123")
    teacher = login("teacher", "teacher123")
    teacher2 = login("teacher2", "teacher123")
    admin = login("admin", "admin123")

    # 1. 正常提交
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["own"], "expected_status": "PRESENT", "reason": "当天有请假条"})
    report("学生在窗口内提交更正成功(201)", code == 201, f"code={code}")
    cid = data["id"] if code == 201 else None

    # 2. 重复提交（同一考勤，已有待审）-> 整次拒绝
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["own"], "expected_status": "LEAVE", "reason": "重复提交"})
    report("已有待审申请时重复提交被拒(409)，且不产生第二条", code == 409, f"code={code} msg={data and data.get('message')}")
    _, lst = http("GET", "/attendance/corrections", student)
    own_pending = [c for c in lst if c["attendance_id"] == ids["own"]]
    report("该考勤仅有 1 条申请", len(own_pending) == 1, f"count={len(own_pending)}")

    # 3. 超过 7 天窗口
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["old"], "expected_status": "PRESENT"})
    report("超过考勤后 7 天提交被拒(400)", code == 400, f"code={code} msg={data and data.get('message')}")

    # 4. 越权：为他人考勤提交
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["other"], "expected_status": "PRESENT"})
    report("学生为他人考勤提交被拒(403)", code == 403, f"code={code} msg={data and data.get('message')}")

    # 5. 越权：学生尝试批准
    code, data = http("POST", f"/attendance/corrections/{cid}/approve", student, {"remark": None})
    report("学生批准申请被拒(403)", code == 403, f"code={code}")

    # 6. 越权：非任课教师批准（teacher2 不教该课程）
    code, data = http("POST", f"/attendance/corrections/{cid}/approve", teacher2, {"remark": None})
    report("非任课教师批准被拒(403)", code == 403, f"code={code} msg={data and data.get('message')}")

    # 7. 驳回必须填写原因（用 teacher2 的课程申请先造一条？此处直接对 cid 空原因驳回 by teacher）
    code, data = http("POST", f"/attendance/corrections/{cid}/reject", teacher, {"reason": "   "})
    report("空白驳回原因被拒(422/400)", code in (400, 422), f"code={code}")

    # 8. 并发审批：teacher 与 admin 同时批准同一条，只能成功一次
    box = {}
    barrier = threading.Barrier(2)
    def approve(token, who):
        barrier.wait()
        box[who] = http("POST", f"/attendance/corrections/{cid}/approve", token, {"remark": f"{who} 批准"})
    t1 = threading.Thread(target=approve, args=(teacher, "teacher"))
    t2 = threading.Thread(target=approve, args=(admin, "admin"))
    t1.start(); t2.start(); t1.join(); t2.join()
    codes = sorted([box["teacher"][0], box["admin"][0]])
    success = [c for c in codes if c == 200]
    conflict = [c for c in codes if c == 409]
    report("并发审批：恰好一个成功(200)、一个冲突(409)", len(success) == 1 and len(conflict) == 1, f"codes={codes}")

    # 9. 失败方不得改动考勤；成功方更新了状态+备注
    _, atts = http("GET", "/attendance", admin)
    own_att = next(a for a in atts if a["id"] == ids["own"])
    report("批准后考勤状态更新为 PRESENT", own_att["status"] == "PRESENT", f"status={own_att['status']}")
    report("批准后考勤备注已留痕", own_att["remark"] and "更正通过" in own_att["remark"], f"remark={own_att['remark']}")
    report("考勤记录关联申请状态为 APPROVED（刷新一致）", own_att["correction_status"] == "APPROVED", f"corr={own_att['correction_status']}")

    # 10. 对已批准申请再次驳回 / 再次批准 -> 409
    code_again_app, _ = http("POST", f"/attendance/corrections/{cid}/approve", admin, {"remark": "重复"})
    code_again_rej, _ = http("POST", f"/attendance/corrections/{cid}/reject", admin, {"reason": "重复驳回"})
    report("重复处理(再批准/再驳回)均被拒(409)", code_again_app == 409 and code_again_rej == 409,
           f"approve={code_again_app} reject={code_again_rej}")
    _, atts2 = http("GET", "/attendance", admin)
    own_att2 = next(a for a in atts2 if a["id"] == ids["own"])
    report("重复处理后考勤状态未被改动", own_att2["status"] == "PRESENT" and own_att2["remark"] == own_att["remark"],
           f"status={own_att2['status']}")

    # 11. 驳回流程：对另一条考勤（跨课程记录 cross 由 teacher2 任教，teacher 无权；这里用学生再提一条其他记录）
    #     学生为 cross（teacher2 课程）提交，teacher2 驳回并保留原因
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["cross"], "expected_status": "PRESENT", "reason": "我没迟到"})
    report("学生为跨课程记录提交成功(201)", code == 201, f"code={code}")
    cid2 = data["id"] if code == 201 else None
    # 任课教师之外的 teacher 无权驳回
    code_forbidden, _ = http("POST", f"/attendance/corrections/{cid2}/reject", teacher, {"reason": "越权驳回"})
    report("非任课教师驳回他人课程申请被拒(403)", code_forbidden == 403, f"code={code_forbidden}")
    code_rej, rej_data = http("POST", f"/attendance/corrections/{cid2}/reject", teacher2, {"reason": "监控显示迟到 15 分钟"})
    report("任课教师驳回成功(200)", code_rej == 200, f"code={code_rej}")
    report("驳回原因被保留", code_rej == 200 and rej_data.get("review_remark") == "监控显示迟到 15 分钟",
           f"review_remark={rej_data.get('review_remark') if code_rej==200 else None}")

    # 12. 驳回不改考勤
    _, atts3 = http("GET", "/attendance", teacher2)
    cross_att = next(a for a in atts3 if a["id"] == ids["cross"])
    report("驳回后考勤状态保持 LATE 不变", cross_att["status"] == "LATE", f"status={cross_att['status']}")
    report("驳回后申请状态为 REJECTED（刷新一致）", cross_att["correction_status"] == "REJECTED", f"corr={cross_att['correction_status']}")

    # 13. 驳回后（已无待审）可再次提交
    code, data = http("POST", "/attendance/corrections", student,
                      {"attendance_id": ids["cross"], "expected_status": "LEAVE", "reason": "有假条"})
    report("驳回后允许重新提交(201)", code == 201, f"code={code}")
    cid3 = data["id"] if code == 201 else None

    # 14. 数据隔离：学生在列表里看不到别人的申请；教师列表只含自己课程
    _, stu_list = http("GET", "/attendance/corrections", student)
    report("学生只能看到自己的申请", all(c["student_id"] == ids["student_id"] for c in stu_list) and len(stu_list) >= 3,
           f"count={len(stu_list)}")
    _, t_list = http("GET", "/attendance/corrections", teacher)
    report("教师只能看到自己课程的申请", all(c["course_name"] == "Python" for c in t_list) and len(t_list) >= 1,
           f"count={len(t_list)}")
    _, t2_list = http("GET", "/attendance/corrections", teacher2)
    report("teacher2 只看到 Web 课程申请", all(c["course_name"] == "Web" for c in t2_list) and len(t2_list) >= 2,
           f"count={len(t2_list)}")

    # 15. 审计留痕
    _, logs = http("GET", "/audit/logs", admin)
    actions = {l["action"] for l in logs}
    needed = {"attendance_correction.create", "attendance_correction.approve", "attendance_correction.reject"}
    report("审批三类操作均写入审计日志", needed.issubset(actions), f"actions={sorted(actions)}")

    # 16. 未登录访问被拒
    code, _ = http("GET", "/attendance/corrections")
    report("未携带令牌访问被拒(401)", code == 401, f"code={code}")

if __name__ == "__main__":
    sys.exit(main())
