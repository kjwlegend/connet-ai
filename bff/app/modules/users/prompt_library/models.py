"""SQLModel definitions for user prompt library entries."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Column as SQLColumn, Field, SQLModel, Text


class UserPromptLibraryModel(SQLModel, table=True):
    """Custom prompts saved by users."""

    __tablename__ = "user_prompt_library"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    prompt_text: str = Field(sa_column=SQLColumn(Text))

    category: str = Field(default="general", max_length=50, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    use_count: int = Field(default=0)
    last_used_at: Optional[datetime] = Field(default=None)

    is_public: bool = Field(default=False)
    is_favorite: bool = Field(default=False)

    variables: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_models: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    temperature: Optional[float] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["UserPromptLibraryModel"]
