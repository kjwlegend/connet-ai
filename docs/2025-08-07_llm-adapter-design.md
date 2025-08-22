# LLM Adapter Design Document

## Overview

This document outlines the **simplified, unified architecture** for supporting multiple LLM providers in the Connet.AI platform.

**Core Principle**: All users go through the same backend architecture, with differences in available features and models based on their subscription tier.

## Architecture Decision: Unified Backend with Tiered Features

### Why Unified Architecture?

#### ✅ **Advantages**:

1. **Simplicity**: One codebase, one architecture to maintain
2. **Consistency**: Identical user experience across all tiers
3. **Reliability**: Proven patterns for multi-agent chat rooms
4. **Scalability**: Easy to add new providers and features
5. **Security**: Centralized security and monitoring
6. **Maintainability**: Single point of truth for business logic

#### ❌ **Why Not Hybrid/Mixed Approaches**:

- Exponential complexity in multi-agent scenarios
- Inconsistent user experience
- Double maintenance burden
- Complex error handling and debugging
- Poor upgrade conversion rates

## Proposed Architecture

### Unified LLM Gateway (BFF Layer)

```
All Users → Unified BFF → LLM Providers
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend  │────▶│  BFF Gateway │────▶│  LLM Providers   │
│             │     │              │     │                  │
│  - Chat UI  │     │  - Unified   │     │  - Platform Keys │
│  - Settings │     │    Service   │     │  - User Keys     │
│             │     │  - Tier      │     │    (BYOK)        │
│             │     │    Control   │     │  - OpenAI        │
│             │     │  - Multi     │     │  - Anthropic     │
│             │     │    Agent     │     │  - Google        │
└─────────────┘     └──────────────┘     │  - DeepSeek      │
                                        │  - Others        │
                                        └──────────────────┘
```

### User Tier Management

```python
# bff/app/services/llm/unified_service.py
from typing import Dict, Any, List
from enum import Enum

class UserTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UnifiedLLMService:
    """
    Single LLM service handling all users with tier-based features
    """

    TIER_FEATURES = {
        UserTier.FREE: {
            "models": ["gpt-3.5-turbo", "gemini-flash"],
            "custom_agents": 3,
            "daily_quota": 100,
            "multi_agent_limit": 2,
            "byok_allowed": False
        },
        UserTier.PRO: {
            "models": ["gpt-4", "claude-3.5", "gemini-pro"],
            "custom_agents": 50,
            "daily_quota": 2000,
            "multi_agent_limit": 10,
            "byok_allowed": True
        },
        UserTier.ENTERPRISE: {
            "models": "all",
            "custom_agents": "unlimited",
            "daily_quota": "unlimited",
            "multi_agent_limit": "unlimited",
            "byok_allowed": True
        }
    }

    async def chat(
        self,
        user_id: str,
        agent_config: Dict[str, Any],
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Unified chat interface for all users and agents"""

        # 1. Get user tier and validate quota
        user_tier = await self.get_user_tier(user_id)
        await self.validate_quota(user_id, user_tier)

        # 2. Get appropriate LLM adapter
        adapter = await self.get_llm_adapter(user_id, user_tier, agent_config)

        # 3. Execute chat with unified error handling
        return await adapter.chat_completion(
            messages=self.prepare_messages(agent_config, message, context),
            model=self.select_model(agent_config, user_tier),
            **self.get_parameters(agent_config, user_tier)
        )

    async def get_llm_adapter(self, user_id: str, tier: UserTier, agent_config: Dict):
        """Get appropriate adapter based on user configuration"""

        # Check if user has BYOK configuration
        user_api_key = await self.api_key_manager.get_user_key(
            user_id, agent_config.get("provider")
        )

        if user_api_key and tier.value in ["pro", "enterprise"]:
            # Use user's API key
            return self.create_byok_adapter(agent_config["provider"], user_api_key)
        else:
            # Use platform-managed keys
            return self.create_platform_adapter(agent_config["provider"])
```

### API Key Management (BYOK Support)

