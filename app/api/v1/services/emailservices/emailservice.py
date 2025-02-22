import aiosmtplib
from email.message import EmailMessage

class EmailService:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "your-email@gmail.com"
    SMTP_PASSWORD = "your-email-password"

    @staticmethod
    async def send_otp(email: str, otp: str):
        """Send OTP to the given email."""
        msg = EmailMessage()
        msg["Subject"] = "Your OTP Code"
        msg["From"] = EmailService.SMTP_USERNAME
        msg["To"] = email
        msg.set_content(f"Your OTP code is: {otp}\n\nThis code expires in 5 minutes.")

        try:
            await aiosmtplib.send(
                msg,
                hostname=EmailService.SMTP_SERVER,
                port=EmailService.SMTP_PORT,
                start_tls=True,
                username=EmailService.SMTP_USERNAME,
                password=EmailService.SMTP_PASSWORD,
            )
            return {"success": True, "message": "OTP sent successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}
