from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v1.models.basemodel import BaseModel
from app.api.v1.models.lecturer import Lecturer
from app.api.v1.models.course import Course
from app.api.v1.db.db_conn import Base
class Department(BaseModel, Base):
    __tablename__ = 'departments'
    
    departmentname = Column(String(50), nullable=False)
    department_email = Column(String(255), nullable=True)
    fingerprint = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    lecturers = relationship(Lecturer, back_populates="department")
    courses = relationship(Course, back_populates="department")
    students = relationship("Student", back_populates="department")
    attendances = relationship("Attendance", back_populates="department")