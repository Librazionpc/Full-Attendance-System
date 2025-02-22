from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.course import Course
from app.api.v1.services.auth_services.dept_services import DepartmentAuthServices as Department

class CourseAuthServices:

    @staticmethod
    async def register_course(data: dict, session: AsyncSession):
        """
        Register a new course with the course name and faculty admin ID.
        It ensures that the course does not already exist.
        """
        try:
            coursename = data.get("coursename")
            coursecode = data.get("coursecode")
            departmentname = data.get("departmentname")

            if not coursename or not coursecode or not departmentname:
                raise HTTPException(status_code=400, detail="All fields (coursename, coursecode, departmentname) are required")

            # Fetch department details
            department = await Department.get_department_details({"departmentname": departmentname}, session)
            if "Error" in department:
                raise HTTPException(status_code=404, detail="Department not found")

            existing_course = await Course.filter_by(session, coursecode=coursecode)
            if existing_course:
                raise HTTPException(status_code=409, detail="Course already exists")

            # Create a new course entry
            new_course = Course(
                coursename=coursename,
                coursecode=coursecode,
                department_id=department["department_id"]
            )

            # Save the course to the database
            await new_course.new(session, new_course)

            return {"message": "Course registered successfully", "course_id": new_course.id}

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    
    @staticmethod
    async def update_course(data: dict, session: AsyncSession):
        """
        Update the course details by course code.
        """
        try:
            coursecode = data.get("coursecode")
            facultyadmin_id = data.get("facultyadmin_id")
            new_course_code = data.get("new_course_code")
            new_course_name = data.get("new_name")

            if not coursecode or not facultyadmin_id:
                raise HTTPException(status_code=400, detail="coursecode and facultyadmin_id are required")

            # Find the course by course code
            course = await Course.filter_by(session, coursecode=coursecode)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Update fields if provided
            if new_course_name:
                course.coursename = new_course_name
            if new_course_code:
                course.coursecode = new_course_code

            # Save the updated course to the database
            await course.update(session, course)
            return {"message": "Course updated successfully"}

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

        
    @staticmethod
    async def delete(data: dict, session: AsyncSession):
        """
        Delete a course by course code.
        """
        try:
            coursecode = data.get("coursecode")
            if not coursecode:
                raise HTTPException(status_code=400, detail="coursecode is required")

            course = await Course.filter_by(session=session, coursecode=coursecode)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            await Course.delete(session, course)
            return {"message": "Course deleted successfully"}

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    @staticmethod
    async def get_course_details(data: dict, session: AsyncSession):
        """
        Get course details by course code.
        """
        try:
            coursecode = data.get("coursecode")
            if not coursecode:
                raise HTTPException(status_code=400, detail="coursecode is required")

            # Fetch course with relationships
            course = await Course.filter_by(session, coursecode=coursecode)

            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            course = course[0] if isinstance(course, list) else course

            # Extract lecturer details
            lecturers = [
                {
                    "lecturer_id": str(lecturer.id),
                    "lecturername": lecturer.lecturername,
                    "lectureremail": lecturer.lectureremail
                }
                for lecturer in course.lecturers
            ]

            # Extract student details
            students = [
                {
                    "student_id": str(student.id),
                    "studentname": student.studentname,
                    "studentemail": student.studentemail
                }
                for student in course.students
            ]

            return {
                "course_id": str(course.id),
                "coursename": course.coursename,
                "coursecode": course.coursecode,
                "department": {
                    "department_id": str(course.department.id),
                    "departmentname": course.department.departmentname
                },
                "lecturers": lecturers,
                "students": students
            }

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
