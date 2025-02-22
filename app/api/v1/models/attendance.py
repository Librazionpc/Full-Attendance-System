from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.api.v1.models.basemodel import BaseModel
from datetime import datetime
from app.api.v1.db.db_conn import Base

class Attendance(BaseModel, Base):
    __tablename__ = 'attendances'
    
    ispresent = Column(Boolean, nullable=True, default=False)
    timestamp = Column(DateTime, nullable=True, default="No time")
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    lecturer_id = Column(Integer, ForeignKey('lecturers.id'), nullable=False)
    lecturer = relationship("Lecturer", back_populates="attendances")
    students = relationship("Student", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")
    department = relationship("Department", back_populates="attendances")
