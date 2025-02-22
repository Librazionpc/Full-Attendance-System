from fastapi import FastAPI
from app.api.v1.routers.faculty_admin import faculty_router
from app.api.v1.routers.dept_route import router as dept_router
from app.api.v1.routers.course_route import router as course_router
from app.api.v1.routers.lecturer_route import router as lecturer_router
from app.api.v1.routers.student_route import router as student_router
from app.api.v1.routers.attendance_route import attendace_router

version = "v1"
app = FastAPI(title="Fingerprint Attendance System", version=version)

# app.include_router(faculty_router, prefix="/faculty_admin", tags=["Faculty Admin"])
app.include_router(dept_router, prefix="/department", tags=["Department"])
app.include_router(course_router, prefix="/course", tags=["Course"])
app.include_router(lecturer_router, prefix="/lecturer", tags=["Lecturer"])
app.include_router(student_router, prefix="/student", tags=["Student"])
app.include_router(attendace_router, prefix="/attendance", tags=["Attendance"])