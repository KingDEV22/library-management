from app.oath import jwt_authenticate
from fastapi import Depends,HTTPException,status
class PermissionChecker:

    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles

    def __call__(self, user: any = Depends(jwt_authenticate)) -> bool:
        for role in user['role']:
            if role not in self.required_roles:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Don't have permissions to access the resources..."
                )
        return user