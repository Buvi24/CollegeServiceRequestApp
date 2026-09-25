# app/routers/comments.py
#
# Purpose:
#   HTTP endpoints for the Comment entity.
#   Comments are nested under a specific service request.
#
#   GET    /requests/{request_id}/comments
#   GET    /requests/{request_id}/comments/{comment_id}
#   POST   /requests/{request_id}/comments
#   PUT    /requests/{request_id}/comments/{comment_id}
#   DELETE /requests/{request_id}/comments/{comment_id}

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import (
    get_comments_collection,
    get_service_requests_collection,
    get_users_collection,
)

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)


router = APIRouter(
    prefix="/requests/{request_id}/comments",
    tags=["Comments"],
)


def _get_request_or_404(
    request_id: str,
    requests_collection: Collection,
) -> dict:
    """Check whether the service request exists."""

    request_doc = requests_collection.find_one(
        {"id": request_id}
    )

    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    return request_doc


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    request_id: str,
    payload: CommentCreate,
    comments_collection: Collection = Depends(
        get_comments_collection
    ),
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
    users_collection: Collection = Depends(
        get_users_collection
    ),
):
    """Add a comment to a service request."""

    _get_request_or_404(
        request_id,
        requests_collection,
    )

    if not users_collection.find_one(
        {"id": payload.author_id}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="author_id does not match any existing user.",
        )

    comment_doc = {
        "id": str(uuid4()),
        "request_id": request_id,
        "author_id": payload.author_id,
        "content": payload.content,
        "created_at": datetime.utcnow(),
    }

    comments_collection.insert_one(comment_doc)

    return comment_doc


@router.get(
    "",
    response_model=List[CommentResponse],
)
def list_comments(
    request_id: str,
    comments_collection: Collection = Depends(
        get_comments_collection
    ),
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """List all comments on a service request, oldest first."""

    _get_request_or_404(
        request_id,
        requests_collection,
    )

    return list(
        comments_collection.find(
            {"request_id": request_id}
        ).sort("created_at", 1)
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    request_id: str,
    comment_id: str,
    comments_collection: Collection = Depends(
        get_comments_collection
    ),
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """Get a specific comment on a service request."""

    _get_request_or_404(
        request_id,
        requests_collection,
    )

    comment_doc = comments_collection.find_one(
        {
            "id": comment_id,
            "request_id": request_id,
        }
    )

    if not comment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return comment_doc


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    request_id: str,
    comment_id: str,
    payload: CommentUpdate,
    comments_collection: Collection = Depends(
        get_comments_collection
    ),
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """Update a comment's content."""

    _get_request_or_404(
        request_id,
        requests_collection,
    )

    existing = comments_collection.find_one(
        {
            "id": comment_id,
            "request_id": request_id,
        }
    )

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if not update_data:
        return existing

    comments_collection.update_one(
        {
            "id": comment_id,
            "request_id": request_id,
        },
        {"$set": update_data},
    )

    return comments_collection.find_one(
        {
            "id": comment_id,
            "request_id": request_id,
        }
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    request_id: str,
    comment_id: str,
    comments_collection: Collection = Depends(
        get_comments_collection
    ),
    requests_collection: Collection = Depends(
        get_service_requests_collection
    ),
):
    """Delete a comment from a service request."""

    _get_request_or_404(
        request_id,
        requests_collection,
    )

    result = comments_collection.delete_one(
        {
            "id": comment_id,
            "request_id": request_id,
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return None