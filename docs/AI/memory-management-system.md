# AI Memory Management System - 记忆管理系统

## 🧠 记忆系统概览

Connet.AI 采用三层记忆架构，模拟人类认知记忆模式：短期记忆(Working Memory)、中期记忆(Episodic Memory)、长期记忆(Semantic Memory)。这种设计确保 AI 能够在不同时间尺度上保持上下文连贯性，同时优化存储效率和检索性能。

---

## 📊 三层记忆架构

### 1. 短期记忆 (Short-term Memory)

**定位**: 当前会话的工作记忆  
**生命周期**: 15分钟 - 2小时  
**存储介质**: Redis (内存缓存)  
**容量限制**: 每个对话 4K tokens  

```python
class ShortTermMemory:
    """短期记忆管理器"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl_minutes = 30  # 默认TTL
        self.max_tokens = 4000
    
    async def store_message(self, conversation_id: str, message: Message):
        """存储消息到短期记忆"""
        key = f"stm:{conversation_id}"
        
        # 获取当前记忆
        current_memory = await self.redis.lrange(key, 0, -1)
        
        # Token 计数检查
        total_tokens = sum(self._count_tokens(msg) for msg in current_memory)
        if total_tokens + self._count_tokens(message.content) > self.max_tokens:
            await self._compress_memory(conversation_id)
        
        # 存储新消息
        message_data = {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender_id,
            'timestamp': message.created_at.isoformat(),
            'message_type': message.message_type,
            'metadata': message.metadata
        }
        
        await self.redis.lpush(key, json.dumps(message_data))
        await self.redis.expire(key, self.ttl_minutes * 60)
    
    async def get_context_window(self, conversation_id: str, window_size: int = 10) -> List[Message]:
        """获取上下文窗口"""
        key = f"stm:{conversation_id}"
        messages = await self.redis.lrange(key, 0, window_size - 1)
        
        return [Message.from_dict(json.loads(msg)) for msg in messages]
    
    async def _compress_memory(self, conversation_id: str):
        """压缩记忆 - 转移到中期记忆"""
        messages = await self.get_context_window(conversation_id, -1)  # 获取所有
        
        # 创建对话摘要
        summary = await self._create_summary(messages[10:])  # 保留最近10条
        
        # 转移到中期记忆
        medium_memory = MediumTermMemory()
        await medium_memory.store_summary(conversation_id, summary)
        
        # 清理旧消息，保留最近消息
        key = f"stm:{conversation_id}"
        await self.redis.ltrim(key, 0, 9)  # 保留最近10条
```

### 2. 中期记忆 (Medium-term Memory)

**定位**: 对话摘要和重要信息提取  
**生命周期**: 1天 - 1个月  
**存储介质**: PostgreSQL + Redis 缓存  
**容量限制**: 每个对话摘要 ~1K tokens  

