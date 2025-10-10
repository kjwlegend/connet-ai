"""Repository protocol for user invitations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.users.invitations.models import UserInvitationModel


class UserInvitationRepositoryProtocol(ABC):
    """Abstract operations for invitation persistence."""

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[UserInvitationModel]: ...

    @abstractmethod
    async def list_for_user(
        self, user_id: UUID
    ) -> List[UserInvitationModel]: ...

    @abstractmethod
    async def create(
        self, invitation: UserInvitationModel
    ) -> UserInvitationModel: ...

    @abstractmethod
    async def save(
        self, invitation: UserInvitationModel
    ) -> UserInvitationModel: ...


UserInvitationRepository = UserInvitationRepositoryProtocol

__all__ = [
    "UserInvitationRepositoryProtocol",
    "UserInvitationRepository",
]
