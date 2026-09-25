
# app/routers/categories.py
#
# Purpose:
#   Handles HTTP endpoints for college service categories.
#
# Endpoints:
#   GET    /categories          -> List all service categories
#   GET    /categories/{id}     -> Get one service category
#   POST   /categories          -> Create a service category
#   PUT    /categories/{id}     -> Update a service category
#   DELETE /categories/{id}     -> Delete a service category

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import get_service_categories_collection
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

router = APIRouter(
    prefix="/categories",
    tags=["Service Categories"]
)


# --------------------------------------------------
# Create a service category
# POST /categories
# --------------------------------------------------

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    payload: CategoryCreate,
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Create a new college service category."""

    # Check for duplicate category names
    if categories_collection.find_one({"name": payload.name}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A service category with this name already exists."
        )

    category_doc = {
        "id": str(uuid4()),
        "name": payload.name,
        "description": payload.description,
        "created_at": datetime.utcnow(),
    }

    categories_collection.insert_one(category_doc)

    return category_doc


# --------------------------------------------------
# List all service categories
# GET /categories
# --------------------------------------------------

@router.get(
    "",
    response_model=List[CategoryResponse]
)
def list_categories(
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Retrieve all college service categories."""

    return list(categories_collection.find({}, {"_id": 0}))


# --------------------------------------------------
# Get a service category by ID
# GET /categories/{category_id}
# --------------------------------------------------

@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: str,
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Retrieve a service category using its unique ID."""

    category_doc = categories_collection.find_one(
        {"id": category_id},
        {"_id": 0}
    )

    if not category_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found."
        )

    return category_doc


# --------------------------------------------------
# Update a service category
# PUT /categories/{category_id}
# --------------------------------------------------

@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Update an existing college service category."""

    existing = categories_collection.find_one(
        {"id": category_id}
    )

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found."
        )

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        existing.pop("_id", None)
        return existing

    # Check for duplicate names if the name is being changed
    if "name" in update_data:
        conflict = categories_collection.find_one({
            "name": update_data["name"],
            "id": {"$ne": category_id}
        })

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another service category already uses this name."
            )

    categories_collection.update_one(
        {"id": category_id},
        {"$set": update_data}
    )

    updated_doc = categories_collection.find_one(
        {"id": category_id},
        {"_id": 0}
    )

    return updated_doc


# --------------------------------------------------
# Delete a service category
# DELETE /categories/{category_id}
# --------------------------------------------------

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: str,
    categories_collection: Collection = Depends(
        get_service_categories_collection
    ),
):
    """Delete a college service category."""

    result = categories_collection.delete_one(
        {"id": category_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found."
        )

    return None