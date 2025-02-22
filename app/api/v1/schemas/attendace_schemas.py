from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class AttendanceBase(BaseModel):
    course_name: str
    course_code: str
    dpartment_name: UUID
    lecturer_name: str

class AttendanceCreate(AttendanceBase):
    pass
class AttendanceUpdate(BaseModel):
    student_id: Optional[UUID]
    course_id: Optional[UUID]
    department_id: Optional[UUID]
    ispresent: Optional[bool]

    class Config:
        orm_mode = True  # Ensure compatibility with ORM models
class AddStudent(BaseModel):
    coursecode: str
    studentemail: EmailStr
    
class DelStudent(BaseModel):
    coursecode: str
    studentemail: EmailStr
class StartAttendance(BaseModel):
    coursecode : str
    lectureremail: str
    
class AttendanceDelete(BaseModel):
    attendance_id : UUID
