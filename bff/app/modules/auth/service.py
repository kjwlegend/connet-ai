"""Supabase authentication service implementation."""

import json
import secrets
import string
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple

from supabase import Client
from supabase_auth.errors import AuthApiError, AuthError

from app.infrastructure.external.supabase.client import get_supabase_client
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import User, UserCreate
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SupabaseAuthService:
    """Integrates Supabase Auth with local persistence."""

    def __init__(
        self,
        user_repository: UserRepository,
        supabase_client: Optional[Client] = None,
    ) -> None:
        self.user_repository = user_repository
        self.supabase = supabase_client or get_supabase_client()

    def _generate_invitation_code(self) -> str:
        letters = "".join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        numbers = "".join(secrets.choice(string.digits) for _ in range(3))
        return letters + numbers

    async def _ensure_unique_invitation_code(self) -> str:
        import time

        for _ in range(10):
            code = self._generate_invitation_code()
            if not await self.user_repository.get_by_invitation_code(code):
                return code

        timestamp = str(int(time.time()))[-6:]
        return f"USR{timestamp}"

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        username: Optional[str] = None,
        invited_by_code: Optional[str] = None,
        registration_source: Optional[str] = None,
        registration_channel: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        user_metadata: Optional[Dict] = None,
    ) -> Tuple[User, Dict]:
        try:
            if await self.user_repository.get_by_email(email):
                raise ValueError("User with this email already exists")

            if username and await self.user_repository.get_by_username(username):
                raise ValueError("Username already taken")

            invited_by_user_id = None
            if invited_by_code:
                inviter = await self.user_repository.get_by_invitation_code(invited_by_code)
                if not inviter:
                    raise ValueError("Invalid invitation code")
                invited_by_user_id = inviter.id

            invitation_code = await self._ensure_unique_invitation_code()

            metadata = {
                "full_name": full_name,
                "username": username,
                "invitation_code": invitation_code,
                "invited_by_code": invited_by_code,
                "registration_source": registration_source,
                "registration_channel": registration_channel,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                **(user_metadata or {}),
            }

            auth_response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": metadata},
                }
            )

            if auth_response.user is None:
                raise ValueError("Failed to create user in Supabase Auth")

            supabase_user = auth_response.user

            user_data = UserCreate(
                id=supabase_user.id,
                email=email,
                full_name=full_name,
                username=username,
                is_active=supabase_user.email_confirmed_at is not None,
                auth_provider="supabase",
                external_id=supabase_user.id,
                invitation_code=invitation_code,
                invited_by_code=invited_by_code,
                invited_by_user_id=invited_by_user_id,
                registration_source=registration_source or "web",
                registration_channel=
                    registration_channel or ("invite" if invited_by_code else "organic"),
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
                user_metadata=metadata,
            )

            local_user = await self.user_repository.create(user_data)

            logger.info("User registered successfully: %s (ID: %s)", email, supabase_user.id)

            return local_user, {"user": supabase_user, "session": auth_response.session}

        except AuthError as exc:
            logger.error("Supabase auth error during registration: %s", exc)
            raise ValueError(f"Registration failed: {exc.message}") from exc
        except ValueError:
            raise
        except Exception as exc:
            logger.error("Failed to register user %s: %s", email, exc)
            raise

    async def login_user(self, email: str, password: str) -> Tuple[User, Dict]:
        try:
            auth_response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if auth_response.user is None:
                raise ValueError("Authentication failed")

            supabase_user = auth_response.user

            local_user = await self._sync_user_from_supabase(supabase_user)
            await self.user_repository.update_last_login(local_user.id)

            logger.info("User authenticated successfully: %s", email)

            return local_user, {"user": supabase_user, "session": auth_response.session}

        except AuthError as exc:
            logger.error("Supabase auth error during login: %s", exc)
            raise ValueError("Authentication failed") from exc
        except ValueError:
            raise
        except Exception as exc:
            logger.error("Login failed for %s: %s", email, exc)
            raise

    async def refresh_session(self, refresh_token: str) -> Dict:
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            if response.session is None:
                raise ValueError("Failed to refresh session")

            logger.info("Session refreshed successfully")
            return {"user": response.user, "session": response.session}

        except AuthError as exc:
            logger.error("Failed to refresh session: %s", exc)
            raise ValueError("Invalid refresh token") from exc

    async def logout_user(self, access_token: str) -> bool:
        try:
            self.supabase.auth.set_session(access_token, refresh_token="")
            self.supabase.auth.sign_out()
            logger.info("User logged out successfully")
            return True
        except AuthError as exc:
            logger.error("Failed to logout user: %s", exc)
            return False

    async def reset_password(self, email: str, redirect_to: Optional[str] = None) -> bool:
        try:
            self.supabase.auth.reset_password_email(
                email=email,
                options={"redirect_to": redirect_to} if redirect_to else None,
            )
            logger.info("Password reset email sent to: %s", email)
            return True
        except AuthError as exc:
            logger.error("Failed to send password reset email: %s", exc)
            return False

    async def update_user_password(
        self,
        user_id: str,
        new_password: str,
        access_token: str,
    ) -> bool:
        try:
            self.supabase.auth.set_session(access_token, refresh_token="")
            self.supabase.auth.update_user({"password": new_password})
            logger.info("Password updated for user: %s", user_id)
            return True
        except AuthError as exc:
            logger.error("Failed to update password: %s", exc)
            return False

    async def verify_email(self, token: str, email: str) -> bool:
        try:
            auth_response = self.supabase.auth.verify_otp(
                {"email": email, "token": token, "type": "signup"}
            )
            if auth_response.user:
                await self.user_repository.update_by_email(email, {"is_active": True})
                logger.info("Email verified for user: %s", email)
                return True
            return False
        except AuthError as exc:
            logger.error("Failed to verify email: %s", exc)
            return False

    async def get_user_from_token(self, access_token: str) -> Optional[User]:
        try:
            self.supabase.auth.set_session(access_token, refresh_token="")
            user_response = self.supabase.auth.get_user()
            if user_response.user is None:
                return None

            local_user = await self.user_repository.get_by_id(user_response.user.id)
            if not local_user:
                local_user = await self._sync_user_from_supabase(user_response.user)
            return local_user
        except AuthError as exc:
            logger.warning("Invalid access token: %s", exc)
            return None
        except Exception as exc:
            logger.error("Failed to get user from token: %s", exc)
            return None

    async def get_oauth_url(
        self,
        provider: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> Dict[str, str]:
        try:
            if not state:
                state = str(uuid.uuid4())

            provider_mapping = {"google": "google", "github": "github"}
            supabase_provider = provider_mapping.get(provider)
            if not supabase_provider:
                raise ValueError(f"Unsupported OAuth provider: {provider}")

            auth_response = self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": supabase_provider,
                    "options": {"redirect_to": redirect_uri, "state": state},
                }
            )

            logger.info("Generated OAuth URL for provider: %s", provider)
            return {"url": auth_response.url, "state": state}
        except Exception as exc:
            logger.error("Failed to generate OAuth URL for %s: %s", provider, exc)
            raise

    async def oauth_callback(
        self,
        provider: str,
        code: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> Tuple[User, Dict, bool]:
        try:
            auth_response = self.supabase.auth.exchange_code_for_session(
                {"auth_code": code}
            )

            if auth_response.user is None:
                raise ValueError("OAuth authentication failed")

            supabase_user = auth_response.user
            existing_user = await self.user_repository.get_by_id(supabase_user.id)
            is_new_user = existing_user is None

            if is_new_user:
                user_metadata = supabase_user.user_metadata or {}
                invitation_code = await self._ensure_unique_invitation_code()

                username = None
                if provider == "github":
                    username = user_metadata.get("user_name") or user_metadata.get(
                        "preferred_username"
                    )
                elif provider == "google" and supabase_user.email:
                    email_prefix = supabase_user.email.split("@")[0]
                    existing_username = await self.user_repository.get_by_username(
                        email_prefix
                    )
                    if not existing_username:
                        username = email_prefix

                user_data = UserCreate(
                    id=supabase_user.id,
                    email=supabase_user.email or "",
                    full_name=user_metadata.get("full_name") or username or "User",
                    username=username,
                    is_active=True,
                    auth_provider=provider,
                    external_id=supabase_user.id,
                    invitation_code=invitation_code,
                    user_metadata=user_metadata,
                )

                local_user = await self.user_repository.create(user_data)
            else:
                local_user = existing_user

            logger.info("OAuth authentication successful for user: %s", supabase_user.email)

            return local_user, {"user": supabase_user, "session": auth_response.session}, is_new_user
        except (AuthError, AuthApiError) as exc:
            logger.error("OAuth callback failed for provider %s: %s", provider, exc)
            raise ValueError("OAuth authentication failed") from exc
        except ValueError:
            raise
        except Exception as exc:
            logger.error("OAuth callback failed: %s", exc)
            raise

    async def _sync_user_from_supabase(self, supabase_user) -> User:
        local_user = await self.user_repository.get_by_id(supabase_user.id)

        user_metadata = supabase_user.user_metadata or {}

        if local_user:
            update_data = {
                "full_name": user_metadata.get("full_name", local_user.full_name),
                "username": user_metadata.get("username", local_user.username),
                "is_active": supabase_user.email_confirmed_at is not None,
                "user_metadata": user_metadata,
                "external_id": supabase_user.id,
            }
            await self.user_repository.update(local_user.id, update_data)
            local_user = await self.user_repository.get_by_id(supabase_user.id)
            return local_user

        user_data = UserCreate(
            id=supabase_user.id,
            email=supabase_user.email or "",
            full_name=user_metadata.get("full_name") or supabase_user.email or "User",
            username=user_metadata.get("username"),
            is_active=supabase_user.email_confirmed_at is not None,
            auth_provider="supabase",
            external_id=supabase_user.id,
            invitation_code=user_metadata.get("invitation_code"),
            user_metadata=user_metadata,
        )
        return await self.user_repository.create(user_data)


__all__ = ["SupabaseAuthService"]
