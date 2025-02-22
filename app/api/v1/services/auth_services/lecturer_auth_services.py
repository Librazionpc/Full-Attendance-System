from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.models.lecturer import Lecturer
from app.api.v1.utils.jwt import JWTUtils
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.utils.otp import OTP
from app.api.v1.services.emailservices.emailservice import EmailService
from app.api.v1.services.auth_services.dept_services import DepartmentAuthServices as Department

class LecturerAuthService:

    @staticmethod
    async def register_lecturer(data: dict, session: AsyncSession):
        """Register a new lecturer with hashed password."""
        try:
            email = data.get("lectureremail")
            password = data.get("password")
            departmentname = data.get("departmentname")

            if await Lecturer.filter_by(session, lectureremail=email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

            hashed_password = HashUtils.hash_password(password)
            department = await Department.get_department_details({"departmentname": departmentname}, session)

            new_lecturer = Lecturer(
                lecturername=data.get("lecturername"),
                lectureremail=email,
                department_id=department["department_id"],
                password=hashed_password,
                fingerprint=data.get('fingerprint')
            )

            await new_lecturer.new(session, new_lecturer)
            return {"message": "Lecturer registered successfully", "data": new_lecturer}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def authenticate_lecturer(data: dict, session: AsyncSession):
        """Authenticate lecturer by checking email, password, and fingerprint."""
        try:
            email = data.get("lectureremail")
            password = data.get("password")
            fingerprint = data.get('fingerprint')

            lecturer = await Lecturer.filter_by(session, lectureremail=email)
            if not lecturer or not HashUtils.verify_password(password, lecturer.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

            if lecturer.fingerprint != fingerprint:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown device")

            token = JWTUtils.generate_token(lecturer.id, "lecturer", fingerprint)
            return {"message": "Authentication successful", "token": token}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP."""
        try:
            email = data.get("lectureremail")
            fingerprint = data.get("fingerprint")
            if not email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")

            user = await Lecturer.filter_by(session, lectureremail=email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
            
            user = user[0] if user else None
            otp =  OTP.generate_otp(data, session, email)
            expiry = OTP.generate_expiry_time()
            
            await Lecturer.update(session, user, {"otp": otp, "expiry": expiry, "fingerprint": fingerprint})
            await EmailService.send_otp(email=email, otp=user.otp)
            return {"message": "OTP sent successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def update_lecturer(data: dict, session: AsyncSession, lecturer_id: int):
        """Update lecturer information."""
        try:
            lecturer = await Lecturer.filter_by(session, id=lecturer_id)
            if not lecturer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")

            department = Department.get_department_id(data.get("departmentname"), session)
            lecturername = data.get("lecturername", lecturer.lecturername)
            lecturerphone = data.get("lecturerphone", lecturer.lecturerphone)
            department_id = department["department_id"] if department is {} else lecturer.department_id

            await lecturer.update(session, lecturer, {"lecturername": lecturername, "lecturerphone": lecturerphone, "department_id": department_id})
            return {"message": "Lecturer updated successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset lecturer password after validating OTP."""
        try:
            email = data.get("lectureremail")
            password = data.get("password")
            newpassword = data.get("newPassword")
            fingerprint = data.get('fingerprint')

            lecturer = await Lecturer.filter_by(session, email=email)
            if not lecturer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
            if HashUtils.verify_password(newpassword, lecturer.password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from the old password")

        
            if lecturer.fingerprint != fingerprint:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown device")

            lecturer.password = HashUtils.hash_password(newpassword)
            await lecturer.update(session, lecturer)
            return {"message": "Password reset successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    @staticmethod
    async def delete(data: dict, session: AsyncSession):
        """Delete a lecturer by email."""
        try:
            lectureremail = data.get("lectureremail")
            if not lectureremail:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided")

            lecturer = await Lecturer.filter_by(session=session, email=lectureremail)
            if not lecturer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
            
            await Lecturer.delete(session, lecturer)
            return {"message": "Lecturer deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



    async def list_lecturers(data: dict, session: AsyncSession):
        """Search lecturers by department, faculty, or course."""
        try:
            # Get all lecturers initially
            lecturers = await Lecturer.get_all(session)
            
            if not lecturers:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lecturers found")

            # Apply filters if provided
            if data.departmentname:
                lecturers = [lect for lect in lecturers if lect.departmentname == data.departmentname]
            if data.facultyname:
                lecturers = [lect for lect in lecturers if lect.facultyname == data.facultyname]
            if data.coursename:
                lecturers = [lect for lect in lecturers if lect.coursename == data.coursename]

            # Convert to dictionary format
            lecturer_data = [
                {
                    "id": str(lecturer.id),
                    "lecturername": lecturer.lecturername,
                    "lectureremail": lecturer.lectureremail
                }
                for lecturer in lecturers
            ]

            return {"message": "Lecturers found", "data": lecturer_data}
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def validate_otp(data:dict, session: AsyncSession):
            """Validate OTP."""
            email = data.get("lectureremail")
            otp = data.get("otp")
            fingerprint = data.get("fingerprint")

            try:
                lecturer = await Lecturer.filter_by(lectureremail=email, session=session)
                lecturer = lecturer[0] if isinstance(lecturer, list) else lecturer
                if lecturer:
                    if lecturer.otp == otp:
                        if OTP.is_expired(lecturer.otp_expiry):
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")
                        else:
                            if lecturer.fingerprint != fingerprint:
                                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Verified")
                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            

    async def get_lecturer_details(data: dict, session: AsyncSession):
        """Get lecturer details."""
        try:
            name = data.get("lecturername")
            lecturer = await Lecturer.filter_by(session, lecturername=name)

            if not lecturer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")

            lecturer = lecturer[0] if isinstance(lecturer, list) else lecturer

            # Extract all courses assigned to the lecturer
            course_list = [{"course_id": str(course.id), "course_name": course.name} for course in lecturer.courses]

            return {
                "lecturer_id": str(lecturer.id),
                "lecturername": lecturer.lecturername,
                "lectureremail": lecturer.lectureremail,
                "department_id": lecturer.department_id,
                "courses": course_list
            }
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