```python
# bff/app/services/llm/api_key_manager.py
from cryptography.fernet import Fernet
import os

class APIKeyManager:
    """
    Secure API key management for BYOK (Bring Your Own Key) users
    """

    def __init__(self):
        self.cipher = Fernet(os.environ["API_KEY_ENCRYPTION_KEY"])

    async def store_user_api_key(
        self,
        user_id: str,
        provider: str,
        api_key: str,
        user_consent: bool = True
    ):
        """Securely store user's API key with proper consent"""

        if not user_consent:
            raise ValueError("User consent required for API key storage")

        # Validate API key works
        is_valid = await self.validate_api_key(provider, api_key)
        if not is_valid:
            raise ValueError(f"Invalid {provider} API key")

        # Encrypt and store
        encrypted_key = self.cipher.encrypt(api_key.encode())

        await self.db.execute("""
            INSERT INTO user_api_keys (user_id, provider, encrypted_key, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (user_id, provider) DO UPDATE SET
                encrypted_key = excluded.encrypted_key,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, provider, encrypted_key, datetime.utcnow()))

        # Audit log
        await self.audit_logger.log_key_storage(user_id, provider)

    async def get_user_key(self, user_id: str, provider: str) -> str | None:
        """Retrieve and decrypt user's API key"""

        result = await self.db.fetch_one(
            "SELECT encrypted_key FROM user_api_keys WHERE user_id = ? AND provider = ?",
            (user_id, provider)
        )

        if not result:
            return None

        # Decrypt
        decrypted_key = self.cipher.decrypt(result["encrypted_key"]).decode()

        # Audit log
        await self.audit_logger.log_key_access(user_id, provider)

        return decrypted_key
```

### Multi-Agent Chat Support

```python
# bff/app/services/chat/multi_agent_manager.py
import asyncio
from typing import List

class MultiAgentChatManager:
    """
    Unified multi-agent chat manager
    All agents use the same execution pipeline regardless of configuration
    """

    def __init__(self, llm_service: UnifiedLLMService):
        self.llm_service = llm_service

    async def execute_multi_agent_chat(
        self,
        user_id: str,
        room_id: str,
        message: str,
        agents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute multi-agent chat with unified timeout and error handling"""

        # Validate user can use multi-agent features
        user_tier = await self.llm_service.get_user_tier(user_id)
        max_agents = self.llm_service.TIER_FEATURES[user_tier]["multi_agent_limit"]

        if len(agents) > max_agents:
            raise ValueError(f"Too many agents for {user_tier.value} tier")

        # Execute all agents concurrently with timeout
        tasks = []
        for agent in agents:
            task = asyncio.create_task(
                self._execute_agent_with_timeout(user_id, agent, message)
            )
            tasks.append((agent["id"], task))

        # Wait for all responses
        responses = []
        for agent_id, task in tasks:
            try:
                response = await asyncio.wait_for(task, timeout=30.0)
                responses.append({
                    "agent_id": agent_id,
                    "response": response,
                    "status": "success"
                })
            except asyncio.TimeoutError:
                responses.append({
                    "agent_id": agent_id,
                    "error": "Response timeout",
                    "status": "timeout"
                })
            except Exception as e:
                responses.append({
                    "agent_id": agent_id,
                    "error": str(e),
                    "status": "error"
                })

        return responses

    async def _execute_agent_with_timeout(
        self,
        user_id: str,
        agent: Dict[str, Any],
        message: str
    ):
        """Execute single agent with proper context and error handling"""

        context = await self.get_chat_context(agent["id"], message)

        return await self.llm_service.chat(
            user_id=user_id,
            agent_config=agent,
            message=message,
            context=context
        )
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

- [ ] Unified LLM service foundation
- [ ] User tier management system
- [ ] Secure API key storage (BYOK)
- [ ] Basic provider adapters (OpenAI, Anthropic)

### Phase 2: Multi-Agent Support (Week 3-4)

- [ ] Multi-agent chat manager
- [ ] Concurrent execution with timeout handling
- [ ] Context management across agents
- [ ] Error handling and fallback mechanisms

### Phase 3: Additional Providers & Features (Week 5-6)

- [ ] Add more providers (Google, DeepSeek, etc.)
- [ ] Advanced quota management
- [ ] Usage analytics and billing
- [ ] Performance optimization

### Phase 4: Enterprise Features (Week 7-8)

- [ ] Advanced security features
- [ ] Audit logging and compliance
- [ ] Custom deployment options
- [ ] Advanced monitoring and alerting

## API Design

### Unified Chat Endpoint

```yaml
POST /api/v1/chat
Content-Type: application/json
Authorization: Bearer {user_token}

