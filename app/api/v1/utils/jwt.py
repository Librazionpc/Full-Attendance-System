import jwt
import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class JWTUtils:
    @staticmethod
    def generate_token(user_id: int, role: str, fingerprint: str, expires_in: int = 86400):  
        """
        Generate JWT token with user ID, role, and fingerprint.
        """
        payload = {
            "sub": user_id,
            "role": role,  
            "fingerprint": fingerprint,  
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str):
        """
        Verify the JWT token and return user data or raise an error.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return {
                "user_id": payload.get("sub"),
                "role": payload.get("role"),
                "fingerprint": payload.get("fingerprint")
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)):
        """
        Dependency function to get the current user from the token.
        """
        return JWTUtils.verify_token(token)
