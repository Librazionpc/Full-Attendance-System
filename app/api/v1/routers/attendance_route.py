from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.attendace_schemas import (AttendanceCreate, 
    AttendanceDelete,  AttendanceUpdate, StartAttendance,
    AddStudent, DelStudent
)
from app.api.v1.services.auth_services.attendance_auth_serivce import AttendanceAuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.db.db_conn import get_db
from app.api.v1.utils.jwt import JWTUtils  # Import updated JWTUtils
from typing import List

attendace_router = APIRouter()

def admin_required(user: dict = Depends(JWTUtils.get_current_user)):
    """Ensure only admins or lecturers can access."""
    if user["role"] not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return user

@attendace_router.post('/create')
async def create_faculty_admin(
    data: AttendanceCreate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    new_dept = await AttendanceAuthService.register_Attendance(data.dict(), session)
    return new_dept

@attendace_router.post("/attendance/start/{course_id}")
async def start_attendance_session(
    data: StartAttendance,
    course_id: int,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    """
    Lecturer starts the attendance session for the course.
    This will trigger face and fingerprint recognition for all students.
    Lecturer's email is validated to ensure they are the course owner.
    """
    result = await AttendanceAuthService.start_attendance_session(data.dict(), session)
    return result

@attendace_router.get("/attendances/student/{student_id}")
async def get_student_attendance(
    student_id: int,
    session: AsyncSession = Depends(get_db)
):
    return await AttendanceAuthService.get_attendance(student_id, session)

@attendace_router.get("/attendances/course/{course_id}")
async def get_course_attendance(
    course_id: int,
    session: AsyncSession = Depends(get_db)
):
    return await AttendanceAuthService.get_attendance_for_course(course_id, session)

@attendace_router.get("/attendances/student/{student_id}/course/{course_id}",)
async def get_student_attendance_for_course(
    student_id: int,
    course_id: int,
    session: AsyncSession = Depends(get_db)
):
    return await AttendanceAuthService.get_student_attendance_for_course(student_id, course_id, session)

@attendace_router.post("/add-student/{lecturer_id}", response_model=dict)
async def add_student_to_course(
    lecturer_id: int,
    data: AddStudent,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    result = await AttendanceAuthService.add_student_to_attendance(data.dict(), session, lecturer_id)
    return {"message": f"Student {data.studentemail} added to course {data.coursecode}"}

@attendace_router.delete("/remove-student/{lecturer_id}", response_model=dict)
async def remove_student_from_course(
    lecturer_id: int,
    data: DelStudent,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    result = await AttendanceAuthService.remove_student_from_attendance(data.dict(), session, lecturer_id)
    return {"message": f"Student {data.studentemail} removed from course {data.coursecode}"}

@attendace_router.post("/update")
async def update_attendance(
    data: AttendanceUpdate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    updated_attendance = await AttendanceAuthService.update_attendance(data.dict(), session)
    return updated_attendance

@attendace_router.delete('/delete')
async def delete_attendance(
    data: AttendanceDelete,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    return await AttendanceAuthService.delete_attendance(data.dict(), session)
