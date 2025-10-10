"""SQLAlchemy implementation for user invitations."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.invitations.models import UserInvitationModel
from app.modules.users.invitations.repository import UserInvitationRepositoryProtocol


class UserInvitationRepository(UserInvitationRepositoryProtocol):
    """Persistence logic for invitation records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_code(self, code: str) -> Optional[UserInvitationModel]:
        stmt = select(UserInvitationModel).where(UserInvitationModel.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> List[UserInvitationModel]:
        stmt = select(UserInvitationModel).where(UserInvitationModel.invited_by == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, invitation: UserInvitationModel
    ) -> UserInvitationModel:
        self.session.add(invitation)
        await self.session.flush()
        await self.session.refresh(invitation)
        return invitation

    async def save(
        self, invitation: UserInvitationModel
    ) -> UserInvitationModel:
        await self.session.flush()
        await self.session.refresh(invitation)
        return invitation


__all__ = ["UserInvitationRepository"]
