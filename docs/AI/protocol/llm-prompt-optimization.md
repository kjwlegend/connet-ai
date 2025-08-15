# LLM 提示词结构优化 - 缓存友好设计

## 🎯 目标

设计一个最大化利用 LLM 厂商 cached context 功能的提示词结构，以最小化 token 消耗和请求成本。

## 📊 缓存机制分析

### 主要厂商缓存策略

| 厂商             | 缓存机制        | 缓存时长  | 命中条件     |
| ---------------- | --------------- | --------- | ------------ |
| **OpenAI**       | Prompt Caching  | 5-10 分钟 | 前缀完全匹配 |
| **Anthropic**    | Context Caching | 5 分钟    | 前缀完全匹配 |
| **Google**       | Context Caching | 1 小时    | 前缀完全匹配 |
| **Azure OpenAI** | Prompt Caching  | 10 分钟   | 前缀完全匹配 |

### 核心原理

1. **前缀匹配**: 只有提示词的前缀部分完全相同才能命中缓存
2. **最小长度**: 通常需要 1024+ tokens 才启用缓存
3. **优先级**: 静态内容应放在前面，动态内容放在后面

## 🏗️ 内容分类与优先级

### 📌 静态内容（缓存友好 - 高优先级）

```
优先级 1: 全局提示词 (Global Prompt)
优先级 2: 智能体身份提示词 (Agent Identity)
优先级 3: 用户自定义提示词 (User Custom Prompt)
优先级 4: 长期记忆 (Long-term Memory) - 相对稳定
```

### 🔄 动态内容（按变化频率排序）

```
优先级 5: 会话记忆 (Session Memory) - 会话内相对稳定
优先级 6: 短期记忆 (Short-term Memory) - 中等变化频率
优先级 7: 对话历史 (Chat History) - 每轮增长
优先级 8: 工具调用结果 (Tools Results) - 每次调用变化
```

## 🎨 最优提示词结构

### 1. 层级结构设计

```
┌─────────────────────────────────────┐
│ 第一层: 全局系统提示词 (Global)      │ ← 缓存层 1 (最稳定)
├─────────────────────────────────────┤
│ 第二层: 智能体身份 (Agent Identity)  │ ← 缓存层 2 (稳定)
├─────────────────────────────────────┤
│ 第三层: 用户定制 (User Custom)       │ ← 缓存层 3 (较稳定)
├─────────────────────────────────────┤
│ 第四层: 长期记忆 (Long-term Memory)  │ ← 缓存层 4 (变化慢)
├─────────────────────────────────────┤
│ 第五层: 会话记忆 (Session Memory)    │ ← 缓存边界
├─────────────────────────────────────┤
│ 第六层: 短期记忆 (Short-term Memory) │ ← 动态内容开始
├─────────────────────────────────────┤
│ 第七层: 对话历史 (Chat History)      │ ← 高频变化
├─────────────────────────────────────┤
│ 第八层: 工具结果 (Tools Results)     │ ← 最高频变化
└─────────────────────────────────────┘
```

### 2. 具体模板结构

