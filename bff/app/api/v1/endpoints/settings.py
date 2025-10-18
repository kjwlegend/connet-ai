"""
User Settings API Endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user
from app.modules.users.prompt_library.schemas import (
    UserPromptLibraryCreate,
    UserPromptLibraryResponse,
    UserPromptLibraryUpdate,
)
from app.modules.users.schemas import (
    InviteStatsResponse,
    OrderHistoryResponse,
    UserLLMSettingsResponse,
    UserLLMSettingsUpdate,
    UserSubscriptionResponse,
)
from app.modules.settings import SettingsService
from app.modules.users.models import UserModel

router = APIRouter()


# Subscription/Membership endpoints
@router.get("/subscription", response_model=UserSubscriptionResponse)
async def get_user_subscription(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's current subscription details."""
    return await settings_service.get_user_subscription(current_user.id)


@router.post("/subscription/upgrade")
async def upgrade_subscription(
    plan_type: str = Query(..., regex="^(basic|premium|enterprise)$"),
    billing_cycle: str = Query("monthly", regex="^(monthly|yearly)$"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Upgrade user's subscription plan."""
    return await settings_service.upgrade_subscription(
        user_id=current_user.id,
        plan_type=plan_type,
        billing_cycle=billing_cycle
    )


@router.post("/subscription/cancel")
async def cancel_subscription(
    cancel_at_period_end: bool = Query(True, description="Cancel at end of billing period"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Cancel user's subscription."""
    await settings_service.cancel_subscription(
        user_id=current_user.id,
        cancel_at_period_end=cancel_at_period_end
    )
    return {"message": "Subscription canceled successfully"}


# LLM Settings endpoints
@router.get("/llm", response_model=UserLLMSettingsResponse)
async def get_llm_settings(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's LLM model settings."""
    return await settings_service.get_llm_settings(current_user.id)


@router.put("/llm", response_model=UserLLMSettingsResponse)
async def update_llm_settings(
    settings_data: UserLLMSettingsUpdate,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Update user's LLM model settings."""
    return await settings_service.update_llm_settings(
        user_id=current_user.id,
        settings_data=settings_data
    )


@router.get("/llm/providers")
async def get_available_providers():
    """Get list of available LLM providers and models."""
    return await SettingsService.get_available_llm_providers()


@router.post("/llm/test-api-key")
async def test_api_key(
    provider: str = Query(..., description="Provider name"),
    api_key: str = Query(..., description="API key to test"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Test an API key for a specific provider."""
    is_valid = await settings_service.test_provider_api_key(provider, api_key)
    return {"provider": provider, "is_valid": is_valid}


# Prompt Library endpoints
@router.get("/prompts", response_model=List[UserPromptLibraryResponse])
async def get_user_prompts(
    skip: int = Query(0, ge=0, description="Skip prompts"),
    limit: int = Query(50, le=100, description="Limit prompts"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search prompts"),
    favorites_only: bool = Query(False, description="Only favorite prompts"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's custom prompt library."""
    return await settings_service.get_user_prompts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        category=category,
        search=search,
        favorites_only=favorites_only
    )


@router.post("/prompts", response_model=UserPromptLibraryResponse)
async def create_prompt(
    prompt_data: UserPromptLibraryCreate,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Create a new custom prompt."""
    return await settings_service.create_prompt(
        user_id=current_user.id,
        prompt_data=prompt_data
    )


@router.get("/prompts/{prompt_id}", response_model=UserPromptLibraryResponse)
async def get_prompt(
    prompt_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get specific prompt details."""
    return await settings_service.get_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id
    )


@router.put("/prompts/{prompt_id}", response_model=UserPromptLibraryResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_data: UserPromptLibraryUpdate,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Update a custom prompt."""
    return await settings_service.update_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_data=prompt_data
    )


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Delete a custom prompt."""
    await settings_service.delete_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id
    )
    return {"message": "Prompt deleted successfully"}


@router.post("/prompts/{prompt_id}/favorite")
async def toggle_favorite_prompt(
    prompt_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Toggle favorite status for a prompt."""
    is_favorite = await settings_service.toggle_favorite_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id
    )
    return {"message": f"Prompt {'added to' if is_favorite else 'removed from'} favorites"}


@router.get("/prompts/categories")
async def get_prompt_categories():
    """Get available prompt categories."""
    return {
        "categories": [
            {"key": "general", "name": "General", "description": "General purpose prompts"},
            {"key": "coding", "name": "Coding", "description": "Programming and development prompts"},
            {"key": "writing", "name": "Writing", "description": "Content creation and writing prompts"},
            {"key": "analysis", "name": "Analysis", "description": "Data analysis and research prompts"},
            {"key": "creative", "name": "Creative", "description": "Creative and artistic prompts"},
            {"key": "business", "name": "Business", "description": "Business and professional prompts"}
        ]
    }


# Invite System endpoints
@router.get("/invites", response_model=InviteStatsResponse)
async def get_invite_stats(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's invitation statistics and rewards."""
    return await settings_service.get_invite_stats(current_user.id)


@router.post("/invites/generate")
async def generate_invite_code(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Generate a new invitation code."""
    invite_data = await settings_service.generate_invite_code(current_user.id)
    return invite_data


@router.get("/invites/history")
async def get_invite_history(
    skip: int = Query(0, ge=0, description="Skip invites"),
    limit: int = Query(20, le=50, description="Limit invites"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's invitation history."""
    return await settings_service.get_invite_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# Order History endpoints  
@router.get("/orders", response_model=List[OrderHistoryResponse])
async def get_order_history(
    skip: int = Query(0, ge=0, description="Skip orders"),
    limit: int = Query(20, le=50, description="Limit orders"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get user's order/billing history."""
    return await settings_service.get_order_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# Account Management
@router.get("/account")
async def get_account_settings(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Get account settings and preferences."""
    return await settings_service.get_account_settings(current_user.id)


@router.put("/account") 
async def update_account_settings(
    settings_data: dict,
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Update account settings and preferences."""
    return await settings_service.update_account_settings(
        user_id=current_user.id,
        settings_data=settings_data
    )


@router.post("/account/export-data")
async def export_account_data(
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Export all user data (GDPR compliance)."""
    export_info = await settings_service.export_user_data(current_user.id)
    return export_info


@router.delete("/account")
async def delete_account(
    confirmation: str = Query(..., description="Type 'DELETE' to confirm"),
    current_user: UserModel = Depends(get_current_user),
    settings_service: SettingsService = Depends()
):
    """Delete user account (with confirmation)."""
    if confirmation != "DELETE":
        raise HTTPException(status_code=400, detail="Invalid confirmation")
    
    await settings_service.delete_user_account(current_user.id)
    return {"message": "Account deletion initiated"}
