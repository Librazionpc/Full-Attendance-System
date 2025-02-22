from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from app.api.v1.models.basemodel import BaseModel, Base
from sqlalchemy.orm import relationship

class FacultyAdmin(BaseModel, Base):
    __tablename__ = 'facultyadmins'
    
    facultyname = Column(String(50), nullable=False)
    facultyemail = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    otp = Column(Integer, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    fingerprint = Column(String, nullable=False)
    facultyphone = Column(String(50), nullable=False)
    facultyaddress = Column(String(50), nullable=False)
    department = relationship("Department", back_populates='facultyadmin')
    
    
    
    