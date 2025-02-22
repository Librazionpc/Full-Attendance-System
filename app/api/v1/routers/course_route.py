from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.course_schemas import CourseCreate, CourseUpdate, CourseDelete
from app.api.v1.services.auth_services.course_services import CourseAuthServices
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.db.db_conn import get_db
from app.api.v1.utils.jwt import JWTUtils  # Import updated JWTUtils

router = APIRouter()

def admin_required(user: dict = Depends(JWTUtils.get_current_user)):
    """Ensure only admins can access"""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return user
@router.post('/create')
async def create_faculty_admin(
    data: CourseCreate,
    session: AsyncSession = Depends(get_db),
    # user: dict = Depends(admin_required)
):
    new_course = await CourseAuthServices.register_course(data.dict(), session)
    return new_course

@router.post("/update")
async def updateCourse(
    data: CourseUpdate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    course = await CourseAuthServices.update_Course(data.dict(), session)
    return course

@router.delete("/delete")
async def deleteCourse(
    data: CourseDelete, 
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    return await CourseAuthServices.delete(data.dict(), session)