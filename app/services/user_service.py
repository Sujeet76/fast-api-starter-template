"""
User business logic and service layer.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import database_logger
from app.models.user import User, UserCreate, UserUpdate


class UserService:
    """Service class for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        database_logger.debug(
            "Fetching users from database", extra={"skip": skip, "limit": limit}
        )

        result = await self.db.execute(select(User).offset(skip).limit(limit))
        users = list(result.scalars().all())

        database_logger.debug(
            "Users fetched from database",
            extra={"count": len(users), "skip": skip, "limit": limit},
        )
        return users

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        database_logger.debug(
            "Fetching user by ID from database", extra={"user_id": user_id}
        )

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user:
            database_logger.debug(
                "User found in database",
                extra={"user_id": user_id, "email": user.email},
            )
        else:
            database_logger.debug(
                "User not found in database", extra={"user_id": user_id}
            )

        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        database_logger.debug(
            "Fetching user by email from database", extra={"email": email}
        )

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            database_logger.debug(
                "User found by email in database",
                extra={"email": email, "user_id": user.id},
            )
        else:
            database_logger.debug(
                "User not found by email in database", extra={"email": email}
            )

        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        database_logger.info(
            "Creating new user in database",
            extra={"email": user_data.email, "first_name": user_data.first_name},
        )

        try:
            # Hash the password before storing
            from app.utils.helpers import get_password_hash

            user_dict = user_data.model_dump()
            hashed_password = get_password_hash(user_dict.pop("password"))

            db_user = User(**user_dict, hashed_password=hashed_password)
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            database_logger.info(
                "User created successfully in database",
                extra={"user_id": db_user.id, "email": db_user.email},
            )

            return db_user
        except Exception as e:
            database_logger.error(
                "Failed to create user in database",
                extra={
                    "email": user_data.email,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            await self.db.rollback()
            raise

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        database_logger.info("Updating user in database", extra={"user_id": user_id})

        try:
            db_user = await self.get_user(user_id)
            if db_user:
                update_data = user_data.model_dump(exclude_unset=True)

                database_logger.debug(
                    "Applying user updates",
                    extra={
                        "user_id": user_id,
                        "update_fields": list(update_data.keys()),
                    },
                )

                for field, value in update_data.items():
                    setattr(db_user, field, value)
                await self.db.commit()
                await self.db.refresh(db_user)

                database_logger.info(
                    "User updated successfully in database",
                    extra={"user_id": user_id, "email": db_user.email},
                )
            else:
                database_logger.warning(
                    "Attempted to update non-existent user", extra={"user_id": user_id}
                )

            return db_user
        except Exception as e:
            database_logger.error(
                "Failed to update user in database",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            await self.db.rollback()
            raise

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        database_logger.info("Deleting user from database", extra={"user_id": user_id})

        try:
            db_user = await self.get_user(user_id)
            if db_user:
                await self.db.delete(db_user)
                await self.db.commit()

                database_logger.info(
                    "User deleted successfully from database",
                    extra={"user_id": user_id},
                )
                return True
            else:
                database_logger.warning(
                    "Attempted to delete non-existent user", extra={"user_id": user_id}
                )
                return False
        except Exception as e:
            database_logger.error(
                "Failed to delete user from database",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            await self.db.rollback()
            raise
