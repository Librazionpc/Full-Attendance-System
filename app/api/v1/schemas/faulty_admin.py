from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


# Schema for creating a new FacultyAdmin
class FacultyAdminBase(BaseModel):
    facultyname: str = Field(min_length=1)
    facultyemail: EmailStr = Field(min_length=1)
    facultyphone: str = Field(min_length=2)
    facultyaddress: str = Field(min_length=1)

    class Config:
        orm_mode = True

class FacultyAdminCreate(FacultyAdminBase):
    password: str = Field(min_length=1)
    fingerprint: str = Field(min_length=9)

# Schema for updating a FacultyAdmin
class FacultyResetPassword(BaseModel):
    facultyemail: EmailStr = Field(min_length=2)
    newPassword: str = Field(min_length=1)
    fingerprint: str = Field(min_length=9)

class FacultyAdminSearch(BaseModel):
    facultyname: str = Field(min_length=1)

class FacultyGetOTP(BaseModel):
    facultyemail : EmailStr = Field(min_length=2)
    fingerprint: str = Field(min_length=9)
class FacultyAdminLogin(BaseModel):
    facultyemail: EmailStr = Field(min_length=2)
    password: str = Field(min_length=1)
    fingerprint: str = Field(min_length=9)
    
class FacultyValidateOTP(BaseModel):
    facultyemail: EmailStr = Field(min_length=2)
    otp: int = Field(min_length=6)
    fingerprint: str = Field(min_length=9)
    
class FacultyAdminOut(BaseModel):
    id: uuid.UUID
    created_at: Optional[str]
    updated_at: Optional[str]
    facultyname: str
    facultyemail: str
    facultyphone: str
    facultyaddress: str
    fingerprint: str
    

    class Config:
        orm_mode = True
