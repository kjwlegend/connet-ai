"""Business logic for user invitations."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.users.invitations.models import UserInvitationModel
from app.modules.users.invitations.repository import UserInvitationRepositoryProtocol


class UserInvitationService:
    """Handles creation and lifecycle of user invitations."""

    def __init__(self, repository: UserInvitationRepositoryProtocol) -> None:
        self.repository = repository

    async def list_invitations(self, user_id: UUID) -> List[UserInvitationModel]:
        return await self.repository.list_for_user(user_id)

    async def get_invitation(self, code: str) -> Optional[UserInvitationModel]:
        return await self.repository.get_by_code(code)

    async def create_invitation(
        self,
        user_id: UUID,
        code: str,
        max_uses: int = 1,
        expires_at: datetime | None = None,
    ) -> UserInvitationModel:
        existing = await self.repository.get_by_code(code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invitation code already exists",
            )
        invitation = UserInvitationModel(
            invited_by=user_id,
            code=code,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        return await self.repository.create(invitation)

    async def deactivate_invitation(self, code: str) -> None:
        invitation = await self.repository.get_by_code(code)
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        invitation.is_active = False
        invitation.updated_at = datetime.utcnow()
        await self.repository.save(invitation)


__all__ = ["UserInvitationService"]
