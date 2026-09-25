from datetime import datetime

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """
    Data required when creating a new user.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user"
    )

    email: EmailStr = Field(
        ...,
        description="Unique email address used as login identifier"
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User password"
    )

    role: UserRole = Field(
        default=UserRole.STUDENT,
        description="Role: student, faculty, service_staff, department_lead, admin"
    )


class UserUpdate(BaseModel):
    """
    Optional fields for updating an existing user.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        default=None,
        min_length=8
    )

    role: Optional[UserRole] = None


class UserResponse(BaseModel):
    """
    User data returned by the API.
    Password is excluded for security.
    """

    id: str
    name: str
    email: EmailStr
    role: UserRole