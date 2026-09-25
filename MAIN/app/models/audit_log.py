# app/models/audit_log.py
#
# Purpose:
#   Describes the shape of an audit_log document stored in MongoDB.
#   Audit logs are automatically written when a service request
#   is created, assigned, or changes status.
#
# Example document:
#   {
#       "id": "uuid4 string",
#       "request_id": "service request UUID",
#       "action": "status_changed",
#       "performed_by": "user UUID",
#       "details": "Status changed from 'new' to 'assigned'",
#       "created_at": "2026-09-22T10:00:00"
#   }

from datetime import datetime
from enum import Enum
from uuid import uuid4


class AuditAction(str, Enum):
    """Events recorded in the service request audit trail."""

    CREATED = "created"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"


def build_audit_log_doc(
    request_id: str,
    action: AuditAction,
    performed_by: str,
    details: str,
) -> dict:
    """
    Build an audit log document ready for insertion into MongoDB.
    """

    return {
        "id": str(uuid4()),
        "request_id": request_id,
        "action": action.value,
        "performed_by": performed_by,
        "details": details,
        "created_at": datetime.utcnow(),
    }