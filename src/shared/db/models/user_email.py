"""UserEmail SQLModel."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from .base_model import BaseDBModelMixin


class UserEmail(SQLModel, BaseDBModelMixin, table=True):
    """User email addresses with primary and verification flags."""

    __tablename__ = "user_email"

    id: str = Field(primary_key=True, default=None)
    user_account_id: str = Field(foreign_key="user_account.id", index=True)
    email: str = Field(unique=True, index=True)
    is_primary: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
