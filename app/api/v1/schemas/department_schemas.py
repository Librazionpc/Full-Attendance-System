from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid


# Schema for creating a new Department
class DepartmentCreate(BaseModel):
    departmentname: str = Field(min_length=1)
    department_email: EmailStr = Field(min_length=3)
    # facultyname: str = Field(min_length=1)
    fingerprint: str = Field(min_length=10)
    password: str = Field(min_length=8)

class DepartmentLogin(BaseModel):
    departmentname: str = Field(min_length=1)
    fingerprint: str = Field(min_length=10)
    password: str = Field(min_length=8)

# Schema for updating a Department
class DepartmentUpdate(BaseModel):
    department_id: str = Field(min_length=1)
    departmentname: Optional[str] = Field(min_length=1)
    new_name: Optional[str] = Field(min_length=1) # Correct syntax for Optional[str]
    faultyid: Optional[str] = Field(min_length=1) # Correct type for Optional[uuid.UUID]

class DepartmentDetails(BaseModel):
    departmentname: str = Field(min_length=1)
# Schema for returning a Department's data
