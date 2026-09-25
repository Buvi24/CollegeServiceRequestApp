
# This file handles user-related API operations
# for the College Service Request System.

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import get_users_collection
from app.schemas.user import UserCreate, UserUpdate, UserResponse


# Create the users router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# --------------------------------------------------
# Create a new user
# POST /users
# --------------------------------------------------

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    payload: UserCreate,
    users_collection: Collection = Depends(get_users_collection),
):
    """
    Create a new user (Student, Faculty, Service Staff,
    Department Lead, or Admin).
    """

    # Check whether the email already exists
    if users_collection.find_one({"email": payload.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Create the user document
    user_doc = {
        "id": str(uuid4()),
        "name": payload.name,
        "email": str(payload.email),
        "password": payload.password,
        "role": payload.role.value,
        "created_at": datetime.utcnow(),
    }

    # Save the user in MongoDB
    users_collection.insert_one(user_doc)

    # Return user data without the password
    return user_doc


# --------------------------------------------------
# Get all users
# GET /users
# --------------------------------------------------

@router.get(
    "",
    response_model=List[UserResponse]
)
def list_users(
    users_collection: Collection = Depends(get_users_collection),
):
    """
    Retrieve all users in the system.
    """

    return list(users_collection.find({}, {"_id": 0}))


# --------------------------------------------------
# Get a single user
# GET /users/{user_id}
# --------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: str,
    users_collection: Collection = Depends(get_users_collection),
):
    """
    Retrieve a user using their unique ID.
    """

    user_doc = users_collection.find_one(
        {"id": user_id},
        {"_id": 0}
    )

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user_doc


# --------------------------------------------------
# Update an existing user
# PUT /users/{user_id}
# --------------------------------------------------

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: str,
    payload: UserUpdate,
    users_collection: Collection = Depends(get_users_collection),
):
    """
    Update an existing user's details.
    Only the fields provided by the client are updated.
    """

    # Check whether the user exists
    existing = users_collection.find_one({"id": user_id})

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Extract only the fields sent by the client
    update_data = payload.model_dump(exclude_unset=True)

    # Convert EmailStr and Enum values into standard strings
    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"])

    if "role" in update_data and update_data["role"] is not None:
        update_data["role"] = update_data["role"].value

    # If no fields were provided, return the existing user
    if not update_data:
        existing.pop("_id", None)
        return existing

    # Check for duplicate email if the email is being changed
    if "email" in update_data:
        conflict = users_collection.find_one({
            "email": update_data["email"],
            "id": {"$ne": user_id}
        })

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another user already uses this email."
            )

    # Update the user document
    users_collection.update_one(
        {"id": user_id},
        {"$set": update_data}
    )

    # Retrieve the updated user
    updated_doc = users_collection.find_one(
        {"id": user_id},
        {"_id": 0}
    )

    return updated_doc


# --------------------------------------------------
# Delete a user
# DELETE /users/{user_id}
# --------------------------------------------------

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: str,
    users_collection: Collection = Depends(get_users_collection),
):
    """
    Delete a user from the system.
    """

    result = users_collection.delete_one({"id": user_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return None