```python
class MediumTermMemory:
    """中期记忆管理器"""
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        self.db = db_session
        self.redis = redis_client
        self.ttl_days = 30
    
    async def store_summary(self, conversation_id: str, summary: ConversationSummary):
        """存储对话摘要"""
        
        # 存储到数据库
        summary_record = ConversationSummaryModel(
            conversation_id=conversation_id,
            summary_text=summary.text,
            key_points=summary.key_points,
            entities=summary.entities,
            sentiment=summary.sentiment,
            topics=summary.topics,
            created_at=datetime.utcnow()
        )
        
        self.db.add(summary_record)
        await self.db.commit()
        
        # 缓存热点数据
        cache_key = f"mtm:summary:{conversation_id}"
        await self.redis.setex(
            cache_key, 
            3600 * 24,  # 1天缓存
            json.dumps(summary.to_dict())
        )
    
    async def extract_important_info(self, messages: List[Message]) -> ImportantInfo:
        """提取重要信息"""
        
        # 使用 LLM 提取关键信息
        extraction_prompt = f"""
        从以下对话中提取重要信息：
        
        对话内容：
        {self._format_messages_for_extraction(messages)}
        
        请提取：
        1. 关键决策和结论
        2. 重要的人物和实体
        3. 任务和待办事项
        4. 重要的时间点和截止日期
        5. 用户偏好和设置变更
        
        以JSON格式返回结果。
        """
        
        # 调用 LLM 提取
        llm_response = await self.llm_client.complete(extraction_prompt)
        extracted_info = json.loads(llm_response.content)
        
        return ImportantInfo(
            decisions=extracted_info.get('decisions', []),
            entities=extracted_info.get('entities', []),
            tasks=extracted_info.get('tasks', []),
            deadlines=extracted_info.get('deadlines', []),
            preferences=extracted_info.get('preferences', {})
        )
    
    async def get_relevant_summaries(self, conversation_id: str, query: str) -> List[ConversationSummary]:
        """获取相关摘要"""
        
        # 先检查缓存
        cache_key = f"mtm:relevant:{conversation_id}:{hash(query)}"
        cached_result = await self.redis.get(cache_key)
        if cached_result:
            return [ConversationSummary.from_dict(item) for item in json.loads(cached_result)]
        
        # 从数据库检索
        summaries = await self.db.execute(
            select(ConversationSummaryModel)
            .where(ConversationSummaryModel.conversation_id == conversation_id)
            .order_by(ConversationSummaryModel.created_at.desc())
            .limit(10)
        )
        
        # 语义匹配 (使用向量相似度)
        relevant_summaries = await self._semantic_match(query, summaries.scalars().all())
        
        # 缓存结果
        await self.redis.setex(cache_key, 1800, json.dumps([s.to_dict() for s in relevant_summaries]))
        
        return relevant_summaries
    
    async def update_user_preferences(self, user_id: str, new_preferences: dict):
        """更新用户偏好"""
        
        # 获取现有偏好
        existing_prefs = await self._get_user_preferences(user_id)
        
        # 合并偏好 (智能合并，考虑时间权重)
        updated_prefs = await self._merge_preferences(existing_prefs, new_preferences)
        
        # 存储更新后的偏好
        await self._store_user_preferences(user_id, updated_prefs)
        
        # 清除相关缓存
        await self.redis.delete(f"user_prefs:{user_id}")
```

### 3. 长期记忆 (Long-term Memory)

**定位**: 用户画像、知识图谱、历史模式  
**生命周期**: 永久存储  
**存储介质**: PostgreSQL + 向量数据库 (pgvector/Chroma)  
**容量限制**: 无限制，基于向量相似度检索  

```python
class LongTermMemory:
    """长期记忆管理器"""
    
    def __init__(self, db_session: AsyncSession, vector_store: VectorStore):
        self.db = db_session
        self.vector_store = vector_store
        self.embedding_model = "text-embedding-3-small"
    
    async def build_user_profile(self, user_id: str) -> UserProfile:
        """构建/更新用户画像"""
        
        # 收集用户历史数据
        user_data = await self._collect_user_data(user_id)
        
        # 分析用户行为模式
        behavior_patterns = await self._analyze_behavior_patterns(user_data)
        
        # 提取用户偏好
        preferences = await self._extract_user_preferences(user_data)
        
        # 构建兴趣图谱
        interest_graph = await self._build_interest_graph(user_data)
        
        # 创建用户画像
        profile = UserProfile(
            user_id=user_id,
            behavior_patterns=behavior_patterns,
            preferences=preferences,
            interest_graph=interest_graph,
            communication_style=await self._analyze_communication_style(user_data),
            expertise_areas=await self._identify_expertise_areas(user_data),
            updated_at=datetime.utcnow()
        )
        
        # 存储用户画像
        await self._store_user_profile(profile)
        
        return profile
    
    async def store_knowledge(self, knowledge: Knowledge):
        """存储知识到长期记忆"""
        
        # 创建知识向量
        embedding = await self._create_embedding(knowledge.content)
        
        # 存储到向量数据库
        await self.vector_store.store(
            id=knowledge.id,
            vector=embedding,
            metadata={
                'type': knowledge.type,
                'source': knowledge.source,
                'relevance_score': knowledge.relevance_score,
                'created_at': knowledge.created_at.isoformat(),
                'tags': knowledge.tags
            },
            content=knowledge.content
        )
        
        # 存储到关系数据库
        knowledge_record = KnowledgeModel(
            id=knowledge.id,
            user_id=knowledge.user_id,
            content=knowledge.content,
            knowledge_type=knowledge.type,
            source=knowledge.source,
            tags=knowledge.tags,
            created_at=knowledge.created_at
        )
        
        self.db.add(knowledge_record)
        await self.db.commit()
    
    async def semantic_search(self, query: str, user_id: str, top_k: int = 5) -> List[Memory]:
        """语义搜索相关记忆"""
        
        # 创建查询向量
        query_embedding = await self._create_embedding(query)
        
        # 向量搜索
        search_results = await self.vector_store.similarity_search(
            query_vector=query_embedding,
            top_k=top_k * 2,  # 获取更多候选
            filter_metadata={'user_id': user_id}
        )
        
        # 重排序 (考虑时间衰减、用户偏好等因素)
        ranked_results = await self._rerank_results(search_results, user_id, query)
        
        return ranked_results[:top_k]
    
    async def _analyze_behavior_patterns(self, user_data: UserData) -> BehaviorPatterns:
        """分析用户行为模式"""
        
        patterns = BehaviorPatterns()
        
        # 时间模式分析
        patterns.active_hours = self._analyze_active_hours(user_data.activity_log)
        patterns.session_duration = self._analyze_session_duration(user_data.sessions)
        
        # 交互模式分析  
        patterns.preferred_response_length = self._analyze_response_length_preference(user_data.interactions)
        patterns.communication_formality = self._analyze_formality_preference(user_data.messages)
        
        # 任务模式分析
        patterns.task_complexity_preference = self._analyze_task_complexity(user_data.tasks)
        patterns.tool_usage_patterns = self._analyze_tool_usage(user_data.tool_interactions)
        
        return patterns
    
    async def get_contextual_memories(self, conversation_id: str, current_context: str) -> List[Memory]:
        """获取上下文相关记忆"""
        
        # 组合查询：当前上下文 + 对话历史
        combined_query = f"{current_context} conversation:{conversation_id}"
        
        # 多维度搜索
        memories = []
        
        # 1. 语义相似性搜索
        semantic_memories = await self.semantic_search(combined_query, top_k=3)
        memories.extend(semantic_memories)
        
        # 2. 时间相关性搜索
        temporal_memories = await self._temporal_search(conversation_id, days=7)
        memories.extend(temporal_memories)
        
        # 3. 用户偏好相关搜索
        preference_memories = await self._preference_based_search(conversation_id)
        memories.extend(preference_memories)
        
        # 去重和排序
        unique_memories = self._deduplicate_memories(memories)
        sorted_memories = self._sort_by_relevance(unique_memories, current_context)
        
        return sorted_memories[:5]  # 返回最相关的5条记忆
```

