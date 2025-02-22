from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v1.models.basemodel import BaseModel, lecturer_course_association
from app.api.v1.db.db_conn import Base

class Lecturer(BaseModel, Base):
    __tablename__ = 'lecturers'
    
    lecturername = Column(String(50), nullable=False)
    lectureremail = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    password = Column(String(50), nullable=False)
    fingerprint = Column(String(50), nullable=False)
    department = relationship("Department", back_populates="lecturers")
    courses = relationship("Course", secondary=lecturer_course_association, back_populates="lecturers")
    attendances = relationship("Attendance", back_populates="lecturer")

