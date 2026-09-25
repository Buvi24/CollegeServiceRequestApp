# app/schemas/attachment.py
#
# Purpose:
#   Defines the Pydantic models for the Attachment entity.
#   As planned, this only stores FILE METADATA (filename, a URL pointing to
#   where the file actually lives, and its size) — there is no real file
#   upload/storage engine here, to keep this project simple.
#   An attachment always belongs to exactly one ticket (ticket_id comes from
#   the URL path — see app/routers/attachments.py).
#
# Concepts demonstrated here:
#   - Field validation -> HttpUrl type check, size limits
#   - Request/Response models, Optional/default fields (same pattern as before)

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class AttachmentCreate(BaseModel):
    """Data required from the client when attaching a file to a ticket."""

    uploaded_by: str = Field(..., description="id of the User who uploaded this file")
    filename: str = Field(..., min_length=1, max_length=255, description="Original file name, e.g. 'screenshot.png'")
    url: HttpUrl = Field(..., description="Location where the actual file is stored")
    size: int = Field(..., gt=0, le=26_214_400, description="File size in bytes (max 25 MB)")


class AttachmentUpdate(BaseModel):
    """
    Data a client MAY send when correcting attachment metadata
    (e.g. fixing a typo'd filename). The file itself is never re-uploaded here.
    """

    filename: Optional[str] = Field(default=None, min_length=1, max_length=255)
    url: Optional[HttpUrl] = Field(default=None)


class AttachmentResponse(BaseModel):
    """Shape of an attachment as returned by the API."""

    id: str
    ticket_id: str
    uploaded_by: str
    filename: str
    url: HttpUrl
    size: int
    created_at: datetime