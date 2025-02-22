from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.student_schemas import StudentCreate, StudentLogin, StudentResetPassword, StudentUpdate
from app.api.v1.services.auth_services.student_auth_services import StudentAuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.db.db_conn import get_db

router = APIRouter()

@router.post("/create")
async def create_student(data: StudentCreate, session: AsyncSession = Depends(get_db)):
    # Pass the data as a dictionary to the service
    new_admin = await StudentAuthService.register_student(data.dict(), session)
    return new_admin

@router.post("/login")
async def login_student(data: StudentLogin, session: AsyncSession = Depends(get_db)):
    admin = await StudentAuthService.authenticate_student(data.dict(), session)
    return admin

@router.post("/validate_email")
async def login_student(data: StudentLogin, session: AsyncSession = Depends(get_db)):
    await StudentAuthService.validate_email(data.dict(), session)

@router.put("/update/{student_id}", response_model=dict)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update student information."""
    result = await StudentAuthService.update_student(data.dict(), session, student_id)
    return result

@router.post("/reset_password")
async def reset_password(data:StudentResetPassword, session: AsyncSession = Depends(get_db)):
    admin = await StudentAuthService.reset_password(data.dict(), session)
    return admin

@router.post('/delete')
async def delete_student(data: dict, session: AsyncSession = Depends(get_db)):
    student = await StudentAuthService.delete(data, session)
    return student