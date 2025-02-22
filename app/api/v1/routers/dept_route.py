from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.department_schemas import DepartmentCreate, DepartmentUpdate, DepartmentDetails, DepartmentLogin
from app.api.v1.services.auth_services.dept_services import DepartmentAuthServices
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
    data: DepartmentCreate,
    session: AsyncSession = Depends(get_db),
    # user: dict = Depends(admin_required)
):
    new_dept = await DepartmentAuthServices.register_department(data.dict(), session)
    return {"message": "Server Returns",
            "data" : {"departmentname": new_dept.departmentname, "facultyadmin_id": new_dept.facultyadmin_id}}
    
@router.post("/login")
async def loginDepartment(
    data: DepartmentLogin,
    session: AsyncSession = Depends(get_db)
):
    return await DepartmentAuthServices.authenticate_dept(data.dict(), session)

@router.post("/update")
async def updateDepartment(
    data: DepartmentUpdate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    dept = await DepartmentAuthServices.update_department(data.dict(), session)
    return dept

@router.post("/details")
async def getDepartmentDetails(
    data: DepartmentDetails,
    session: AsyncSession = Depends(get_db)
):
    return await DepartmentAuthServices.get_department_details(data.dict(), session)