
# app/models/request.py
#
# Purpose:
#   Defines the status lifecycle for a service request
#   in the College Service Request System.
#
# Request lifecycle:
#   NEW -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
#
# Additional transitions:
#   IN_PROGRESS -> ON_HOLD -> IN_PROGRESS


from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.models.request import RequestStatus


# Schema for creating a service request
class RequestCreate(BaseModel):
    title: str
    description: str
    category_id: str
    created_by: str


# Schema for updating a service request
class RequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None


# Schema for assigning a request to staff
class RequestAssign(BaseModel):
    assigned_to: str


# Schema for updating request status
class RequestStatusUpdate(BaseModel):
    status: RequestStatus


# Schema for returning request details
class RequestResponse(BaseModel):
    id: str
    title: str
    description: str
    category_id: str
    status: RequestStatus
    created_by: str
    assigned_to: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None