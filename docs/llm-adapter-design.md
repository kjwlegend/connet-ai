# LLM Adapter Design Document

## Overview
This document outlines the architecture and implementation strategy for supporting multiple LLM providers in the Connet.AI platform, handling both user-provided API keys and platform-managed keys.

## Architecture Decision: Server-Side Processing

### Recommendation: **Server-Side Adapter Pattern**
We recommend implementing all LLM provider integrations on the **server side (BFF layer)** for the following reasons:

#### ✅ Advantages of Server-Side Processing:
1. **Security**: API keys never exposed to client/browser
2. **Unified Interface**: Single API endpoint regardless of provider
3. **Rate Limiting**: Centralized control over API usage
4. **Cost Management**: Track and limit usage per user/plan
5. **Error Handling**: Consistent error handling and retry logic
6. **Caching**: Response caching for identical requests
7. **Monitoring**: Centralized logging and metrics
8. **Provider Switching**: Easy to switch providers without client updates
9. **Compliance**: Better control over data flow for compliance requirements

#### ❌ Why Not Client-Side:
- Security risk: API keys visible in browser
- CORS issues with many providers
- Difficult to track usage and costs
- No centralized rate limiting
- Inconsistent error handling

## Proposed Architecture

### 1. Unified LLM Gateway (BFF Layer)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend  │────▶│  BFF Gateway │────▶│  LLM Providers   │
│             │     │              │     │                  │
│  - Chat UI  │     │  - Router    │     │  - OpenAI        │
│  - Settings │     │  - Adapter   │     │  - Anthropic     │
│             │     │  - RateLimit │     │  - Google        │
└─────────────┘     └──────────────┘     │  - DeepSeek      │
                                          │  - Kimi          │
                                          │  - Qwen          │
                                          └──────────────────┘
```

### 2. Adapter Pattern Implementation

```python
# bff/app/services/llm/base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator

class BaseLLMAdapter(ABC):
    """Base adapter interface for all LLM providers"""
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: list,
        model: str,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Standard chat completion interface"""
        pass
    
    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: list,
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion interface"""
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        text: str,
        model: str
    ) -> list[float]:
        """Text embeddings interface"""
        pass
```

### 3. Provider-Specific Adapters

```python
# bff/app/services/llm/adapters/openai_adapter.py
from openai import AsyncOpenAI
from ..base_adapter import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str = None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def chat_completion(self, messages, model, **kwargs):
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.model_dump()

# Similar implementations for other providers...
```

### 4. LLM Service Manager

```python
# bff/app/services/llm/manager.py
from typing import Dict, Optional
from .adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GoogleAdapter,
    DeepSeekAdapter,
    KimiAdapter,
    QwenAdapter
)

class LLMManager:
    """Manages multiple LLM providers and routes requests"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseLLMAdapter] = {}
        self.user_configs: Dict[str, Dict] = {}
    
    def register_user_config(self, user_id: str, provider: str, config: Dict):
        """Register user's LLM configuration"""
        if provider == "openai":
            adapter = OpenAIAdapter(config["api_key"], config.get("base_url"))
        elif provider == "anthropic":
            adapter = AnthropicAdapter(config["api_key"])
        elif provider == "google":
            adapter = GoogleAdapter(config["api_key"])
        elif provider == "deepseek":
            adapter = DeepSeekAdapter(config["api_key"])
        # ... other providers
        
        self.adapters[f"{user_id}_{provider}"] = adapter
        self.user_configs[user_id] = {
            "provider": provider,
            "models": config.get("models", {})
        }
    
    async def chat(self, user_id: str, messages: list, model_type: str = "chat"):
        """Route chat request to appropriate provider"""
        config = self.user_configs.get(user_id)
        
        if not config:
            # Use platform default based on user's membership
            config = self._get_default_config(user_id)
        
        provider = config["provider"]
        model = config["models"].get(model_type)
        adapter = self.adapters.get(f"{user_id}_{provider}")
        
        if not adapter:
            adapter = self._get_platform_adapter(provider)
        
        return await adapter.chat_completion(messages, model)
```

## Existing Solutions & Libraries

### Recommended: **LangChain** Integration

LangChain provides excellent abstractions for multiple LLM providers:

```python
# Using LangChain for unified interface
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage

class LangChainLLMAdapter:
    """Adapter using LangChain for provider abstraction"""
    
    PROVIDERS = {
        "openai": ChatOpenAI,
        "anthropic": ChatAnthropic,
        # Extended with custom providers
    }
    
    def __init__(self, provider: str, **kwargs):
        model_class = self.PROVIDERS.get(provider)
        self.model = model_class(**kwargs)
    
    async def chat(self, messages):
        return await self.model.ainvoke(messages)
```

### Alternative Solutions:

1. **LiteLLM** - Lightweight unified interface for 100+ LLMs
   ```python
   import litellm
   response = await litellm.acompletion(
       model="gpt-4",  # or "claude-3", "gemini-pro", etc.
       messages=messages
   )
   ```

2. **OpenRouter** - API gateway service (3rd party)
   - Single API endpoint for multiple providers
   - Usage-based pricing
   - Good for quick prototyping

3. **Custom Implementation** - Full control but more development effort

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up base adapter interface
- [ ] Implement OpenAI adapter
- [ ] Implement Google (Gemini) adapter
- [ ] Create LLM manager service
- [ ] Add user configuration storage

### Phase 2: Additional Providers (Week 2)
- [ ] Implement DeepSeek adapter
- [ ] Implement Kimi adapter
- [ ] Implement Qwen adapter
- [ ] Implement Anthropic adapter

### Phase 3: Advanced Features (Week 3)
- [ ] Add response caching
- [ ] Implement rate limiting per user/provider
- [ ] Add usage tracking and billing integration
- [ ] Implement fallback providers
- [ ] Add streaming support

### Phase 4: Optimization (Week 4)
- [ ] Add connection pooling
- [ ] Implement retry logic with exponential backoff
- [ ] Add provider health checks
- [ ] Optimize for latency

## API Design

### Endpoint Structure

```yaml
POST /api/v1/llm/chat
Content-Type: application/json
Authorization: Bearer {user_token}

{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "model_type": "chat",  # or "memory", "embedding"
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1000
}

Response:
{
  "id": "chat-123",
  "provider": "openai",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you today?"
    }
  }]
}
```

### Configuration Endpoint

```yaml
POST /api/v1/llm/config
Content-Type: application/json
Authorization: Bearer {user_token}

{
  "provider": "openai",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",  # optional
  "models": {
    "chat": "gpt-4",
    "memory": "gpt-3.5-turbo",
    "embedding": "text-embedding-3"
  }
}
```

## Security Considerations

1. **API Key Storage**: 
   - Encrypt API keys using AES-256
   - Store in secure database with access logging
   - Never log or return API keys in responses

2. **Rate Limiting**:
   - Per-user limits based on membership tier
   - Per-provider limits to prevent abuse
   - Circuit breaker for provider failures

3. **Input Validation**:
   - Sanitize all user inputs
   - Limit message size and token count
   - Validate model names against whitelist

4. **Audit Logging**:
   - Log all LLM requests (without content)
   - Track usage per user and provider
   - Monitor for anomalous patterns

## Cost Management

### Usage Tracking
```python
class UsageTracker:
    async def track_usage(
        self,
        user_id: str,
        provider: str,
        model: str,
        tokens: int,
        cost: float
    ):
        """Track usage for billing and limits"""
        # Store in database
        # Check against user limits
        # Trigger alerts if needed
```

### Membership-Based Limits
- **Free**: GPT-4o-mini, Gemini-2.0-flash only
- **Pro ($9.99)**: GPT-4o, Gemini-2.5-Pro
- **Premium ($19.99)**: All models including latest versions
- **Own API Key**: No model restrictions

## Monitoring & Observability

1. **Metrics to Track**:
   - Request latency per provider
   - Error rates
   - Token usage per user
   - Cost per request
   - Provider availability

2. **Recommended Tools**:
   - OpenTelemetry for distributed tracing
   - Prometheus for metrics
   - Grafana for visualization
   - Sentry for error tracking

## Conclusion

The server-side adapter pattern provides the best balance of security, flexibility, and control. Using LangChain or LiteLLM as a foundation will accelerate development while maintaining the ability to add custom providers and features.

## Next Steps

1. **Immediate Actions**:
   - Set up BFF LLM service structure
   - Implement OpenAI adapter as proof of concept
   - Create database schema for user configurations

2. **Testing Strategy**:
   - Unit tests for each adapter
   - Integration tests with mock providers
   - Load testing for concurrent users
   - Failover testing

3. **Documentation**:
   - API documentation with OpenAPI/Swagger
   - Provider-specific configuration guides
   - Troubleshooting guide for common issues