```python
class OptimizedPromptBuilder:
    """缓存优化的提示词构建器"""

    def __init__(self):
        self.cache_boundary_marker = "=== CACHE_BOUNDARY ==="
        self.section_separators = {
            "global": "=== GLOBAL_CONTEXT ===",
            "agent": "=== AGENT_IDENTITY ===",
            "user_custom": "=== USER_CUSTOM ===",
            "long_memory": "=== LONG_TERM_MEMORY ===",
            "session_memory": "=== SESSION_MEMORY ===",
            "short_memory": "=== SHORT_TERM_MEMORY ===",
            "chat_history": "=== CHAT_HISTORY ===",
            "tools_results": "=== TOOLS_RESULTS ==="
        }

    def build_prompt(self, context: Dict) -> str:
        """构建优化的提示词"""

        # 第一层: 全局系统提示词 (最稳定 - 缓存核心)
        global_prompt = self._build_global_section(context.get('global_prompt', ''))

        # 第二层: 智能体身份定义 (稳定)
        agent_identity = self._build_agent_section(context.get('agent_profile', {}))

        # 第三层: 用户自定义提示词 (较稳定)
        user_custom = self._build_user_custom_section(context.get('user_custom', ''))

        # 第四层: 长期记忆 (变化较慢)
        long_memory = self._build_long_memory_section(context.get('long_memory', []))

        # === 缓存边界标记 ===
        cache_boundary = f"\n{self.cache_boundary_marker}\n"

        # 第五层: 会话记忆 (会话内相对稳定)
        session_memory = self._build_session_memory_section(context.get('session_memory', []))

        # 第六层: 短期记忆 (中等变化频率)
        short_memory = self._build_short_memory_section(context.get('short_memory', []))

        # 第七层: 对话历史 (每轮增长)
        chat_history = self._build_chat_history_section(context.get('chat_history', []))

        # 第八层: 工具调用结果 (最高变化频率)
        tools_results = self._build_tools_section(context.get('tools_results', []))

        # 组合完整提示词
        prompt = (
            global_prompt +
            agent_identity +
            user_custom +
            long_memory +
            cache_boundary +
            session_memory +
            short_memory +
            chat_history +
            tools_results
        )

        return prompt

    def _build_global_section(self, global_prompt: str) -> str:
        """构建全局提示词部分"""
        if not global_prompt:
            global_prompt = """
You are an intelligent AI agent operating in a multi-agent collaboration environment.
Your primary goal is to work effectively with other agents to complete complex tasks.

Core Principles:
1. Always prioritize accuracy and helpfulness
2. Collaborate effectively with other agents
3. Use available tools and memory efficiently
4. Maintain context awareness across conversations
5. Provide clear, actionable responses
"""

        return f"""
{self.section_separators['global']}

{global_prompt.strip()}

IMPORTANT: Follow all instructions carefully and maintain consistency throughout the conversation.
"""

    def _build_agent_section(self, agent_profile: Dict) -> str:
        """构建智能体身份部分"""
        agent_id = agent_profile.get('agent_id', 'unknown')
        name = agent_profile.get('name', 'AI Assistant')
        capabilities = agent_profile.get('capabilities', [])
        description = agent_profile.get('description', '')

        capabilities_text = "\n".join([f"- {cap}" for cap in capabilities]) if capabilities else "- General assistance"

        return f"""
{self.section_separators['agent']}

Agent Identity:
- ID: {agent_id}
- Name: {name}
- Description: {description}

Capabilities:
{capabilities_text}

You should act according to your defined capabilities and maintain your identity throughout the conversation.
"""

    def _build_user_custom_section(self, user_custom: str) -> str:
        """构建用户自定义部分"""
        if not user_custom:
            return ""

        return f"""
{self.section_separators['user_custom']}

User Custom Instructions:
{user_custom.strip()}

Please follow these custom instructions in addition to your default behavior.
"""

    def _build_long_memory_section(self, long_memory: List[Dict]) -> str:
        """构建长期记忆部分"""
        if not long_memory:
            return ""

        # 只取最相关的长期记忆，控制 token 数量
        relevant_memories = long_memory[:5] if len(long_memory) > 5 else long_memory

        memory_text = ""
        for i, memory in enumerate(relevant_memories, 1):
            content = memory.get('content', '')
            relevance = memory.get('relevance_score', 0)
            memory_text += f"{i}. [Relevance: {relevance:.2f}] {content}\n"

        return f"""
{self.section_separators['long_memory']}

Long-term Memory (Key Information):
{memory_text}

Use this historical context to inform your responses when relevant.
"""

    def _build_session_memory_section(self, session_memory: List[Dict]) -> str:
        """构建会话记忆部分"""
        if not session_memory:
            return ""

        memory_text = ""
        for i, memory in enumerate(session_memory, 1):
            content = memory.get('content', '')
            timestamp = memory.get('timestamp', '')
            memory_text += f"{i}. [{timestamp}] {content}\n"

        return f"""
{self.section_separators['session_memory']}

Session Memory (Current Session Context):
{memory_text}

This represents the key events and decisions from the current session.
"""

    def _build_short_memory_section(self, short_memory: List[Dict]) -> str:
        """构建短期记忆部分"""
        if not short_memory:
            return ""

        # 短期记忆按时间倒序，最新的在前
        recent_memories = short_memory[:10] if len(short_memory) > 10 else short_memory

        memory_text = ""
        for i, memory in enumerate(recent_memories, 1):
            content = memory.get('content', '')
            timestamp = memory.get('timestamp', '')
            memory_text += f"{i}. [{timestamp}] {content}\n"

        return f"""
{self.section_separators['short_memory']}

Short-term Memory (Recent Context):
{memory_text}

Use this recent context to maintain continuity in the conversation.
"""

    def _build_chat_history_section(self, chat_history: List[Dict]) -> str:
        """构建对话历史部分"""
        if not chat_history:
            return ""

        # 保留最近的对话，控制长度
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

        history_text = ""
        for msg in recent_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            # 格式化不同角色的消息
            if role == 'user':
                history_text += f"User: {content}\n"
            elif role == 'assistant':
                history_text += f"Assistant: {content}\n"
            elif role == 'system':
                history_text += f"System: {content}\n"
            else:
                history_text += f"{role}: {content}\n"

        return f"""
{self.section_separators['chat_history']}

Recent Conversation:
{history_text}

Continue the conversation naturally based on this history.
"""

    def _build_tools_section(self, tools_results: List[Dict]) -> str:
        """构建工具调用结果部分"""
        if not tools_results:
            return ""

        tools_text = ""
        for i, result in enumerate(tools_results, 1):
            tool_name = result.get('tool_name', 'unknown')
            tool_input = result.get('input', {})
            tool_output = result.get('output', '')
            timestamp = result.get('timestamp', '')

            tools_text += f"""
{i}. Tool: {tool_name}
   Input: {json.dumps(tool_input, ensure_ascii=False)}
   Output: {tool_output}
   Time: {timestamp}
"""

        return f"""
{self.section_separators['tools_results']}

Recent Tool Results:
{tools_text}

Use these tool results to inform your response. Reference specific results when relevant.
"""
```

