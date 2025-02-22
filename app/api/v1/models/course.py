from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v1.models.basemodel import BaseModel, lecturer_course_association, student_course_association
from app.api.v1.db.db_conn import Base
class Course(BaseModel, Base):
    __tablename__ = 'courses'
    
    coursecode = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    department = relationship("Department", back_populates="courses")
    lecturers = relationship("Lecturer", secondary=lecturer_course_association, back_populates="courses")
    students = relationship("Student", secondary=student_course_association, back_populates="courses")
    attendances = relationship("Attendance", back_populates="course")