
# app/routers/requests.py
#
# Purpose:
#   HTTP endpoints for the ServiceRequest entity.
#
# Endpoints:
#   GET    /requests                  -> List all service requests
#   GET    /requests/{id}             -> Get one service request
#   POST   /requests                  -> Create a service request
#   PUT    /requests/{id}             -> Update request details
#   PATCH  /requests/{id}/assign      -> Assign or reassign service staff
#   PATCH  /requests/{id}/status      -> Update request status
#   DELETE /requests/{id}             -> Delete a service request

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import (
    get_service_requests_collection,
    get_service_categories_collection,
    get_users_collection,
)

from app.models.request import RequestStatus, is_valid_transition

from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestAssign,
    RequestStatusUpdate,
    RequestResponse,
)


router = APIRouter(
    prefix="/requests",
    tags=["Service Requests"]
)


# --------------------------------------------------
# Create a new service request
# POST /requests
# --------------------------------------------------

@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED
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
):
    """
    Create a new college service request.

    Every new request starts with NEW status and no assigned staff.
    """

    # Check whether the service category exists
    if not categories_collection.find_one(
        {"id": payload.category_id}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing service category."
        )

    # Check whether the requesting student or faculty exists
    if not users_collection.find_one(
        {"id": payload.created_by}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_by does not match any existing user."
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

    return request_doc


# --------------------------------------------------
# List all service requests
# GET /requests
# --------------------------------------------------

@router.get(
    "",
    response_model=List[RequestResponse]
)
def list_requests(
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """
    Retrieve all service requests.
    """

    return list(
        requests_collection.find({}, {"_id": 0})
    )


# --------------------------------------------------
# Get a service request by ID
# GET /requests/{request_id}
# --------------------------------------------------

@router.get(
    "/{request_id}",
    response_model=RequestResponse
)
def get_request(
    request_id: str,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """
    Retrieve a single service request using its ID.
    """

    request_doc = requests_collection.find_one(
        {"id": request_id},
        {"_id": 0}
    )

    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found."
        )

    return request_doc


# --------------------------------------------------
# Update service request details
# PUT /requests/{request_id}
# --------------------------------------------------

@router.put(
    "/{request_id}",
    response_model=RequestResponse
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
    """
    Update request details such as title, description,
    or service category.

    Status and assignment are handled separately.
    """

    existing = requests_collection.find_one(
        {"id": request_id}
    )

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found."
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if not update_data:
        existing.pop("_id", None)
        return existing

    # Validate the category if it is being changed
    if (
        "category_id" in update_data
        and not categories_collection.find_one(
            {"id": update_data["category_id"]}
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing service category."
        )

    update_data["updated_at"] = datetime.utcnow()

    requests_collection.update_one(
        {"id": request_id},
        {"$set": update_data}
    )

    return requests_collection.find_one(
        {"id": request_id},
        {"_id": 0}
    )


# --------------------------------------------------
# Assign or reassign service staff
# PATCH /requests/{request_id}/assign
# --------------------------------------------------

@router.patch(
    "/{request_id}/assign",
    response_model=RequestResponse
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
):
    """
    Assign or reassign service staff to a service request.

    When a NEW request is assigned, its status becomes ASSIGNED.
    Reassignment does not reset the current status.
    """

    existing = requests_collection.find_one(
        {"id": request_id}
    )

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found."
        )

    # Check whether the assigned staff member exists
    staff = users_collection.find_one(
        {"id": payload.assigned_to}
    )

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_to does not match any existing user."
        )

    # Ensure only service staff can be assigned
    if staff.get("role") != "service_staff":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The assigned user must have the service_staff role."
        )

    update_data = {
        "assigned_to": payload.assigned_to,
        "updated_at": datetime.utcnow(),
    }

    # Move a NEW request to ASSIGNED
    if existing["status"] == RequestStatus.NEW.value:
        update_data["status"] = RequestStatus.ASSIGNED.value

    requests_collection.update_one(
        {"id": request_id},
        {"$set": update_data}
    )

    return requests_collection.find_one(
        {"id": request_id},
        {"_id": 0}
    )


# --------------------------------------------------
# Update service request status
# PATCH /requests/{request_id}/status
# --------------------------------------------------

@router.patch(
    "/{request_id}/status",
    response_model=RequestResponse
)
def update_request_status(
    request_id: str,
    payload: RequestStatusUpdate,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """
    Update the status of a service request.

    Valid transitions are defined in app/models/request.py.
    """

    existing = requests_collection.find_one(
        {"id": request_id}
    )

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found."
        )

    current_status = RequestStatus(
        existing["status"]
    )

    new_status = payload.status

    # Validate the requested status transition
    if not is_valid_transition(
        current_status,
        new_status
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot move request from "
                f"'{current_status.value}' to "
                f"'{new_status.value}'."
            )
        )

    requests_collection.update_one(
        {"id": request_id},
        {
            "$set": {
                "status": new_status.value,
                "updated_at": datetime.utcnow(),
            }
        }
    )

    return requests_collection.find_one(
        {"id": request_id},
        {"_id": 0}
    )


# --------------------------------------------------
# Delete a service request
# DELETE /requests/{request_id}
# --------------------------------------------------

@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_request(
    request_id: str,
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """
    Delete a service request by its ID.
    """

    result = requests_collection.delete_one(
        {"id": request_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found."
        )

    return None