{
  "agent_id": "agent_123",
  "message": "Hello, how can you help me?",
  "context": {
    "conversation_id": "conv_456",
    "history": [...]
  }
}

Response:
{
  "id": "response_789",
  "agent_id": "agent_123",
  "message": "Hello! I'm here to help you with...",
  "metadata": {
    "model": "gpt-4",
    "provider": "openai",
    "tokens_used": 150,
    "response_time_ms": 1200
  }
}
```

### Multi-Agent Chat Endpoint

```yaml
POST /api/v1/chat/multi-agent
Content-Type: application/json
Authorization: Bearer {user_token}

{
  "room_id": "room_123",
  "message": "What do you all think about this?",
  "agents": ["agent_1", "agent_2", "agent_3"]
}

Response:
{
  "room_id": "room_123",
  "responses": [
    {
      "agent_id": "agent_1",
      "response": "I think this is interesting because...",
      "status": "success"
    },
    {
      "agent_id": "agent_2",
      "response": "From my perspective...",
      "status": "success"
    }
  ]
}
```

### BYOK Configuration

```yaml
POST /api/v1/user/api-keys
Content-Type: application/json
Authorization: Bearer {user_token}

{
  "provider": "openai",
  "api_key": "sk-...",
  "consent": true
}

Response:
{
  "success": true,
  "provider": "openai",
  "status": "configured",
  "features_unlocked": [
    "Cost optimization",
    "Higher rate limits",
    "Custom model access"
  ]
}
```

## Security Considerations

### API Key Protection

1. **Encryption**: All user API keys encrypted with AES-256
2. **Access Control**: Keys only accessible during LLM calls
3. **Audit Logging**: All key access logged with user consent
4. **Consent Management**: Clear user consent for key storage

### Rate Limiting

1. **Tier-based Limits**: Different quotas per subscription tier
2. **Per-agent Limits**: Prevent abuse in multi-agent scenarios
3. **Provider Limits**: Respect upstream provider rate limits
4. **Circuit Breakers**: Automatic failover for provider issues

## Cost Management

### Usage Tracking

```python
class UsageTracker:
    async def track_usage(
        self,
        user_id: str,
        agent_id: str,
        provider: str,
        model: str,
        tokens: int,
        cost: float
    ):
        """Track usage for billing and quota management"""
        await self.db.execute("""
            INSERT INTO usage_logs
            (user_id, agent_id, provider, model, tokens, cost, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, agent_id, provider, model, tokens, cost, datetime.utcnow()))

        # Check quotas
        await self.check_and_enforce_quotas(user_id)
```

### Subscription Tiers

- **Free**: Basic models, limited agents, 100 daily requests
- **Pro ($19/month)**: Advanced models, BYOK option, higher limits
- **Enterprise**: Custom pricing, unlimited usage, dedicated support

## Conclusion

This simplified, unified architecture provides:

### ✅ **Technical Benefits**

- **Single codebase** to maintain and debug
- **Consistent performance** across all features
- **Reliable multi-agent support** with proper error handling
- **Scalable foundation** for future growth

### ✅ **Business Benefits**

- **Clear upgrade path** from free to paid tiers
- **Reduced support complexity** with unified experience
- **Cost optimization** through BYOK for power users
- **Enterprise-ready** with proper security and compliance

### ✅ **User Benefits**

- **Consistent experience** regardless of subscription
- **Powerful multi-agent capabilities** that actually work
- **Flexible payment options** (platform credits or BYOK)
- **Simple configuration** without technical complexity

**Focus on what matters**: Building amazing multi-agent experiences, not managing complex technical architectures.

## Next Steps

1. **Week 1**: Start with unified LLM service and basic tier management
2. **Week 2**: Add secure BYOK support for Pro+ users
3. **Week 3**: Implement robust multi-agent chat manager
4. **Week 4**: Add more providers and polish the experience

Keep it simple, keep it unified, and focus on delivering value to users! 🚀