## 💰 成本优化策略

### 1. 缓存分层策略

```python
class CacheOptimizedAgent:
    """缓存优化的智能体"""

    def __init__(self, agent_profile: Dict):
        self.agent_profile = agent_profile
        self.prompt_builder = OptimizedPromptBuilder()

        # 缓存层配置
        self.cache_layers = {
            "static_cache": {  # 缓存层 1-4 (最稳定)
                "ttl": 3600,  # 1小时
                "content": ["global", "agent", "user_custom", "long_memory"]
            },
            "session_cache": {  # 缓存层 5 (会话稳定)
                "ttl": 1800,  # 30分钟
                "content": ["session_memory"]
            },
            "dynamic": {  # 动态内容 (不缓存)
                "content": ["short_memory", "chat_history", "tools_results"]
            }
        }

    def estimate_cache_hit_rate(self, context_changes: Dict) -> float:
        """估算缓存命中率"""
        total_tokens = 0
        cached_tokens = 0

        # 计算各部分 token 数
        for layer, config in self.cache_layers.items():
            layer_tokens = sum(
                len(str(context_changes.get(content_type, ""))) * 0.75  # 估算 token 数
                for content_type in config["content"]
            )
            total_tokens += layer_tokens

            if layer != "dynamic":
                cached_tokens += layer_tokens

        return cached_tokens / total_tokens if total_tokens > 0 else 0

    def optimize_memory_selection(self, memories: List[Dict], max_tokens: int = 1000) -> List[Dict]:
        """优化记忆选择，控制 token 数量"""
        # 按相关性和重要性排序
        sorted_memories = sorted(
            memories,
            key=lambda x: (x.get('relevance_score', 0) + x.get('importance_score', 0)) / 2,
            reverse=True
        )

        selected_memories = []
        current_tokens = 0

        for memory in sorted_memories:
            memory_tokens = len(str(memory.get('content', ''))) * 0.75  # 估算
            if current_tokens + memory_tokens <= max_tokens:
                selected_memories.append(memory)
                current_tokens += memory_tokens
            else:
                break

        return selected_memories
```

### 2. 动态内容管理

```python
class DynamicContentManager:
    """动态内容管理器"""

    def __init__(self, max_chat_history: int = 10, max_tools_results: int = 5):
        self.max_chat_history = max_chat_history
        self.max_tools_results = max_tools_results

    def truncate_chat_history(self, chat_history: List[Dict]) -> List[Dict]:
        """截断对话历史，保留最重要的部分"""
        if len(chat_history) <= self.max_chat_history:
            return chat_history

        # 保留最新的对话 + 重要的历史对话
        recent_messages = chat_history[-self.max_chat_history//2:]

        # 从剩余消息中选择重要的
        remaining_messages = chat_history[:-self.max_chat_history//2]
        important_messages = [
            msg for msg in remaining_messages
            if msg.get('importance', 0) > 0.7 or 'important' in msg.get('tags', [])
        ]

        # 合并并按时间排序
        selected_messages = important_messages + recent_messages
        return sorted(selected_messages, key=lambda x: x.get('timestamp', ''))

    def filter_tool_results(self, tools_results: List[Dict]) -> List[Dict]:
        """过滤工具结果，只保留最相关的"""
        if len(tools_results) <= self.max_tools_results:
            return tools_results

        # 按时间和重要性排序
        sorted_results = sorted(
            tools_results,
            key=lambda x: (
                x.get('timestamp', ''),
                x.get('relevance_score', 0)
            ),
            reverse=True
        )

        return sorted_results[:self.max_tools_results]
```

## 📊 实际示例

### 示例 1: 代码智能体的提示词

```python
# 示例上下文
context = {
    "global_prompt": "You are part of a multi-agent development team.",
    "agent_profile": {
        "agent_id": "code_agent_001",
        "name": "Senior Code Assistant",
        "capabilities": ["code_generation", "code_review", "debugging"],
        "description": "Specialized in Python, JavaScript, and system architecture"
    },
    "user_custom": "Focus on clean, maintainable code with comprehensive comments.",
    "long_memory": [
        {
            "content": "User prefers functional programming patterns",
            "relevance_score": 0.9,
            "importance_score": 0.8
        }
    ],
    "session_memory": [
        {
            "content": "Working on a data processing pipeline project",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    ],
    "short_memory": [
        {
            "content": "User mentioned performance optimization is critical",
            "timestamp": "2024-01-15T10:15:00Z"
        }
    ],
    "chat_history": [
        {
            "role": "user",
            "content": "Can you help me optimize this data processing function?",
            "timestamp": "2024-01-15T10:20:00Z"
        }
    ],
    "tools_results": [
        {
            "tool_name": "code_analyzer",
            "input": {"code": "def process_data(data): ..."},
            "output": "Function has O(n²) complexity, suggest optimization",
            "timestamp": "2024-01-15T10:21:00Z"
        }
    ]
}

# 构建优化的提示词
builder = OptimizedPromptBuilder()
optimized_prompt = builder.build_prompt(context)
```

### 生成的提示词结构 (缩略版):

```
=== GLOBAL_CONTEXT ===
You are part of a multi-agent development team...

=== AGENT_IDENTITY ===
Agent Identity:
- ID: code_agent_001
- Name: Senior Code Assistant
...

=== USER_CUSTOM ===
User Custom Instructions:
Focus on clean, maintainable code with comprehensive comments.

=== LONG_TERM_MEMORY ===
Long-term Memory (Key Information):
1. [Relevance: 0.90] User prefers functional programming patterns

=== CACHE_BOUNDARY ===

=== SESSION_MEMORY ===
Session Memory (Current Session Context):
1. [2024-01-15T10:00:00Z] Working on a data processing pipeline project

=== SHORT_TERM_MEMORY ===
Short-term Memory (Recent Context):
1. [2024-01-15T10:15:00Z] User mentioned performance optimization is critical

=== CHAT_HISTORY ===
Recent Conversation:
User: Can you help me optimize this data processing function?

=== TOOLS_RESULTS ===
Recent Tool Results:
1. Tool: code_analyzer
   Input: {"code": "def process_data(data): ..."}
   Output: Function has O(n²) complexity, suggest optimization
   Time: 2024-01-15T10:21:00Z
```

## 📈 性能分析

### 缓存命中率估算

| 内容类型       | Token 占比 | 缓存可能性   | 成本节省  |
| -------------- | ---------- | ------------ | --------- |
| Global Prompt  | 15%        | 95%          | 14.25%    |
| Agent Identity | 10%        | 90%          | 9%        |
| User Custom    | 5%         | 80%          | 4%        |
| Long Memory    | 20%        | 70%          | 14%       |
| Session Memory | 15%        | 60%          | 9%        |
| Short Memory   | 15%        | 30%          | 4.5%      |
| Chat History   | 15%        | 10%          | 1.5%      |
| Tools Results  | 5%         | 5%           | 0.25%     |
| **总计**       | **100%**   | **平均 55%** | **56.5%** |

### 实际成本节省示例

```python
# 成本计算示例
class CostCalculator:
    def __init__(self, input_cost_per_1k: float = 0.01, output_cost_per_1k: float = 0.03):
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k

    def calculate_costs(self, prompt_tokens: int, completion_tokens: int, cache_hit_rate: float):
        """计算缓存优化前后的成本"""
        # 原始成本
        original_input_cost = (prompt_tokens / 1000) * self.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * self.output_cost_per_1k
        original_total = original_input_cost + output_cost

        # 缓存优化后成本
        cached_tokens = prompt_tokens * cache_hit_rate
        paid_input_tokens = prompt_tokens - cached_tokens
        optimized_input_cost = (paid_input_tokens / 1000) * self.input_cost_per_1k
        optimized_total = optimized_input_cost + output_cost

        savings = original_total - optimized_total
        savings_percentage = (savings / original_total) * 100

        return {
            "original_cost": original_total,
            "optimized_cost": optimized_total,
            "savings": savings,
            "savings_percentage": savings_percentage
        }

# 示例计算
calculator = CostCalculator()
result = calculator.calculate_costs(
    prompt_tokens=2000,      # 2K tokens 提示词
    completion_tokens=500,   # 500 tokens 响应
    cache_hit_rate=0.565     # 56.5% 缓存命中率
)

print(f"原始成本: ${result['original_cost']:.4f}")
print(f"优化成本: ${result['optimized_cost']:.4f}")
print(f"节省: ${result['savings']:.4f} ({result['savings_percentage']:.1f}%)")
```

