from random import randint
from datetime import datetime, timedelta

class OTP:
    """One Time Password."""

    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP."""
        return randint(100000, 999999)

    @staticmethod
    def generate_expiry_time():
        """Generate an expiry time for the OTP."""
        return datetime.now() + timedelta(minutes=5)

    @staticmethod
    def is_expired(expiry_time: datetime):
        """Check if the OTP has expired."""
        return datetime.now() > expiry_time