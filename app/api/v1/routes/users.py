"""
User API routes.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import api_logger
from app.db.database import get_db
from app.models.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all users with pagination."""
    api_logger.info("Fetching users list", extra={"skip": skip, "limit": limit})

    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)

    api_logger.info(
        "Users list fetched successfully",
        extra={"count": len(users), "skip": skip, "limit": limit},
    )
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    api_logger.info("Fetching user", extra={"user_id": user_id})

    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        api_logger.warning("User not found", extra={"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    api_logger.info(
        "User fetched successfully", extra={"user_id": user_id, "email": user.email}
    )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    api_logger.info(
        "Creating new user",
        extra={"email": user_data.email, "first_name": user_data.first_name},
    )

    user_service = UserService(db)

    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        api_logger.warning(
            "Attempt to create user with existing email",
            extra={"email": user_data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await user_service.create_user(user_data)

    api_logger.info(
        "User created successfully", extra={"user_id": user.id, "email": user.email}
    )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update user by ID."""
    api_logger.info(
        "Updating user",
        extra={
            "user_id": user_id,
            "update_fields": user_data.model_dump(exclude_unset=True),
        },
    )

    user_service = UserService(db)

    user = await user_service.get_user(user_id)
    if not user:
        api_logger.warning(
            "Attempt to update non-existent user", extra={"user_id": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated_user = await user_service.update_user(user_id, user_data)

    if updated_user:
        api_logger.info(
            "User updated successfully",
            extra={"user_id": user_id, "email": updated_user.email},
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete user by ID."""
    api_logger.info("Deleting user", extra={"user_id": user_id})

    user_service = UserService(db)

    user = await user_service.get_user(user_id)
    if not user:
        api_logger.warning(
            "Attempt to delete non-existent user", extra={"user_id": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_service.delete_user(user_id)

    api_logger.info("User deleted successfully", extra={"user_id": user_id})
