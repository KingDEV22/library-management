from fastapi import Depends,HTTPException,status
import logging

from app.oath import jwt_authenticate

# Set up a logger with basic configuration
logging.basicConfig(level=logging.INFO)
class PermissionChecker:

    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles

    def __call__(self, user: any = Depends(jwt_authenticate)) -> bool:
        for role in self.required_roles:
            if role not in user['role']:
                logging.error("User don't have specific role: ", role, "!!!!!!")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Don't have permissions to access the resources..."
                )
        logging.info("User verfied. Has the specific role")
        return user