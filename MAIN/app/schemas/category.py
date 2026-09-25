
# app/schemas/category.py
#
# Purpose:
# Defines Pydantic models for college service categories.
#
# Categories include:
# Bonafide Certificate, ID Card, Hostel, Transport, Library, IT Support.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """
    Data required when creating a new service category.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Service category name, e.g. Bonafide Certificate, ID Card"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Short explanation of the college service"
    )


class CategoryUpdate(BaseModel):
    """
    Optional fields for updating an existing service category.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    description: Optional[str] = Field(
        default=None,
        max_length=300
    )


class CategoryResponse(BaseModel):
    """
    Shape of a service category returned by the API.
    """

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime