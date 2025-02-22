from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.lecturer_schemas import (
    LecturerCreate, LecturerGetOTP, LecturerLogin, 
    LecturerResetPassword, LecturerUpdate, LecturerDelete,
   LecturersFilter, LectFilter, ValidateOTP
)
from app.api.v1.services.auth_services.lecturer_auth_services import LecturerAuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.db.db_conn import get_db
from app.api.v1.utils.jwt import JWTUtils 

router = APIRouter()

def admin_required(user: dict = Depends(JWTUtils.get_current_user)):
    """Ensure only admins can access"""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return user

@router.post("/create")
async def create_lecturer(
    data: LecturerCreate, 
    session: AsyncSession = Depends(get_db),
    # user: dict = Depends(admin_required)
):
    new_lecturer = await LecturerAuthService.register_lecturer(data.dict(), session)
    return new_lecturer

@router.post("/login")
async def login_lecturer(data: LecturerLogin, session: AsyncSession = Depends(get_db)):
    lecturer = await LecturerAuthService.authenticate_lecturer(data.dict(), session)
    return lecturer

@router.post("/validate_email")
async def validate_email(data: LecturerGetOTP, session: AsyncSession = Depends(get_db)):
    await LecturerAuthService.validate_email(data.dict(), session)

@router.post("/reset_password")
async def reset_password(data: LecturerResetPassword, session: AsyncSession = Depends(get_db)):
    lecturer = await LecturerAuthService.reset_password(data.dict(), session)
    return lecturer

@router.put("/update/{lecturer_id}")
async def update_lecturer(data: LecturerUpdate, session: AsyncSession = Depends(get_db)):
    updated_lecturer = await LecturerAuthService.update_lecturer(data.dict(), session)
    return updated_lecturer

@router.post("/details/{lecturers_filter}")
async def get_lecturers_filter(data: LecturersFilter, session: AsyncSession = Depends(get_db)):
    lecturer_details = await LecturerAuthService.get_lecturer_details(data.dict(), session)
    return lecturer_details

@router.post("/lecturer_filter")
async def get_lecturer_filter(data: LectFilter, session: AsyncSession = Depends(get_db)):
    lecturer_details = await LecturerAuthService.get_lecturer_filter(data.dict(), session)
    return lecturer_details

@router.post("/validate_otp")
async def validate_otp(data: ValidateOTP, session: AsyncSession = Depends(get_db)):
    await LecturerAuthService.validate_otp(data.dict(), session)
    return {"message": "OTP validated successfully"}

@router.delete("/delete", response_model=dict)
async def delete_lecturer(
    data: LecturerDelete, 
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    await LecturerAuthService.delete(data.dict(), session)
    return {"message": "Lecturer deleted successfully"}