# app/models/ticket.py
#
# Purpose:
#   Describes the shape of a "ticket" document as stored in MongoDB, and
#   defines the ticket lifecycle rules (which status can move to which).
#
# Lifecycle (from the requirements):
#   NEW -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
#   Plus the branch:
#   IN_PROGRESS -> ON_HOLD -> IN_PROGRESS
#
# A ticket document in MongoDB looks like this:
#   {
#       "id": "「uuid4 string」",
#       "title": "Laptop won't turn on",
#       "description": "...",
#       "category_id": "「category's uuid4 string」",
#       "status": "new",
#       "created_by": "「employee user's uuid4 string」",
#       "assigned_to": None,                # set once a Team Lead assigns a technician
#       "created_at": "2026-09-22T10:00:00",
#       "updated_at": "2026-09-22T10:00:00"
#   }

from enum import Enum


class RequestStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


# Define allowed status transitions
ALLOWED_TRANSITIONS = {
    RequestStatus.NEW: [RequestStatus.ASSIGNED],
    RequestStatus.ASSIGNED: [
        RequestStatus.IN_PROGRESS,
        RequestStatus.ON_HOLD,
    ],
    RequestStatus.IN_PROGRESS: [
        RequestStatus.ON_HOLD,
        RequestStatus.RESOLVED,
    ],
    RequestStatus.ON_HOLD: [
        RequestStatus.IN_PROGRESS,
    ],
    RequestStatus.RESOLVED: [
        RequestStatus.CLOSED,
    ],
    RequestStatus.CLOSED: [],
}


def is_valid_transition(current_status, new_status):
    """
    Check whether a service request can move
    from its current status to the new status.
    """
    try:
        current_status = RequestStatus(current_status)
        new_status = RequestStatus(new_status)
    except ValueError:
        return False

    return new_status in ALLOWED_TRANSITIONS.get(
        current_status, []
    )