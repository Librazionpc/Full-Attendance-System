from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.attendance import Attendance
from fastapi import HTTPException, status
from ...models.course import Course
from ...models.student import Student
from ...services.auth_services.dept_services import DepartmentAuthServices as Department
from ...services.auth_services.course_services import CourseAuthServices as Course
from ...services.auth_services.lecturer_auth_services import LecturerAuthService as Lecturer
from ...hardware.fingerprint import recognize_fingerprint
from datetime import datetime
import csv
import os

class AttendanceAuthService:
    
    @staticmethod
    async def start_attendance_session(data: dict, session: AsyncSession):
        """
        Lecturer triggers this method to get the list of students and the lecturer for the course.
        This function does not take attendance or invoke fingerprint recognition.
        """
        department_name = data.get("department_name")
        lecturer_name = data.get("lecturer_name")
        course_code = data.get("course_code")
        
        lecturer = await Lecturer.get_lecturer_details(session, lecturer_name)
        department = await Department.get_department_details(session, department_name)
        course = await Course.get_course_details(session, course_code)
        
        if lecturer["department_id"] != department["id"]:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
        
        if not any(course_details["lecturer_id"] == str(lecturer["id"]) for course_details in course["lecturers"]):
            raise HTTPException(status_code=403, detail="Lecturer is not assigned to this course")

        # Return list of students and lecturer info
        student_list = [{"student_id": student["student_id"], "student_name": student["studentName"]} for student in course["students"].values()]

        return {
            "message": "Attendance session initialized",
            "lecturer": {"lecturer_id": lecturer["id"], "lecturer_name": lecturer_name},
            "students": student_list
        }

    @staticmethod
    async def take_attendance(course_id: int, student_id: int, lecturer_id: int, session: AsyncSession):
        """
        Takes attendance for a student in a course by verifying their fingerprint.
        """
        # Fetch course details
        course = await Course.get_course_details(session, course_id)
        lecturer = await Lecturer.get_lecturer_details(session, lecturer_id)

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if not lecturer:
            raise HTTPException(status_code=404, detail="Lecturer not found")

        # Ensure the lecturer is assigned to the course
        if not any(course_details["lecturer_id"] == str(lecturer["id"]) for course_details in course["lecturers"]):
            raise HTTPException(status_code=403, detail="Lecturer is not assigned to this course")

        # Check if student exists in the course
        if student_id not in course["students"]:
            raise HTTPException(status_code=404, detail="Student not found in this course")

        # Get student name for fingerprint recognition
        student_name = course["students"][student_id]["studentName"]

        # Verify fingerprint
        fingerprint_recognized = recognize_fingerprint(student_name)
        attendance_status = bool(fingerprint_recognized)

        # Record attendance if recognized
        if attendance_status:
            attendance = Attendance(
                student_id=student_id,
                course_id=course_id,
                department_id=course["department_id"],
                attendance_time=datetime.now(),
                status=True
            )
            await attendance.new(session, attendance)
            return {"message": "Attendance recorded successfully", "status": "Present"}
        else:
            return {"message": "Fingerprint verification failed", "status": "Absent"}
    
    @staticmethod
    async def get_attendance_for_course(course_id: int, session: AsyncSession):
        """Retrieve attendance records for all students in a specific course."""
        if not course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course ID is required"
            )
        
        attendances = await Attendance.filter_by(session, course_id=course_id)
        if not attendances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found for this course"
            )
        
        return attendances

    @staticmethod
    async def get_student_attendance_for_course(student_id: int, course_id: int, session: AsyncSession):
        """Retrieve attendance records for a specific student in a specific course."""
        if not student_id or not course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID and Course ID are required"
            )
        
        attendance = await Attendance.filter_by(session, student_id=student_id, course_id=course_id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found for this student in the specified course"
            )
        
        return attendance

    @staticmethod
    async def delete_attendance(attendance_id: int, session: AsyncSession):
        """Delete an attendance record."""
        attendance = await Attendance.get(session, attendance_id)

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        await Attendance.delete(session, attendance)
        await session.commit()
        return {"message": "Attendance record deleted successfully"}

    @staticmethod
    async def get_student_attendance_aggregate(student_id: int, course_id: int, session: AsyncSession):
        """
        Calculate the attendance aggregate for a student in a specific course.
        Returns the attendance percentage.
        """
        if not student_id or not course_id:
            raise HTTPException(status_code=400, detail="Student ID and Course ID are required")

        # Fetch all attendance records for the student in the course
        attendances = await Attendance.filter_by(session, student_id=student_id, course_id=course_id)

        if not attendances:
            raise HTTPException(status_code=404, detail="No attendance records found for this student in the specified course")

        # Calculate attendance percentage
        total_sessions = len(attendances)
        attended_sessions = sum(1 for record in attendances if record.status)  # Count only present records

        attendance_percentage = (attended_sessions / total_sessions) * 100

        return {
            "student_id": student_id,
            "course_id": course_id,
            "total_sessions": total_sessions,
            "attended_sessions": attended_sessions,
            "attendance_percentage": round(attendance_percentage, 2)
        }

    @staticmethod
    async def generate_attendance_report(course_id: int, lecturer_name: str, session: AsyncSession):
        """
        Generate a CSV file containing attendance aggregates for all students in a course.
        Saves the file locally.
        """
        if not course_id or not lecturer_name:
            raise HTTPException(status_code=400, detail="Course ID and Lecturer Name are required")

        # Fetch course details
        course = await Course.get_course_details(session, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        course_title = course["course_title"]
        students = course["students"]

        if not students:
            raise HTTPException(status_code=404, detail="No students enrolled in this course")

        # Prepare data for CSV
        report_data = []
        for student in students:
            student_id = student["student_id"]
            student_name = student["studentname"]

            # Fetch all attendance records for the student
            attendances = await Attendance.filter_by(session, student_id=student_id, course_id=course_id)
            total_sessions = len(attendances)
            attended_sessions = sum(1 for record in attendances if record.status)  # Count attended sessions
            attendance_percentage = (attended_sessions / total_sessions) * 100 if total_sessions > 0 else 0

            report_data.append([student_name, student_id, total_sessions, attended_sessions, round(attendance_percentage, 2)])

        # Define file path
        filename = f"attendance_report_{lecturer_name}_{course_title}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        file_path = os.path.join("reports", filename)  # Save in a "reports" folder

        # Ensure the "reports" folder exists
        os.makedirs("reports", exist_ok=True)

        # Write data to CSV file
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student Name", "Student ID", "Total Sessions", "Attended Sessions", "Attendance Percentage"])
            writer.writerows(report_data)

        print(f"Attendance report saved: {file_path}")
