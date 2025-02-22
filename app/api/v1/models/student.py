from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v1.models.basemodel import BaseModel, student_course_association
from app.api.v1.models.attendance import Attendance
from app.api.v1.db.db_conn import Base

class Student(BaseModel, Base):
    __tablename__ = 'students'
    
    student_name = Column(String(50), nullable=False)
    student_email = Column(String(50), nullable=False)
    student_phone = Column(String(50), nullable=False)
    student_matric_no = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    fingerprint = Column(String(255), nullable=True)
    fingerprint_map = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    attendances = relationship(Attendance, back_populates="students")
    department = relationship("Department", back_populates="students")
    courses = relationship("Course", secondary=student_course_association, back_populates="students")
