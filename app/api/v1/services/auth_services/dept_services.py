from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.models.department import Department
from app.api.v1.services.auth_services.faculty_admin_auth_service import FacultyAdminAuthService as Faculty
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.utils.jwt import JWTUtils
from uuid import UUID

class DepartmentAuthServices:
    
    @staticmethod
    async def register_department(data: dict, session: AsyncSession):
        """
        Register a new department with the department name and faculty admin ID.
        Ensures that the department does not already exist.
        """
        try:
            departmentname = data.get("departmentname")
            faculty = data.get("facultyname")  # Fixed key name from "faultyname" to "facultyname"

            if not departmentname or not faculty:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")

            # Check if the department already exists
            faculty_details = await Faculty.get_admin_details({"facultyname": faculty}, session)
            existing_department = await Department.filter_by(session, departmentname=departmentname)

            if existing_department:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department already exists")

            # Create a new department entry
            password = HashUtils.hash_password(data.get("password"))

            new_dept = Department(departmentname=departmentname, 
                                  facultyadmin_id=faculty_details['id'],
                                  fingerprint=data.get("fingerprint"),
                                  department_email=data.get("department_email"),
                                  password=password)

            # Save the department to the database
            await new_dept.new(session, new_dept)

            return new_dept

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    # @staticmethod
    # async def authenticate_dept(data: dict, session: AsyncSession):
    #     """
    #     authenticate department
    #     """
    #     try:
    #         departmentname = data.get("departmentname")
    #         password = data.get("password")
    #         fingerprint = data.get("fingerprint")

    #         department = await Department.filter_by(session, departmentname=departmentname)

    #         if not department:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
            
    #         department = department[0] if isinstance(department, list) else department
    #         if department.fingerprint != fingerprint:
    #             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unkown Device")

    #         password = HashUtils.verify_password(password, department.password)
    #         if not password:
    #             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    #         faculty = await Faculty.get_admin_details({"id": (UUID(department.facultyadmin_id))}, session)
            
    #         token = JWTUtils.generate_token(str(department.id), "department", fingerprint)
    #         return {"message": "Department authenticated successfully",
    #                 "token": token,
    #                 "content": {"id": str(department.id),
    #                     "departmentname": department.departmentname,
    #                     'faculyname': faculty["facultyname"]}}

    #     except Exception as e:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    @staticmethod
    async def update_department(data: dict, session: AsyncSession):
        """
        Update the department details by department name.
        """
        try:
            departmentname = data.get("departmentname")
            facultyname = data.get("faultyname")
            department_new_name = data.get("new_name")

            if not departmentname:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department name is required")

            # Find the department by department name
            department = await Department.filter_by(session, departmentname=departmentname)

            if not department:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

            faculty = await Faculty.get_admin_details(facultyname, session)
            # Update department details
            if faculty:
                department.faultyname = faculty["facultyname"]
            if department_new_name:
                department.departmentname = department_new_name

            # Save changes to database
            await department.update(session, department)

            return {"message": "Department updated successfully", "data": department}

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod   
    async def get_department_details(data: dict, session: AsyncSession):
        """
        Retrieve department details including lecturers and students.
        """
        try:
            department_idc= data.get("department_id")
            departmentname = data.get("departmentname")

            query_params = {}
            if department_idc:
                query_params["id"] = department_idc
            if departmentname:
                query_params["departmentname"] = departmentname
            department = await Department.filter_by(session,**query_params)

            if not department:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
            department = department[0] if isinstance(department, list) else department
            return {"department_id": str(department.id),
                    "departmentname": department.departmentname,
                    "facultyadmin_id": department.facultyadmin_id}

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def delete_department(data: dict, session: AsyncSession):
        """
        Delete a department by email.
        """
        try:
            departmentname = data.get("departmentname")

            department = await Department.filter_by(session=session, departmentname=departmentname)

            if not department:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

            await Department.delete(session, department)
            
            return {"message": "Department deleted successfully"}

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
