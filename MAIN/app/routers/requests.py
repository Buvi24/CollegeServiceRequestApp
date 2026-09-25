# app/routers/requests.py
#
# Purpose:
#   HTTP endpoints for the Service Request entity.
#
#   GET    /requests                  -> List requests with filters
#   GET    /requests/{request_id}     -> Get one request
#   POST   /requests                  -> Create a service request
#   PUT    /requests/{request_id}     -> Update request details
#   PUT    /requests/{request_id}/assign -> Assign request to staff
#   PATCH  /requests/{request_id}/status -> Update request status
#   DELETE /requests/{request_id}     -> Delete a request
#
#   Audit logs are automatically created for request creation,
#   assignment, and status changes.

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pymongo.collection import Collection

from app.dependencies import (
    get_service_requests_collection,
    get_service_categories_collection,
    get_users_collection,
    get_audit_logs_collection,
)

from app.models.request import (
    RequestStatus,
    is_valid_transition,
)

from app.models.audit_log import (
    AuditAction,
    build_audit_log_doc,
)

from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestAssign,
    RequestStatusUpdate,
    RequestResponse,
)


router = APIRouter(
    prefix="/requests",
    tags=["Service Requests"],
)


# ---------------------------------------------------------
# Helper function: Check if service request exists
# ---------------------------------------------------------

def _get_request_or_404(
    request_id: str,
    requests_collection: Collection,
) -> dict:
    """Find a service request or return HTTP 404."""

    request_doc = requests_collection.find_one(
        {"id": request_id}
    )

    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    return request_doc


# ---------------------------------------------------------
# POST /requests
# Create a new service request
# ---------------------------------------------------------

@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    payload: RequestCreate,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
    users_collection: Collection = Depends(
        get_users_collection
    ),
    audit_logs_collection: Collection = Depends(
        get_audit_logs_collection
    ),
):
    """Create a new service request."""

    # Check whether the category exists
    if not categories_collection.find_one(
        {"id": payload.category_id}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing service category.",
        )

    # Check whether the creator exists
    if not users_collection.find_one(
        {"id": payload.created_by}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_by does not match any existing user.",
        )

    now = datetime.utcnow()

    request_doc = {
        "id": str(uuid4()),
        "title": payload.title,
        "description": payload.description,
        "category_id": payload.category_id,
        "status": RequestStatus.NEW.value,
        "created_by": payload.created_by,
        "assigned_to": None,
        "created_at": now,
        "updated_at": now,
    }

    requests_collection.insert_one(request_doc)

    # Record creation in the audit trail
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_doc["id"],
            action=AuditAction.CREATED,
            performed_by=payload.created_by,
            details=(
                f"Service request created with status "
                f"'{RequestStatus.NEW.value}'."
            ),
        )
    )

    return request_doc


# ---------------------------------------------------------
# GET /requests
# List requests with filtering and pagination
# ---------------------------------------------------------