## 🛠️ 实施建议

### 1. 逐步实施策略

```python
# Phase 1: 基础结构
class Phase1Implementation:
    """第一阶段: 实现基础分层结构"""

    def __init__(self):
        self.static_sections = ["global", "agent", "user_custom"]
        self.dynamic_sections = ["chat_history", "tools_results"]

    def build_basic_prompt(self, context: Dict) -> str:
        """构建基础的分层提示词"""
        # 实现简单的静态+动态分层
        pass

# Phase 2: 记忆优化
class Phase2Implementation(Phase1Implementation):
    """第二阶段: 加入记忆管理"""

    def __init__(self):
        super().__init__()
        self.memory_sections = ["long_memory", "session_memory", "short_memory"]

    def optimize_memory_usage(self, memories: List[Dict]) -> List[Dict]:
        """优化记忆使用"""
        # 实现记忆选择和截断逻辑
        pass

# Phase 3: 智能缓存
class Phase3Implementation(Phase2Implementation):
    """第三阶段: 智能缓存优化"""

    def __init__(self):
        super().__init__()
        self.cache_monitor = CacheMonitor()

    def adaptive_caching(self, context: Dict) -> str:
        """自适应缓存策略"""
        # 实现动态缓存边界调整
        pass
```

### 2. 监控和调优

```python
class PromptOptimizationMonitor:
    """提示词优化监控器"""

    def __init__(self):
        self.metrics = {
            "cache_hit_rate": [],
            "token_usage": [],
            "cost_savings": [],
            "response_quality": []
        }

    def track_request(self, request_data: Dict):
        """跟踪请求数据"""
        self.metrics["cache_hit_rate"].append(request_data.get("cache_hit_rate", 0))
        self.metrics["token_usage"].append(request_data.get("prompt_tokens", 0))

    def get_optimization_report(self) -> Dict:
        """生成优化报告"""
        if not self.metrics["cache_hit_rate"]:
            return {"error": "No data available"}

        avg_cache_hit = sum(self.metrics["cache_hit_rate"]) / len(self.metrics["cache_hit_rate"])
        avg_tokens = sum(self.metrics["token_usage"]) / len(self.metrics["token_usage"])

        return {
            "average_cache_hit_rate": f"{avg_cache_hit:.2%}",
            "average_prompt_tokens": int(avg_tokens),
            "total_requests": len(self.metrics["cache_hit_rate"]),
            "optimization_suggestions": self._generate_suggestions(avg_cache_hit)
        }

    def _generate_suggestions(self, cache_hit_rate: float) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if cache_hit_rate < 0.3:
            suggestions.append("缓存命中率过低，考虑调整静态内容结构")
        elif cache_hit_rate < 0.5:
            suggestions.append("可以通过优化记忆选择策略提高缓存效率")
        elif cache_hit_rate > 0.8:
            suggestions.append("缓存效率很好，可以考虑增加更多动态内容")

        return suggestions
```

## 🎯 最佳实践总结

### ✅ 应该做的

1. **静态内容前置**: 将全局提示词、智能体身份等稳定内容放在最前面
2. **分层设计**: 按内容变化频率分层，形成明确的缓存边界
3. **长度控制**: 确保静态部分足够长（>1024 tokens）以触发缓存
4. **记忆筛选**: 智能选择最相关的记忆，避免无关信息
5. **监控优化**: 持续监控缓存命中率和成本节省效果

### ❌ 避免的问题

1. **频繁变动前缀**: 不要在提示词前部放置经常变化的内容
2. **过长动态部分**: 控制对话历史和工具结果的长度
3. **无序记忆**: 避免随机排列记忆，应按重要性和相关性排序
4. **忽略 token 限制**: 注意模型的上下文长度限制
5. **缺乏版本控制**: 提示词模板变更应有版本管理

---

通过这种缓存友好的提示词设计，可以在保持智能体性能的同时，显著降低 LLM 调用成本。预期可实现 **40-60% 的成本节省**，同时提高响应速度。
