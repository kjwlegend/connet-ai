"""
User Prompt Library Database Model

This module defines the SQLModel for user's custom prompt library.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text


class UserPromptLibraryModel(SQLModel, table=True):
    """User's custom prompt library database model."""
    
    __tablename__ = "user_prompt_library"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique prompt identifier"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID"
    )
    
    # Prompt information
    title: str = Field(
        max_length=200,
        description="Prompt title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Prompt description"
    )
    prompt_text: str = Field(
        sa_column=Column(Text),
        description="The actual prompt text"
    )
    
    # Organization
    category: str = Field(
        default="general",
        max_length=50,
        index=True,
        description="Prompt category: general, coding, writing, analysis, creative"
    )
    tags: List[str] = Field(
        default=[],
        description="Tags for organization and search"
    )
    
    # Usage information
    use_count: int = Field(
        default=0,
        description="Number of times this prompt was used"
    )
    last_used_at: Optional[datetime] = Field(
        default=None,
        description="Last usage timestamp"
    )
    
    # Sharing and visibility
    is_public: bool = Field(
        default=False,
        description="Whether prompt is shared publicly"
    )
    is_favorite: bool = Field(
        default=False,
        description="Whether prompt is marked as favorite"
    )
    
    # Template variables
    variables: List[dict] = Field(
        default=[],
        description="Template variables and their descriptions"
    )
    
    # AI model preferences
    preferred_models: List[str] = Field(
        default=[],
        description="Preferred AI models for this prompt"
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Preferred temperature setting"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Preferred max tokens setting"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "title": "Code Review Assistant",
                "description": "Helps review code for bugs, performance, and best practices",
                "prompt_text": "Please review the following code for:\n1. Potential bugs\n2. Performance issues\n3. Best practices\n4. Security concerns\n\nCode:\n{code}\n\nLanguage: {language}",
                "category": "coding",
                "tags": ["code-review", "debugging", "best-practices"],
                "use_count": 15,
                "is_favorite": True,
                "variables": [
                    {
                        "name": "code",
                        "description": "The code to review",
                        "required": True
                    },
                    {
                        "name": "language",
                        "description": "Programming language",
                        "required": True
                    }
                ],
                "preferred_models": ["gpt-4", "claude-3-opus"],
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }