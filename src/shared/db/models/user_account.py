"""UserAccount SQLModel."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from .base_model import BaseDBModelMixin


class UserAccount(SQLModel, BaseDBModelMixin, table=True):
    """User identity and authentication."""

    __tablename__ = "user_account"

    id: str = Field(primary_key=True, default=None)
    user_name: str = Field(unique=True, index=True)
    password_hash: str
    given_name: Optional[str] = Field(default=None)
    family_name: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
