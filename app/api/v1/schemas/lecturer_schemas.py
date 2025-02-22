from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Base Schema for Lecturer
class LecturerBase(BaseModel):
    lecturername: str = Field(min_length=1)
    lectureremail: EmailStr = Field(min_length=2)
    departmentname: str = Field(min_length=1)

# Schema for creating a new Lecturer
class LecturerCreate(LecturerBase):
    fingerprint: str = Field(min_length=10)
    password: str = Field(min_length=8)

# Schema for updating Lecturer information
class LecturerUpdate(BaseModel):
    lecturerid: str =  Field(min_length=1)
    lectureremail: Optional[EmailStr] = Field(min_length=2)
    lecturerphone: Optional[str] = Field(min_length=1)
    departmentname: Optional[int] = Field(min_length=1)

# Schema for updating a Lecturer password
class LecturerResetPassword(BaseModel):
    lectureremail: EmailStr = Field(min_length=1)
    newPassword: str = Field(min_length=8)
    fingerprint: str = Field(min_length=10)

# Schema for OTP request
class LecturerGetOTP(BaseModel):
    lectureremail: EmailStr = Field(min_length=2)
    fingerprint: str = Field(min_length=10)

# Schema for Lecturer login
class LecturerLogin(BaseModel):
    lectureremail: EmailStr = Field(min_length=1)
    password: str = Field(min_length=8)
    fingerprint: str = Field(min_length=10)

class LecturerDelete(BaseModel):
    lectureremail: EmailStr = Field(min_length=1)
    fingerprint: str = Field(min_length=10)

class LecturersFilter(BaseModel):
    departmentname: Optional[str] = None
    facultyname: Optional[str] = None
    coursename: Optional[str] = None

class LectFilter(BaseModel):
    lecturername: str = Field(min_length=1)
    departmentname: Optional[str] = None
    facultyname: Optional[str] = None
    coursename: Optional[str] = None
class ValidateOTP(BaseModel):
    email: EmailStr = Field(min_length=2)
    otp: str = Field(min_length=6)
    fingerprint: str = Field(min_length=10)
    otp: str = Field(min_length=6)         