---

## 🔄 记忆交互机制

### 1. 记忆层间转移

```python
class MemoryTransferManager:
    """记忆层间转移管理器"""
    
    async def short_to_medium_transfer(self, conversation_id: str):
        """短期记忆 -> 中期记忆转移"""
        
        # 获取短期记忆
        short_term = ShortTermMemory()
        messages = await short_term.get_context_window(conversation_id, -1)
        
        # 创建摘要
        medium_term = MediumTermMemory()
        summary = await medium_term.create_conversation_summary(messages)
        
        # 提取重要信息
        important_info = await medium_term.extract_important_info(messages)
        
        # 存储到中期记忆
        await medium_term.store_summary(conversation_id, summary)
        await medium_term.store_important_info(conversation_id, important_info)
        
        # 清理短期记忆中的旧数据
        await short_term.cleanup_old_messages(conversation_id, keep_recent=10)
    
    async def medium_to_long_transfer(self, user_id: str):
        """中期记忆 -> 长期记忆转移"""
        
        medium_term = MediumTermMemory()
        long_term = LongTermMemory()
        
        # 获取用户的中期记忆摘要
        summaries = await medium_term.get_user_summaries(user_id, days=30)
        
        # 分析模式和知识
        patterns = await self._extract_patterns_from_summaries(summaries)
        knowledge = await self._extract_knowledge_from_summaries(summaries)
        
        # 更新用户画像
        await long_term.update_user_profile(user_id, patterns)
        
        # 存储知识
        for item in knowledge:
            await long_term.store_knowledge(item)
        
        # 标记已处理的摘要
        await medium_term.mark_summaries_processed(summaries)
```

### 2. 记忆检索策略

```python
class MemoryRetrievalStrategy:
    """记忆检索策略"""
    
    async def retrieve_for_context(self, conversation_id: str, current_message: str) -> ContextMemory:
        """为当前对话检索相关记忆"""
        
        context_memory = ContextMemory()
        
        # 1. 获取短期记忆 (最近的对话)
        short_term = ShortTermMemory()
        recent_messages = await short_term.get_context_window(conversation_id, 10)
        context_memory.recent_context = recent_messages
        
        # 2. 获取中期记忆 (相关摘要)
        medium_term = MediumTermMemory()
        relevant_summaries = await medium_term.get_relevant_summaries(conversation_id, current_message)
        context_memory.conversation_summaries = relevant_summaries
        
        # 3. 获取长期记忆 (用户画像和相关知识)
        long_term = LongTermMemory()
        user_profile = await long_term.get_user_profile(conversation_id)
        relevant_knowledge = await long_term.semantic_search(current_message, user_profile.user_id)
        
        context_memory.user_profile = user_profile
        context_memory.relevant_knowledge = relevant_knowledge
        
        return context_memory
    
    async def retrieve_for_multi_user_context(self, conversation_id: str, participants: List[str]) -> MultiUserContextMemory:
        """多用户对话记忆检索"""
        
        multi_context = MultiUserContextMemory()
        
        # 获取共享短期记忆
        shared_short_term = await self._get_shared_short_term_memory(conversation_id)
        multi_context.shared_recent_context = shared_short_term
        
        # 获取每个参与者的个人上下文
        for user_id in participants:
            personal_context = await self._get_personal_context_for_group(user_id, conversation_id)
            multi_context.personal_contexts[user_id] = personal_context
        
        # 获取群组共享记忆
        group_memory = await self._get_group_shared_memory(conversation_id)
        multi_context.group_shared_memory = group_memory
        
        return multi_context
```

---

## 💾 数据模型设计

### 1. 短期记忆数据结构

```python
# Redis 数据结构
short_term_memory = {
    f"stm:{conversation_id}": [
        {
            "id": "msg_001",
            "content": "用户消息内容",
            "sender_id": "user_123",
            "sender_type": "user",  # user, agent
            "timestamp": "2024-01-15T10:30:00Z",
            "message_type": "text",
            "metadata": {
                "tokens": 150,
                "language": "zh",
                "sentiment": "neutral"
            }
        }
    ]
}

# 上下文状态
context_state = {
    f"ctx:{conversation_id}": {
        "current_topic": "项目讨论",
        "active_agents": ["agent_001", "agent_002"],
        "user_mood": "professional",
        "session_start": "2024-01-15T10:00:00Z",
        "turn_count": 15,
        "context_summary": "讨论项目进度和下一步计划"
    }
}
```

### 2. 中期记忆数据模型

```python
class ConversationSummaryModel(SQLModel, table=True):
    """对话摘要模型"""
    __tablename__ = "conversation_summaries"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")
    summary_text: str = Field(max_length=2000)
    key_points: List[str] = Field(default=[], sa_column=Column(JSON))
    entities: List[dict] = Field(default=[], sa_column=Column(JSON))
    sentiment: str = Field(default="neutral")
    topics: List[str] = Field(default=[], sa_column=Column(JSON))
    time_range_start: datetime
    time_range_end: datetime
    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ImportantInfoModel(SQLModel, table=True):
    """重要信息模型"""
    __tablename__ = "important_info"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")
    user_id: UUID = Field(foreign_key="users.id")
    info_type: str  # decision, task, preference, entity
    content: str
    confidence_score: float = Field(default=1.0)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    validated: bool = Field(default=False)
```

### 3. 长期记忆数据模型

```python
class UserProfileModel(SQLModel, table=True):
    """用户画像模型"""
    __tablename__ = "user_profiles"
    
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    behavior_patterns: dict = Field(sa_column=Column(JSON))
    preferences: dict = Field(sa_column=Column(JSON))
    interest_graph: dict = Field(sa_column=Column(JSON))
    communication_style: dict = Field(sa_column=Column(JSON))
    expertise_areas: List[str] = Field(default=[], sa_column=Column(JSON))
    personality_traits: dict = Field(sa_column=Column(JSON))
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeModel(SQLModel, table=True):
    """知识存储模型"""
    __tablename__ = "knowledge_store"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    content: str
    knowledge_type: str  # fact, procedure, concept, experience
    source: str  # conversation, document, web
    confidence: float = Field(default=1.0)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(1536)))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)
```

---

## 🔍 记忆搜索与匹配

### 1. 多维度匹配算法

```python
class MemoryMatcher:
    """记忆匹配器"""
    
    async def multi_dimensional_match(self, query: str, user_id: str) -> List[MatchedMemory]:
        """多维度记忆匹配"""
        
        matches = []
        
        # 1. 语义相似度匹配
        semantic_matches = await self._semantic_similarity_search(query, user_id)
        for match in semantic_matches:
            match.add_score('semantic', match.similarity_score)
            matches.append(match)
        
        # 2. 时间相关性匹配
        temporal_matches = await self._temporal_relevance_search(query, user_id)
        for match in temporal_matches:
            match.add_score('temporal', self._calculate_temporal_score(match))
            matches.append(match)
        
        # 3. 频率重要性匹配
        frequency_matches = await self._frequency_based_search(query, user_id)
        for match in frequency_matches:
            match.add_score('frequency', match.access_count / 100.0)
            matches.append(match)
        
        # 4. 用户偏好匹配
        preference_matches = await self._preference_based_search(query, user_id)
        for match in preference_matches:
            match.add_score('preference', self._calculate_preference_score(match, user_id))
            matches.append(match)
        
        # 去重和综合评分
        unique_matches = self._deduplicate_matches(matches)
        scored_matches = self._calculate_final_scores(unique_matches)
        
        return sorted(scored_matches, key=lambda x: x.final_score, reverse=True)
    
    def _calculate_final_scores(self, matches: List[MatchedMemory]) -> List[MatchedMemory]:
        """计算最终得分"""
        
        weights = {
            'semantic': 0.4,    # 语义相似度权重
            'temporal': 0.2,    # 时间相关性权重  
            'frequency': 0.2,   # 访问频率权重
            'preference': 0.2   # 用户偏好权重
        }
        
        for match in matches:
            final_score = 0.0
            for dimension, score in match.scores.items():
                final_score += weights.get(dimension, 0) * score
            
            match.final_score = final_score
        
        return matches
```

### 2. 智能记忆压缩

```python
class MemoryCompressor:
    """记忆压缩器"""
    
    async def compress_conversation_history(self, conversation_id: str) -> ConversationSummary:
        """压缩对话历史"""
        
        # 获取原始消息
        messages = await self._get_conversation_messages(conversation_id)
        
        # 分段处理长对话
        segments = self._segment_conversation(messages, max_tokens=2000)
        
        segment_summaries = []
        for segment in segments:
            summary = await self._summarize_segment(segment)
            segment_summaries.append(summary)
        
        # 合并段落摘要
        final_summary = await self._merge_summaries(segment_summaries)
        
        return final_summary
    
    async def _summarize_segment(self, messages: List[Message]) -> SegmentSummary:
        """总结对话段落"""
        
        prompt = f"""
        请总结以下对话段落，提取关键信息：
        
        对话内容：
        {self._format_messages(messages)}
        
        总结要求：
        1. 保留关键决策和结论
        2. 记录重要的实体和概念
        3. 提取用户偏好和意图
        4. 记录待办事项和后续行动
        5. 保持原意的同时尽可能简洁
        
        请以JSON格式返回总结结果。
        """
        
        llm_response = await self.llm_client.complete(prompt)
        summary_data = json.loads(llm_response.content)
        
        return SegmentSummary(
            key_points=summary_data['key_points'],
            entities=summary_data['entities'],
            decisions=summary_data['decisions'],
            tasks=summary_data['tasks'],
            user_preferences=summary_data['preferences']
        )
```

---

## ⚡ 性能优化策略

### 1. 缓存策略

```python
class MemoryCacheStrategy:
    """记忆缓存策略"""
    
    # 缓存配置
    CACHE_CONFIG = {
        'short_term_memory': {
            'ttl': 1800,     # 30分钟
            'max_size': 1000  # 最大条目数
        },
        'user_profiles': {
            'ttl': 3600,     # 1小时
            'max_size': 500
        },
        'conversation_summaries': {
            'ttl': 7200,     # 2小时
            'max_size': 2000
        },
        'knowledge_embeddings': {
            'ttl': 86400,    # 24小时
            'max_size': 10000
        }
    }
    
    async def cache_memory(self, memory_type: str, key: str, data: any):
        """缓存记忆数据"""
        
        config = self.CACHE_CONFIG.get(memory_type, {})
        ttl = config.get('ttl', 3600)
        
        cache_key = f"memory_cache:{memory_type}:{key}"
        await self.redis.setex(cache_key, ttl, json.dumps(data))
    
    async def get_cached_memory(self, memory_type: str, key: str) -> Optional[any]:
        """获取缓存的记忆数据"""
        
        cache_key = f"memory_cache:{memory_type}:{key}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        return None
```

### 2. 批处理优化

```python
class MemoryBatchProcessor:
    """记忆批处理器"""
    
    async def batch_process_memories(self, memories: List[Memory], operation: str):
        """批量处理记忆"""
        
        batch_size = 50
        batches = [memories[i:i + batch_size] for i in range(0, len(memories), batch_size)]
        
        tasks = []
        for batch in batches:
            if operation == 'embed':
                task = self._batch_embed_memories(batch)
            elif operation == 'store':
                task = self._batch_store_memories(batch)
            elif operation == 'compress':
                task = self._batch_compress_memories(batch)
            
            tasks.append(task)
        
        # 并发执行所有批次
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def _batch_embed_memories(self, memories: List[Memory]) -> List[EmbeddedMemory]:
        """批量生成记忆嵌入"""
        
        contents = [memory.content for memory in memories]
        
        # 批量调用嵌入模型
        embeddings = await self.embedding_client.embed_batch(contents)
        
        embedded_memories = []
        for memory, embedding in zip(memories, embeddings):
            embedded_memory = EmbeddedMemory(
                memory=memory,
                embedding=embedding,
                created_at=datetime.utcnow()
            )
            embedded_memories.append(embedded_memory)
        
        return embedded_memories
```

---

## 📈 记忆质量评估

### 1. 记忆质量指标

```python
class MemoryQualityAssessor:
    """记忆质量评估器"""
    
    QUALITY_METRICS = {
        'relevance': 0.3,      # 相关性
        'accuracy': 0.25,      # 准确性
        'completeness': 0.2,   # 完整性
        'freshness': 0.15,     # 新鲜度
        'consistency': 0.1     # 一致性
    }
    
    async def assess_memory_quality(self, memory: Memory, context: AssessmentContext) -> QualityScore:
        """评估记忆质量"""
        
        scores = {}
        
        # 相关性评分
        scores['relevance'] = await self._assess_relevance(memory, context)
        
        # 准确性评分 (通过交叉验证)
        scores['accuracy'] = await self._assess_accuracy(memory, context)
        
        # 完整性评分
        scores['completeness'] = await self._assess_completeness(memory, context)
        
        # 新鲜度评分 (基于时间衰减)
        scores['freshness'] = await self._assess_freshness(memory)
        
        # 一致性评分 (与其他记忆的一致性)
        scores['consistency'] = await self._assess_consistency(memory, context)
        
        # 计算综合质量分数
        total_score = sum(
            scores[metric] * weight 
            for metric, weight in self.QUALITY_METRICS.items()
        )
        
        return QualityScore(
            total_score=total_score,
            metric_scores=scores,
            assessment_time=datetime.utcnow()
        )
    
    async def clean_low_quality_memories(self, threshold: float = 0.3):
        """清理低质量记忆"""
        
        # 获取所有记忆的质量评分
        all_memories = await self._get_all_memories()
        
        memories_to_clean = []
        for memory in all_memories:
            quality_score = await self.assess_memory_quality(memory, None)
            if quality_score.total_score < threshold:
                memories_to_clean.append(memory)
        
        # 批量清理
        if memories_to_clean:
            await self._batch_delete_memories(memories_to_clean)
            
            # 记录清理日志
            await self._log_memory_cleanup(len(memories_to_clean), threshold)
```

---

## 🔒 隐私与安全

### 1. 记忆加密存储

```python
class MemoryEncryption:
    """记忆加密处理"""
    
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)
    
    async def encrypt_sensitive_memory(self, memory: Memory) -> EncryptedMemory:
        """加密敏感记忆"""
        
        # 检查敏感内容
        if await self._contains_sensitive_info(memory.content):
            encrypted_content = self.fernet.encrypt(memory.content.encode())
            
            return EncryptedMemory(
                id=memory.id,
                encrypted_content=encrypted_content,
                encryption_method="fernet",
                is_encrypted=True,
                created_at=memory.created_at
            )
        
        return memory
    
    async def decrypt_memory(self, encrypted_memory: EncryptedMemory) -> Memory:
        """解密记忆"""
        
        if encrypted_memory.is_encrypted:
            decrypted_content = self.fernet.decrypt(encrypted_memory.encrypted_content).decode()
            
            return Memory(
                id=encrypted_memory.id,
                content=decrypted_content,
                created_at=encrypted_memory.created_at
            )
        
        return encrypted_memory
    
    async def _contains_sensitive_info(self, content: str) -> bool:
        """检测敏感信息"""
        
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',      # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # 信用卡号
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
            r'\b\d{3}-\d{3}-\d{4}\b'       # 电话号码
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                return True
        
        return False
```

这个记忆管理系统设计提供了完整的三层记忆架构，支持智能检索、质量评估和隐私保护，确保 AI 系统能够在不同时间尺度上保持上下文连贯性和个性化体验。