@router.get(
    "",
    response_model=List[RequestResponse],
)
def list_requests(
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    status_filter: Optional[RequestStatus] = Query(
        default=None,
        alias="status",
        description="Filter by request status",
    ),
    category_id: Optional[str] = Query(
        default=None,
        description="Filter by service category ID",
    ),
    assigned_to: Optional[str] = Query(
        default=None,
        description="Filter by assigned staff user ID",
    ),
    created_by: Optional[str] = Query(
        default=None,
        description="Filter by the user who created the request",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of requests to skip",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of requests to return",
    ),
):
    """List service requests with optional filters and pagination."""

    mongo_filter = {}

    if status_filter is not None:
        mongo_filter["status"] = status_filter.value

    if category_id is not None:
        mongo_filter["category_id"] = category_id

    if assigned_to is not None:
        mongo_filter["assigned_to"] = assigned_to

    if created_by is not None:
        mongo_filter["created_by"] = created_by

    cursor = (
        requests_collection.find(mongo_filter)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return list(cursor)


# ---------------------------------------------------------
# GET /requests/{request_id}
# Get one service request
# ---------------------------------------------------------

@router.get(
    "/{request_id}",
    response_model=RequestResponse,
)
def get_request(
    request_id: str,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """Retrieve a service request by its ID."""

    return _get_request_or_404(
        request_id,
        requests_collection,
    )


# ---------------------------------------------------------
# PUT /requests/{request_id}
# Update request details
# ---------------------------------------------------------

@router.put(
    "/{request_id}",
    response_model=RequestResponse,
)
def update_request(
    request_id: str,
    payload: RequestUpdate,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Update service request details."""

    existing = _get_request_or_404(
        request_id,
        requests_collection,
    )

    update_data = payload.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if not update_data:
        return existing

    # Verify the new category if one is provided
    if "category_id" in update_data:
        if not categories_collection.find_one(
            {"id": update_data["category_id"]}
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="category_id does not match any existing service category.",
            )

    update_data["updated_at"] = datetime.utcnow()

    requests_collection.update_one(
        {"id": request_id},
        {"$set": update_data},
    )

    return requests_collection.find_one(
        {"id": request_id}
    )


# ---------------------------------------------------------
# PUT /requests/{request_id}/assign
# Assign or reassign request to staff
# ---------------------------------------------------------

@router.put(
    "/{request_id}/assign",
    response_model=RequestResponse,
)
def assign_request(
    request_id: str,
    payload: RequestAssign,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    users_collection: Collection = Depends(
        get_users_collection
    ),
    audit_logs_collection: Collection = Depends(
        get_audit_logs_collection
    ),
):
    """Assign or reassign a service request to staff."""

    existing = _get_request_or_404(
        request_id,
        requests_collection,
    )

    # Check that the assigned user exists
    assigned_user = users_collection.find_one(
        {"id": payload.assigned_to}
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_to does not match any existing user.",
        )

    # Check that the assigned user is service staff
    if assigned_user.get("role") != "service_staff":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The assigned user must have the service_staff role.",
        )

    # Check that the person performing the assignment exists
    if not users_collection.find_one(
        {"id": payload.assigned_by}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_by does not match any existing user.",
        )

    now = datetime.utcnow()

    update_data = {
        "assigned_to": payload.assigned_to,
        "updated_at": now,
    }

    status_also_changed = (
        existing["status"] == RequestStatus.NEW.value
    )

    if status_also_changed:
        update_data["status"] = RequestStatus.ASSIGNED.value

    requests_collection.update_one(
        {"id": request_id},
        {"$set": update_data},
    )

    # Record assignment in the audit trail
    details = (
        f"Assigned to user '{payload.assigned_to}'."
    )

    if status_also_changed:
        details += (
            f" Status moved from "
            f"'{RequestStatus.NEW.value}' to "
            f"'{RequestStatus.ASSIGNED.value}'."
        )

    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_id,
            action=AuditAction.ASSIGNED,
            performed_by=payload.assigned_by,
            details=details,
        )
    )

    return requests_collection.find_one(
        {"id": request_id}
    )


# ---------------------------------------------------------
# PATCH /requests/{request_id}/status
# Update service request status
# ---------------------------------------------------------

@router.patch(
    "/{request_id}/status",
    response_model=RequestResponse,
)
def update_request_status(
    request_id: str,
    payload: RequestStatusUpdate,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    users_collection: Collection = Depends(
        get_users_collection
    ),
    audit_logs_collection: Collection = Depends(
        get_audit_logs_collection
    ),
):
    """Change the status of a service request."""

    existing = _get_request_or_404(
        request_id,
        requests_collection,
    )

    # Check whether the user performing the change exists
    if not users_collection.find_one(
        {"id": payload.changed_by}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="changed_by does not match any existing user.",
        )

    current_status = RequestStatus(
        existing["status"]
    )

    new_status = payload.status

    # Validate the status transition
    if not is_valid_transition(
        current_status,
        new_status,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition from "
                f"'{current_status.value}' to "
                f"'{new_status.value}'."
            ),
        )

    requests_collection.update_one(
        {"id": request_id},
        {
            "$set": {
                "status": new_status.value,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    # Record the status change in the audit trail
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_id,
            action=AuditAction.STATUS_CHANGED,
            performed_by=payload.changed_by,
            details=(
                f"Status changed from "
                f"'{current_status.value}' to "
                f"'{new_status.value}'."
            ),
        )
    )

    return requests_collection.find_one(
        {"id": request_id}
    )


# ---------------------------------------------------------
# DELETE /requests/{request_id}
# Delete a service request
# ---------------------------------------------------------

@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_request(
    request_id: str,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """Delete a service request."""

    result = requests_collection.delete_one(
        {"id": request_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    return None