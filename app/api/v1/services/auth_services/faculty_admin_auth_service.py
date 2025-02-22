from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.facultyadmin import FacultyAdmin
from app.api.v1.utils.jwt import JWTUtils
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.services.emailservices.emailservice import EmailService
from app.api.v1.utils.otp import OTP



class FacultyAdminAuthService:

    @staticmethod
    async def register_admin(data: dict, session: AsyncSession):
        """Register a new admin with hashed password."""
        try:
            email = data.get("facultyemail")
            password = data.get("password")

            if await FacultyAdmin.filter_by(facultyemail=email, session=session):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already exists")
            
            hashed_password = HashUtils.hash_password(password)
            new_admin = FacultyAdmin(
                facultyname=data.get("facultyname"),
                facultyemail=email,
                facultyphone=data.get("facultyphone"),
                facultyaddress=data.get("facultyaddress"),
                password=hashed_password,
                fingerprint=data.get("fingerprint")
            )

            await new_admin.new(session, new_admin)
            return {"content":
                {
                    "id": str(new_admin.id),
                    "facultyname": new_admin.facultyname,
                    "facultyemail": new_admin.facultyemail
                }}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def authenticate_admin(data: dict, session: AsyncSession):
        """Authenticate admin by checking email, password, and fingerprint."""
        try:
            email = data.get("facultyemail")
            password = data.get("password")
            fingerprint = data.get("fingerprint")

            admin = await FacultyAdmin.filter_by(facultyemail=email, session=session)
            
            if admin:
                admin = admin[0] if isinstance(admin, list) else admin
                password_match = HashUtils.verify_password(password, admin.password)
                if not password_match:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

                if admin.fingerprint == fingerprint:
                    token = JWTUtils.generate_token(str(admin.id), "admin", fingerprint)
                    return {
                            "message": "Login successful",
                            "token": token,
                            "user": {
                                "id": str(admin.id),
                                "facultyname": admin.facultyname,
                                "facultyemail": admin.facultyemail
                            }
                        }
                            
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty Admin not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP."""
        try:
            email = data.get("facultyemail")
            fingerprint = data.get("fingerprint")

            admin = await FacultyAdmin.filter_by(facultyemail=email, session=session)
            admin = admin[0] if isinstance(admin, list) else admin
            if admin:
                
                otp = OTP.generate_otp()
                expiry_time = OTP.generate_expiry_time()
                await FacultyAdmin.update(session, admin, otp=otp, otp_expiry=expiry_time, fingerprint=fingerprint)
                await EmailService.send_otp(email=email, otp=otp)
                return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "OTP sent successfully"})
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def validate_otp(data:dict, session: AsyncSession):
        """Validate OTP."""
        email = data.get("facultyemail")
        otp = data.get("otp")
        fingerprint = data.get("fingerprint")

        try:
            admin = await FacultyAdmin.filter_by(facultyemail=email, session=session)
            admin = admin[0] if isinstance(admin, list) else admin
            if admin:
                if admin.otp == otp:
                    if OTP.is_expired(admin.otp_expiry):
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")
                    else:
                        if admin.fingerprint != fingerprint:
                            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Verified")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset admin password after validating OTP."""
        try:
            email = data.get("facultyemail")
            otp = data.get("otp")
            newpassword = data.get("newpassword")
            fingerprint = data.get("fingerprint")


            admin = await FacultyAdmin.filter_by(session, facultyemail=email)
            if not admin:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
            
            admin = admin[0] if isinstance(admin, list) else admin
            if HashUtils.verify_password(newpassword, admin.password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from the old password")

            if admin.fingerprint != fingerprint:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")

            hashed_password = HashUtils.hash_password(newpassword)
            admin.password = hashed_password
            await FacultyAdmin.update(session, admin)

            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password reset successfully"})

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod


    async def search_admins(session: AsyncSession):
        """Search faculty admin by name."""
        try:
            faculty_list = await FacultyAdmin.get_all(session)  # Get all faculty admins

            if faculty_list is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty does not exist")
            
            # Convert each faculty object to a dictionary
            
            faculty_data = [
                {
                    "id": str(faculty.id),
                    "facultyname": faculty.facultyname,
                    "facultyemail": faculty.facultyemail
                }
                for faculty in faculty_list
            ]

            return {"message": "Faculty Admin Available", "data": faculty_data}

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    @staticmethod
    async def get_admin_details(data: dict, session: AsyncSession):
        """Get faculty admin details by ID or faculty name."""
        try:
            faculty_id = data.get("id")
            faculty_name = data.get("facultyname")

            
            query_params = {}
            if faculty_id:
                query_params["id"] = faculty_id
            if faculty_name:
                query_params["facultyname"] = faculty_name
            
            faculty = await FacultyAdmin.filter_by(session, **query_params)
            print(faculty[0])
            if not faculty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Faculty Admin not found"
                )

            faculty = faculty[0] if isinstance(faculty, list) else faculty
            return {
                "id": str(faculty.id),
                "facultyname": faculty.facultyname,
                "facultyemail": faculty.facultyemail
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

            
    async def update_admin(data: dict, session: AsyncSession):
        """Update faculty admin details."""
        try:
            faculty_id = data.get("facultyid")
            
            faculty = await FacultyAdmin.filter_by(session, id=faculty_id)
            if not faculty:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty Admin not found")
            
            faculty = faculty[0] if isinstance(faculty, list) else faculty
            faculty.facultyname = data.get("facultyname", faculty.facultyname)
            faculty.facultyemail = data.get("facultyemail", faculty.facultyemail)
            await FacultyAdmin.update(session, faculty)
            return {"message": "Faculty Admin updated successfully"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    