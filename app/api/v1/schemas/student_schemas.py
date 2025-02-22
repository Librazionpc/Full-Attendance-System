from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid
# Base Schema for Student (excluding fingerprint)
class StudentBase(BaseModel):
    studentname: str = Field(min_length=1)
    studentemail: EmailStr = Field(min_length=3)
    student_matric_no: str = Field(min_length=12)
    studentphone: str = Field(min_length=11)
    departmentname: str = Field(min_length=1)

# Schema for creating a new Student
class StudentCreate(StudentBase):
    password: str = Field(min_length=8)
    fingerprint: str = Field(min_length=10)

# Schema for updating a Student password
class StudentResetPassword(BaseModel):
    student_matric_no: EmailStr = Field(min_length=1)
    newPassword: str = Field(min_length=8)
    fingerprint: str = Field(min_length=10)

# Schema for OTP request
class StudentGetOTP(BaseModel):
    student_matric_no: EmailStr = Field(min_length=12)
    fingerprint: str = Field(min_length=3)

# Schema for Student login
class StudentLogin(BaseModel):
    studentemail: Optional[EmailStr] = Field(min_length=1)
    student_matric_no: Optional[str] = Field(min_length=12)
    password: str = Field(min_length=8)
    fingerprint: str = Field(min_length=1)

class StudentUpdate(StudentBase):
    student_id: uuid.UUID

class StudentDelete(BaseModel):
    studentemail: EmailStr


class StudentsFilter(BaseModel):
    departmentname: Optional[str] = None
    facultyname: Optional[str] = None
    coursename: Optional[str] = None

class StudFilter(BaseModel):
    student_matric_no : str = Field(min_length=12)
    departmentname: Optional[str] = None
    facultyname: Optional[str] = None
    coursename: Optional[str] = None
    
class ValidateOTP(BaseModel):
    studentemail: EmailStr = Field(min_length=2)
    otp: str = Field(min_length=6)
    fingerprint: str = Field(min_length=10)