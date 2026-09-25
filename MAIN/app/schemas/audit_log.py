# app/schemas/audit_log.py
#
# Purpose:
#   Defines the Pydantic response model for the AuditLog entity.
#   Audit logs are automatically written by the server and
#   are only readable through the API.

from datetime import datetime

from pydantic import BaseModel

from app.models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    """Shape of an audit log entry returned by the API."""

    id: str
    request_id: str
    action: AuditAction
    performed_by: str
    details: str
    created_at: datetime