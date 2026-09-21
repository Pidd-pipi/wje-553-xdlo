from fastapi import HTTPException, status
from .enums import UserRole

ROUTE_PERMISSIONS = {
    "courses:read": [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
    "courses:write": [UserRole.ADMIN, UserRole.TEACHER],
    "enrollment:write": [UserRole.STUDENT],
    "assignments:write": [UserRole.ADMIN, UserRole.TEACHER],
    "attendance:write": [UserRole.ADMIN, UserRole.TEACHER],
    "grades:write": [UserRole.ADMIN, UserRole.TEACHER],
    "audit:read": [UserRole.ADMIN],
}

def check_permission(role: UserRole | str, permission: str) -> bool:
    allowed = ROUTE_PERMISSIONS.get(permission, [])
    try:
        normalized = role if isinstance(role, UserRole) else UserRole(role)
    except ValueError:
        return False
    return normalized in allowed

def require_permission(role: UserRole | str, permission: str) -> None:
    if not check_permission(role, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
