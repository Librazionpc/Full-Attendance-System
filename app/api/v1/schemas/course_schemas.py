from pydantic import BaseModel, Field
from typing import Optional
import uuid


# Schema for creating a new Course
class CourseCreate(BaseModel):
    coursename: str = Field(min_length=1)
    coursecode: str = Field(min_length=1)
    departmentname: str = Field(min_length=1)


# Schema for updating a Course
class CourseUpdate(BaseModel):
    new_name: Optional[str] = Field(min_length=1)
    new_course_code: Optional[str] = Field(min_length=1)
    new_deptartmentname: Optional[str] = Field(min_length=1)

class CourseDelete(BaseModel):
    coursecode: str = Field(min_length=1)

# Schema for returning a Course's data
class CourseDetails(BaseModel):
    coursecode: str = Field(min_length=1)
    departmentname: str = Field(min_length=1)