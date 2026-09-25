# app/schemas/comment.py
#
# Purpose:
#   Defines the Pydantic models for the Comment entity.
#   A comment belongs to exactly one service request.
#   The request_id comes from the URL path, not the request body.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Data required when adding a comment to a service request."""

    author_id: str = Field(
        ...,
        description="ID of the user writing this comment",
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The comment text",
    )


class CommentUpdate(BaseModel):
    """Data a client may send when editing a comment."""

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )


class CommentResponse(BaseModel):
    """Shape of a comment returned by the API."""

    id: str
    request_id: str
    author_id: str
    content: str
    created_at: datetime