from fastapi import Depends, HTTPException, status
from typing import List

# Phase 10 RBAC Middleware

class RoleChecker:
    """
    Dependency injector enforcing Role-Based Access Control limits on PCCOE APIs.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict):
        # We assume the user dictionary is injected by FastAPI auth logic (Phase 9)
        # e.g., current_user = {"prn": "123", "roles": ["student"]}
        
        user_roles = current_user.get("roles", [])
        
        # Check intersection
        has_permission = any(role in self.allowed_roles for role in user_roles)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary EOC or Administrative permissions."
            )
        
        return current_user

# Pre-defined RBAC instances for immediate Dependency usage on routers
RequireEOCAdmin = RoleChecker(["eoc_admin", "super_admin"])
RequireFaculty = RoleChecker(["faculty", "eoc_admin", "super_admin"])
RequireStudent = RoleChecker(["student", "student_rep"])
