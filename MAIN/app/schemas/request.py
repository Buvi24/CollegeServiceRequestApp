from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.request import RequestStatus


class RequestCreate(BaseModel):
    """Data required to create a new service request."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Short summary of the service request"
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Full details of the service request"
    )

    category_id: str = Field(
        ...,
        description="ID of an existing service category"
    )

    created_by: str = Field(
        ...,
        description="ID of the student or faculty member raising the request"
    )

    @field_validator("title", "description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only text."""
        if not value.strip():
            raise ValueError(
                "This field cannot be blank or just whitespace."
            )
        return value.strip()


class RequestUpdate(BaseModel):
    """Edit request details, excluding status and assignment."""

    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=150
    )

    description: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=2000
    )

    category_id: Optional[str] = Field(default=None)

    @field_validator("title", "description")
    @classmethod
    def not_blank(cls, value: Optional[str]) -> Optional[str]:
        """Reject blank text when a value is provided."""
        if value is not None:
            if not value.strip():
                raise ValueError(
                    "This field cannot be blank or just whitespace."
                )
            return value.strip()
        return value


class RequestAssign(BaseModel):
    """Assign or reassign a service staff member to a request."""

    assigned_to: str = Field(
        ...,
        description="ID of the service staff member to assign"
    )

    assigned_by: str = Field(
        ...,
        description="ID of the service lead performing the assignment"
    )


class RequestStatusUpdate(BaseModel):
    """Update the lifecycle status of a service request."""

    status: RequestStatus = Field(
        ...,
        description="The new status of the service request"
    )

    changed_by: str = Field(
        ...,
        description="ID of the user performing the status change"
    )


class RequestResponse(BaseModel):
    """Response model returned for a service request."""

    id: str
    title: str
    description: str
    category_id: str
    status: RequestStatus
    created_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime