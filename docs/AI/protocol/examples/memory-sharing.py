#!/usr/bin/env python3
"""
记忆共享示例 (Memory Sharing Example)

本示例展示了多智能体系统中的记忆共享机制，包括：
1. 分层记忆管理
2. 访问控制和权限验证
3. 记忆推荐和相关性计算
4. 版本控制和冲突解决
5. 知识图谱构建

功能演示:
- 创建和存储不同类型的记忆
- 基于权限的记忆访问控制
- 记忆相关性搜索和推荐
- 协作记忆的版本管理
- 集体知识的提取和共享
"""

import asyncio
import json
import uuid
import hashlib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random

# 记忆相关的数据结构定义
class MemoryType(Enum):
    EPISODIC = "episodic"        # 情景记忆
    SEMANTIC = "semantic"        # 语义记忆  
    PROCEDURAL = "procedural"    # 程序记忆
    WORKING = "working"          # 工作记忆
    LONG_TERM = "long_term"      # 长期记忆

class AccessLevel(Enum):
    PRIVATE = "private"          # 私有访问
    GROUP = "group"             # 群组访问
    PUBLIC = "public"           # 公共访问
    RESTRICTED = "restricted"    # 受限访问

class MemoryQuality(Enum):
    HIGH = "high"               # 高质量
    MEDIUM = "medium"           # 中等质量
    LOW = "low"                # 低质量
    UNVERIFIED = "unverified"  # 未验证

@dataclass
class MemoryObject:
    """记忆对象"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    title: str = ""
    description: str = ""
    memory_type: MemoryType = MemoryType.SEMANTIC
    
    # 创建信息
    creator_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    
    # 访问控制
    access_level: AccessLevel = AccessLevel.PRIVATE
    owner_id: str = ""
    authorized_agents: Set[str] = field(default_factory=set)
    authorized_groups: Set[str] = field(default_factory=set)
    
    # 内容结构
    tags: Set[str] = field(default_factory=set)
    keywords: Set[str] = field(default_factory=set)
    entities: List[str] = field(default_factory=list)
    
    # 质量和信任度
    quality: MemoryQuality = MemoryQuality.UNVERIFIED
    confidence_score: float = 0.5
    verification_count: int = 0
    trust_score: float = 0.5
    
    # 使用统计
    access_count: int = 0
    reference_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # 版本控制
    version: str = "1.0.0"
    previous_versions: List[str] = field(default_factory=list)
    
    # 关联关系
    related_memories: Set[str] = field(default_factory=set)
    derived_from: Optional[str] = None
    
    # 向量嵌入 (简化表示)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "description": self.description,
            "memory_type": self.memory_type.value,
            "creator_id": self.creator_id,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "access_level": self.access_level.value,
            "owner_id": self.owner_id,
            "authorized_agents": list(self.authorized_agents),
            "authorized_groups": list(self.authorized_groups),
            "tags": list(self.tags),
            "keywords": list(self.keywords),
            "entities": self.entities,
            "quality": self.quality.value,
            "confidence_score": self.confidence_score,
            "verification_count": self.verification_count,
            "trust_score": self.trust_score,
            "access_count": self.access_count,
            "reference_count": self.reference_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "version": self.version,
            "previous_versions": self.previous_versions,
            "related_memories": list(self.related_memories),
            "derived_from": self.derived_from
        }

@dataclass
class AccessRequest:
    """访问请求"""
    requester_id: str
    memory_id: str
    access_type: str  # read, write, reference
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
class AccessResult:
    """访问结果"""
    def __init__(self, allowed: bool, reason: str = "", filtered_content: str = ""):
        self.allowed = allowed
        self.reason = reason
        self.filtered_content = filtered_content

@dataclass
class MemoryRecommendation:
    """记忆推荐"""
    memory: MemoryObject
    relevance_score: float
    recommendation_reason: str
    confidence: float

class SimpleEmbeddingGenerator:
    """简单的嵌入生成器 (用于演示)"""
    
    @staticmethod
    def generate_embedding(text: str, dimension: int = 100) -> List[float]:
        """生成文本的简单嵌入向量"""
        # 使用文本哈希来生成一致的向量
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # 将哈希转换为数字种子
        seed = int(text_hash[:8], 16)
        random.seed(seed)
        
        # 生成归一化向量
        vector = [random.gauss(0, 1) for _ in range(dimension)]
        magnitude = math.sqrt(sum(x*x for x in vector))
        
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

class AdvancedMemoryManager:
    """高级记忆管理器"""
    
    def __init__(self):
        self.memories: Dict[str, MemoryObject] = {}
        self.access_log: List[Dict[str, Any]] = []
        self.agent_groups: Dict[str, Set[str]] = {}  # group_id -> agent_ids
        self.knowledge_graph: Dict[str, List[str]] = {}  # entity -> related_memories
        self.embedding_generator = SimpleEmbeddingGenerator()
    
    def create_group(self, group_id: str, member_agents: List[str]):
        """创建智能体群组"""
        self.agent_groups[group_id] = set(member_agents)
        print(f"👥 创建群组: {group_id} (成员: {len(member_agents)})")
    
    async def store_memory(self, memory: MemoryObject) -> bool:
        """存储记忆"""
        try:
            # 生成嵌入向量
            if not memory.embedding:
                memory.embedding = self.embedding_generator.generate_embedding(
                    memory.content + " " + memory.title
                )
            
            # 提取关键词和实体 (简化实现)
            if not memory.keywords:
                memory.keywords = set(self._extract_keywords(memory.content))
            
            if not memory.entities:
                memory.entities = self._extract_entities(memory.content)
            
            # 存储记忆
            self.memories[memory.id] = memory
            
            # 更新知识图谱
            await self._update_knowledge_graph(memory)
            
            print(f"🧠 记忆已存储: {memory.id}")
            print(f"   标题: {memory.title}")
            print(f"   类型: {memory.memory_type.value}")
            print(f"   访问级别: {memory.access_level.value}")
            print(f"   关键词: {list(memory.keywords)[:5]}...")
            
            return True
        except Exception as e:
            print(f"❌ 记忆存储失败: {e}")
            return False
    
    async def retrieve_memory(self, request: AccessRequest) -> Tuple[Optional[MemoryObject], AccessResult]:
        """检索记忆"""
        if request.memory_id not in self.memories:
            return None, AccessResult(False, "记忆不存在")
        
        memory = self.memories[request.memory_id]
        
        # 访问权限检查
        access_result = await self._check_access_permission(request, memory)
        
        if not access_result.allowed:
            await self._log_access_attempt(request, False, access_result.reason)
            return None, access_result
        
        # 更新访问统计
        memory.access_count += 1
        memory.last_accessed = datetime.utcnow()
        
        # 记录访问日志
        await self._log_access_attempt(request, True, "访问成功")
        
        print(f"🔍 记忆检索成功: {memory.id}")
        print(f"   请求者: {request.requester_id}")
        print(f"   访问类型: {request.access_type}")
        
        return memory, access_result
    
    async def _check_access_permission(self, request: AccessRequest, 
                                     memory: MemoryObject) -> AccessResult:
        """检查访问权限"""
        requester_id = request.requester_id
        
        # 所有者总是有访问权限
        if memory.owner_id == requester_id:
            return AccessResult(True, "所有者访问")
        
        # 检查访问级别
        if memory.access_level == AccessLevel.PRIVATE:
            return AccessResult(False, "私有记忆，拒绝访问")
        elif memory.access_level == AccessLevel.PUBLIC:
            return AccessResult(True, "公共访问")
        elif memory.access_level == AccessLevel.GROUP:
            # 检查直接授权
            if requester_id in memory.authorized_agents:
                return AccessResult(True, "直接授权访问")
            
            # 检查群组授权
            for group_id in memory.authorized_groups:
                if group_id in self.agent_groups:
                    if requester_id in self.agent_groups[group_id]:
                        return AccessResult(True, f"群组授权访问: {group_id}")
            
            return AccessResult(False, "无群组访问权限")
        elif memory.access_level == AccessLevel.RESTRICTED:
            # 受限访问需要额外验证
            return await self._check_restricted_access(request, memory)
        
        return AccessResult(False, "未知访问级别")
    
    async def _check_restricted_access(self, request: AccessRequest, 
                                     memory: MemoryObject) -> AccessResult:
        """检查受限访问权限"""
        # 简化的受限访问检查
        requester_id = request.requester_id
        
        # 检查信任度
        if memory.trust_score < 0.7:
            return AccessResult(False, "记忆信任度不足")
        
        # 检查请求者在授权列表中
        if requester_id not in memory.authorized_agents:
            return AccessResult(False, "未授权的受限访问")
        
        # 过滤敏感内容
        filtered_content = self._filter_sensitive_content(memory.content)
        
        return AccessResult(True, "受限访问已过滤", filtered_content)
    
    def _filter_sensitive_content(self, content: str) -> str:
        """过滤敏感内容 (简化实现)"""
        # 简单的敏感内容过滤
        sensitive_patterns = ["密码", "密钥", "机密", "保密"]
        filtered_content = content
        
        for pattern in sensitive_patterns:
            filtered_content = filtered_content.replace(pattern, "[已过滤]")
        
        return filtered_content
    
    async def _log_access_attempt(self, request: AccessRequest, 
                                success: bool, reason: str):
        """记录访问尝试"""
        log_entry = {
            "requester_id": request.requester_id,
            "memory_id": request.memory_id,
            "access_type": request.access_type,
            "success": success,
            "reason": reason,
            "timestamp": request.timestamp.isoformat()
        }
        
        self.access_log.append(log_entry)
    
    async def recommend_memories(self, agent_id: str, query: str, 
                               limit: int = 5) -> List[MemoryRecommendation]:
        """推荐相关记忆"""
        print(f"🔍 为 {agent_id} 推荐记忆，查询: '{query}'")
        
        # 生成查询嵌入
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        recommendations = []
        
        for memory in self.memories.values():
            # 检查访问权限
            access_request = AccessRequest(agent_id, memory.id, "read")
            access_result = await self._check_access_permission(access_request, memory)
            
            if not access_result.allowed:
                continue
            
            # 计算相关性分数
            relevance_score = self._calculate_relevance_score(
                query, query_embedding, memory
            )
            
            if relevance_score > 0.1:  # 阈值过滤
                recommendation = MemoryRecommendation(
                    memory=memory,
                    relevance_score=relevance_score,
                    recommendation_reason=self._generate_recommendation_reason(
                        query, memory, relevance_score
                    ),
                    confidence=min(relevance_score * memory.trust_score, 1.0)
                )
                recommendations.append(recommendation)
        
        # 按相关性排序
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        top_recommendations = recommendations[:limit]
        
        print(f"📋 推荐结果: {len(top_recommendations)} 条记忆")
        for i, rec in enumerate(top_recommendations, 1):
            print(f"   {i}. {rec.memory.title} (相关性: {rec.relevance_score:.3f})")
        
        return top_recommendations
    
    def _calculate_relevance_score(self, query: str, query_embedding: List[float], 
                                 memory: MemoryObject) -> float:
        """计算相关性分数"""
        score = 0.0
        
        # 嵌入相似度 (权重: 0.4)
        if memory.embedding:
            semantic_similarity = self.embedding_generator.cosine_similarity(
                query_embedding, memory.embedding
            )
            score += semantic_similarity * 0.4
        
        # 关键词匹配 (权重: 0.3)
        query_words = set(query.lower().split())
        memory_keywords = {kw.lower() for kw in memory.keywords}
        keyword_overlap = len(query_words.intersection(memory_keywords))
        keyword_score = keyword_overlap / max(len(query_words), 1)
        score += keyword_score * 0.3
        
        # 内容直接匹配 (权重: 0.2)
        content_match = 1.0 if query.lower() in memory.content.lower() else 0.0
        score += content_match * 0.2
        
        # 质量和信任度加权 (权重: 0.1)
        quality_weight = {
            MemoryQuality.HIGH: 1.0,
            MemoryQuality.MEDIUM: 0.8,
            MemoryQuality.LOW: 0.6,
            MemoryQuality.UNVERIFIED: 0.4
        }.get(memory.quality, 0.4)
        
        quality_score = memory.trust_score * quality_weight
        score += quality_score * 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendation_reason(self, query: str, memory: MemoryObject, 
                                      relevance_score: float) -> str:
        """生成推荐理由"""
        reasons = []
        
        # 检查关键词匹配
        query_words = set(query.lower().split())
        memory_keywords = {kw.lower() for kw in memory.keywords}
        matches = query_words.intersection(memory_keywords)
        
        if matches:
            reasons.append(f"关键词匹配: {', '.join(list(matches)[:3])}")
        
        # 检查内容匹配
        if query.lower() in memory.content.lower():
            reasons.append("内容直接匹配")
        
        # 检查质量
        if memory.quality == MemoryQuality.HIGH:
            reasons.append("高质量记忆")
        
        # 检查新近性
        if memory.created_at > datetime.utcnow() - timedelta(days=7):
            reasons.append("最近创建")
        
        if not reasons:
            reasons.append("语义相似性匹配")
        
        return "; ".join(reasons)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词 (简化实现)"""
        # 简单的关键词提取
        words = content.lower().split()
        # 过滤停用词
        stop_words = {"的", "是", "在", "了", "和", "与", "或", "但", "然而", "因此", "所以"}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 返回最常见的关键词
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]
    
    def _extract_entities(self, content: str) -> List[str]:
        """提取实体 (简化实现)"""
        # 简单的实体提取 - 查找大写开头的词
        words = content.split()
        entities = []
        
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word.strip('.,!?;:'))
        
        return list(set(entities))
    
    async def _update_knowledge_graph(self, memory: MemoryObject):
        """更新知识图谱"""
        for entity in memory.entities:
            if entity not in self.knowledge_graph:
                self.knowledge_graph[entity] = []
            
            if memory.id not in self.knowledge_graph[entity]:
                self.knowledge_graph[entity].append(memory.id)
    
    async def create_memory_version(self, memory_id: str, changes: Dict[str, Any], 
                                  changed_by: str, change_reason: str) -> bool:
        """创建记忆版本"""
        if memory_id not in self.memories:
            print(f"❌ 记忆不存在: {memory_id}")
            return False
        
        memory = self.memories[memory_id]
        
        # 保存当前版本
        memory.previous_versions.append(memory.version)
        
        # 生成新版本号
        version_parts = memory.version.split('.')
        minor_version = int(version_parts[1]) + 1
        memory.version = f"{version_parts[0]}.{minor_version}.{version_parts[2]}"
        
        # 应用变更
        for field, value in changes.items():
            if hasattr(memory, field):
                setattr(memory, field, value)
        
        # 重新生成嵌入（如果内容改变）
        if 'content' in changes or 'title' in changes:
            memory.embedding = self.embedding_generator.generate_embedding(
                memory.content + " " + memory.title
            )
        
        print(f"📝 记忆版本已更新: {memory_id} -> {memory.version}")
        print(f"   变更者: {changed_by}")
        print(f"   变更原因: {change_reason}")
        
        return True
    
    async def find_related_memories(self, memory_id: str, max_results: int = 5) -> List[MemoryObject]:
        """查找相关记忆"""
        if memory_id not in self.memories:
            return []
        
        source_memory = self.memories[memory_id]
        related_memories = []
        
        for candidate_id, candidate_memory in self.memories.items():
            if candidate_id == memory_id:
                continue
            
            # 计算相关性
            similarity_score = 0.0
            
            # 嵌入相似度
            if source_memory.embedding and candidate_memory.embedding:
                similarity_score += self.embedding_generator.cosine_similarity(
                    source_memory.embedding, candidate_memory.embedding
                ) * 0.5
            
            # 标签重叠
            tag_overlap = len(source_memory.tags.intersection(candidate_memory.tags))
            tag_score = tag_overlap / max(len(source_memory.tags.union(candidate_memory.tags)), 1)
            similarity_score += tag_score * 0.3
            
            # 实体重叠
            entity_overlap = len(set(source_memory.entities).intersection(set(candidate_memory.entities)))
            entity_score = entity_overlap / max(len(set(source_memory.entities).union(set(candidate_memory.entities))), 1)
            similarity_score += entity_score * 0.2
            
            if similarity_score > 0.3:  # 相关性阈值
                related_memories.append((candidate_memory, similarity_score))
        
        # 排序并返回
        related_memories.sort(key=lambda x: x[1], reverse=True)
        
        return [memory for memory, _ in related_memories[:max_results]]
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        stats = {
            "total_memories": len(self.memories),
            "memory_types": {},
            "access_levels": {},
            "quality_distribution": {},
            "total_accesses": sum(m.access_count for m in self.memories.values()),
            "average_trust_score": sum(m.trust_score for m in self.memories.values()) / len(self.memories) if self.memories else 0,
            "access_log_entries": len(self.access_log),
            "knowledge_graph_entities": len(self.knowledge_graph)
        }
        
        # 统计内存类型分布
        for memory in self.memories.values():
            memory_type = memory.memory_type.value
            stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1
            
            access_level = memory.access_level.value
            stats["access_levels"][access_level] = stats["access_levels"].get(access_level, 0) + 1
            
            quality = memory.quality.value
            stats["quality_distribution"][quality] = stats["quality_distribution"].get(quality, 0) + 1
        
        return stats

class MemoryAgent:
    """具有记忆能力的智能体"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.memory_manager: Optional[AdvancedMemoryManager] = None
    
    def connect_memory_manager(self, memory_manager: AdvancedMemoryManager):
        """连接记忆管理器"""
        self.memory_manager = memory_manager
        print(f"🔗 {self.name} 已连接到记忆管理器")
    
    async def create_memory(self, title: str, content: str, memory_type: MemoryType,
                          access_level: AccessLevel, tags: List[str] = None) -> str:
        """创建记忆"""
        if not self.memory_manager:
            print(f"❌ {self.name}: 记忆管理器未连接")
            return ""
        
        memory = MemoryObject(
            title=title,
            content=content,
            memory_type=memory_type,
            creator_id=self.agent_id,
            owner_id=self.agent_id,
            access_level=access_level,
            tags=set(tags) if tags else set(),
            quality=MemoryQuality.MEDIUM,
            trust_score=0.8
        )
        
        success = await self.memory_manager.store_memory(memory)
        
        if success:
            print(f"✅ {self.name} 创建记忆: {title}")
            return memory.id
        else:
            print(f"❌ {self.name} 记忆创建失败")
            return ""
    
    async def access_memory(self, memory_id: str, access_type: str = "read") -> Optional[MemoryObject]:
        """访问记忆"""
        if not self.memory_manager:
            return None
        
        request = AccessRequest(
            requester_id=self.agent_id,
            memory_id=memory_id,
            access_type=access_type
        )
        
        memory, access_result = await self.memory_manager.retrieve_memory(request)
        
        if access_result.allowed:
            print(f"📖 {self.name} 成功访问记忆: {memory_id}")
            return memory
        else:
            print(f"🚫 {self.name} 访问记忆被拒绝: {access_result.reason}")
            return None
    
    async def search_memories(self, query: str) -> List[MemoryRecommendation]:
        """搜索相关记忆"""
        if not self.memory_manager:
            return []
        
        recommendations = await self.memory_manager.recommend_memories(
            self.agent_id, query
        )
        
        print(f"🔍 {self.name} 搜索记忆: '{query}' -> {len(recommendations)} 条结果")
        
        return recommendations
    
    async def share_memory_with_agent(self, memory_id: str, target_agent_id: str):
        """与其他智能体分享记忆"""
        if not self.memory_manager:
            return
        
        if memory_id not in self.memory_manager.memories:
            print(f"❌ {self.name}: 记忆不存在 {memory_id}")
            return
        
        memory = self.memory_manager.memories[memory_id]
        
        # 检查是否为所有者
        if memory.owner_id != self.agent_id:
            print(f"🚫 {self.name}: 无权分享记忆 {memory_id}")
            return
        
        # 添加到授权列表
        memory.authorized_agents.add(target_agent_id)
        
        print(f"🤝 {self.name} 与 {target_agent_id} 分享记忆: {memory.title}")
    
    async def collaborate_on_memory(self, memory_id: str, contribution: str):
        """协作编辑记忆"""
        if not self.memory_manager:
            return
        
        # 首先访问记忆
        memory = await self.access_memory(memory_id, "write")
        
        if not memory:
            return
        
        # 更新记忆内容
        updated_content = memory.content + f"\n\n[{self.name} 的贡献 - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]\n{contribution}"
        
        changes = {
            "content": updated_content,
            "verification_count": memory.verification_count + 1
        }
        
        await self.memory_manager.create_memory_version(
            memory_id, changes, self.agent_id, f"协作贡献: {contribution[:50]}..."
        )
        
        print(f"🤝 {self.name} 对记忆进行协作编辑: {memory.title}")

async def demo_memory_sharing():
    """记忆共享演示"""
    print("=" * 70)
    print("🧠 多智能体协作协议 - 记忆共享演示")
    print("=" * 70)
    
    # 创建记忆管理器
    memory_manager = AdvancedMemoryManager()
    
    # 创建智能体
    alice = MemoryAgent("alice_001", "Alice (研究员)")
    bob = MemoryAgent("bob_001", "Bob (分析师)")
    charlie = MemoryAgent("charlie_001", "Charlie (工程师)")
    
    # 连接记忆管理器
    alice.connect_memory_manager(memory_manager)
    bob.connect_memory_manager(memory_manager)
    charlie.connect_memory_manager(memory_manager)
    
    # 创建群组
    memory_manager.create_group("research_team", ["alice_001", "bob_001"])
    memory_manager.create_group("dev_team", ["bob_001", "charlie_001"])
    
    print("\n" + "="*70)
    print("📝 阶段 1: 创建和存储记忆")
    print("="*70)
    
    # Alice 创建研究记忆
    research_memory_id = await alice.create_memory(
        title="多智能体协作效果研究",
        content="根据最新研究，多智能体系统在处理复杂任务时比单智能体系统效率提升40%。"
               "主要优势包括：1) 并行处理能力 2) 专业分工 3) 集体智慧 4) 容错能力。"
               "研究还发现，记忆共享机制能显著提升协作效果。",
        memory_type=MemoryType.SEMANTIC,
        access_level=AccessLevel.GROUP,
        tags=["研究", "多智能体", "协作", "效率"]
    )
    
    # 将研究记忆授权给研究团队
    if research_memory_id:
        memory_manager.memories[research_memory_id].authorized_groups.add("research_team")
    
    # Bob 创建分析记忆
    analysis_memory_id = await bob.create_memory(
        title="用户行为模式分析",
        content="通过对1000个用户的行为数据分析发现：用户在使用多智能体系统时，"
               "平均任务完成时间减少35%，满意度提升45%。关键发现：智能体间的协作"
               "越紧密，用户体验越好。建议优化智能体通信协议。",
        memory_type=MemoryType.EPISODIC,
        access_level=AccessLevel.PUBLIC,
        tags=["分析", "用户行为", "性能", "体验"]
    )
    
    # Charlie 创建技术记忆
    tech_memory_id = await charlie.create_memory(
        title="分布式协议实现方案",
        content="基于JSON-RPC 2.0实现的多智能体通信协议具有以下特点：" 
               "1) 标准化接口 2) 可扩展性强 3) 错误处理完善。实现时需要注意："
               "消息路由、负载均衡、故障恢复。推荐使用Redis作为消息队列。",
        memory_type=MemoryType.PROCEDURAL,
        access_level=AccessLevel.RESTRICTED,
        tags=["技术", "协议", "实现", "分布式"]
    )
    
    # 将技术记忆授权给开发团队
    if tech_memory_id:
        memory_manager.memories[tech_memory_id].authorized_agents.add("bob_001")
        memory_manager.memories[tech_memory_id].authorized_groups.add("dev_team")
    
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("🔍 阶段 2: 记忆搜索和推荐")
    print("="*70)
    
    # Bob 搜索相关记忆
    bob_recommendations = await bob.search_memories("多智能体协作效果")
    
    # Charlie 搜索技术相关记忆
    charlie_recommendations = await charlie.search_memories("协议实现")
    
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("🚫 阶段 3: 访问控制演示")
    print("="*70)
    
    # Charlie 尝试访问 Alice 的研究记忆（应该被拒绝，因为不在研究团队）
    print(f"🧪 测试: Charlie 尝试访问 Alice 的研究记忆...")
    restricted_memory = await charlie.access_memory(research_memory_id)
    
    # Bob 访问 Alice 的研究记忆（应该成功，因为在研究团队）
    print(f"🧪 测试: Bob 尝试访问 Alice 的研究记忆...")
    accessible_memory = await bob.access_memory(research_memory_id)
    
    # Alice 尝试访问 Charlie 的技术记忆（应该被拒绝，因为是受限访问）
    print(f"🧪 测试: Alice 尝试访问 Charlie 的技术记忆...")
    restricted_tech_memory = await alice.access_memory(tech_memory_id)
    
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("🤝 阶段 4: 记忆分享和协作")
    print("="*70)
    
    # Alice 与 Charlie 分享研究记忆
    await alice.share_memory_with_agent(research_memory_id, "charlie_001")
    
    # 现在 Charlie 应该能访问这个记忆
    print(f"🧪 测试: Charlie 再次尝试访问 Alice 的研究记忆...")
    shared_memory = await charlie.access_memory(research_memory_id)
    
    # Bob 对 Alice 的研究记忆进行协作编辑
    await bob.collaborate_on_memory(
        research_memory_id,
        "补充数据分析结果：通过A/B测试验证，多智能体协作在处理复杂查询时，"
        "准确率提升25%，响应时间减少30%。建议进一步优化智能体间的任务分配算法。"
    )
    
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("🔗 阶段 5: 关联记忆发现")
    print("="*70)
    
    # 查找与研究记忆相关的其他记忆
    if research_memory_id:
        related_memories = await memory_manager.find_related_memories(research_memory_id)
        print(f"🔍 找到 {len(related_memories)} 条与研究记忆相关的记忆:")
        for memory in related_memories:
            print(f"   - {memory.title} (创建者: {memory.creator_id})")
    
    await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("📊 阶段 6: 系统统计信息")
    print("="*70)
    
    # 获取记忆系统统计信息
    stats = await memory_manager.get_memory_statistics()
    
    print(f"📈 记忆系统统计:")
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   总访问次数: {stats['total_accesses']}")
    print(f"   平均信任度: {stats['average_trust_score']:.3f}")
    print(f"   访问日志条目: {stats['access_log_entries']}")
    print(f"   知识图谱实体: {stats['knowledge_graph_entities']}")
    
    print(f"\n📋 记忆类型分布:")
    for mem_type, count in stats['memory_types'].items():
        print(f"   {mem_type}: {count}")
    
    print(f"\n🔒 访问级别分布:")
    for access_level, count in stats['access_levels'].items():
        print(f"   {access_level}: {count}")
    
    print(f"\n⭐ 质量分布:")
    for quality, count in stats['quality_distribution'].items():
        print(f"   {quality}: {count}")
    
    print("\n" + "="*70)
    print("🎊 记忆共享演示完成!")
    print("="*70)
    
    print(f"\n💡 演示要点总结:")
    print(f"✅ 分层记忆管理: 支持不同类型和访问级别的记忆")
    print(f"✅ 智能推荐系统: 基于语义相似度和关键词匹配")
    print(f"✅ 访问控制: 支持私有、群组、公共和受限访问")
    print(f"✅ 协作编辑: 支持多智能体协作更新记忆")
    print(f"✅ 版本管理: 自动跟踪记忆的版本变化")
    print(f"✅ 关联发现: 自动发现相关记忆和知识图谱")

if __name__ == "__main__":
    # 运行记忆共享演示
    asyncio.run(demo_memory_sharing())
