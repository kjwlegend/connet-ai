# 数据结构定义 (Data Structures)

## 🎯 概览

本文档定义了多智能体协作协议中使用的所有核心数据结构，包括智能体描述、消息格式、任务对象、记忆结构等。所有数据结构都使用 JSON Schema 进行规范化定义，确保跨平台兼容性和类型安全。

## 🤖 智能体相关数据结构

### 1. 智能体描述符 (Agent Descriptor)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Descriptor",
  "type": "object",
  "required": ["agent_id", "name", "capabilities", "endpoints"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]+$",
      "description": "智能体唯一标识符"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "智能体显示名称"
    },
    "description": {
      "type": "string",
      "maxLength": 500,
      "description": "智能体功能描述"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "版本号 (语义化版本)"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "最后更新时间"
    },
    "capabilities": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/AgentCapability"
      },
      "description": "智能体能力列表"
    },
    "personality": {
      "$ref": "#/definitions/PersonalityProfile",
      "description": "人格档案"
    },
    "expertise": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "专业领域"
    },
    "endpoints": {
      "$ref": "#/definitions/AgentEndpoints",
      "description": "通信端点"
    },
    "authentication": {
      "$ref": "#/definitions/AuthenticationConfig",
      "description": "认证配置"
    },
    "resource_limits": {
      "$ref": "#/definitions/ResourceLimits",
      "description": "资源限制"
    },
    "reputation": {
      "$ref": "#/definitions/ReputationScore",
      "description": "声誉分数"
    },
    "current_status": {
      "type": "string",
      "enum": ["online", "offline", "busy", "maintenance"],
      "description": "当前状态"
    },
    "load_metrics": {
      "$ref": "#/definitions/LoadMetrics",
      "description": "负载指标"
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  },
  "definitions": {
    "AgentCapability": {
      "type": "object",
      "required": ["name", "type"],
      "properties": {
        "name": {
          "type": "string",
          "description": "能力名称"
        },
        "type": {
          "type": "string",
          "enum": [
            "computation",
            "communication",
            "knowledge",
            "tool_usage",
            "reasoning"
          ],
          "description": "能力类型"
        },
        "description": {
          "type": "string",
          "description": "能力描述"
        },
        "proficiency_level": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "熟练程度 (0-1)"
        },
        "supported_formats": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "支持的数据格式"
        },
        "dependencies": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "依赖的其他能力"
        }
      }
    },
    "PersonalityProfile": {
      "type": "object",
      "properties": {
        "role": {
          "type": "string",
          "description": "角色定义"
        },
        "communication_style": {
          "type": "string",
          "enum": [
            "formal",
            "casual",
            "professional",
            "friendly",
            "analytical"
          ],
          "description": "沟通风格"
        },
        "creativity_level": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "创造力水平"
        },
        "empathy_level": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "共情能力"
        },
        "assertiveness": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "主张性"
        },
        "risk_tolerance": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "风险承受度"
        },
        "cooperation_tendency": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "合作倾向"
        }
      }
    },
    "AgentEndpoints": {
      "type": "object",
      "required": ["base_url"],
      "properties": {
        "base_url": {
          "type": "string",
          "format": "uri",
          "description": "基础URL"
        },
        "communication": {
          "type": "string",
          "format": "uri",
          "description": "通信端点"
        },
        "task_submission": {
          "type": "string",
          "format": "uri",
          "description": "任务提交端点"
        },
        "status_update": {
          "type": "string",
          "format": "uri",
          "description": "状态更新端点"
        },
        "memory_access": {
          "type": "string",
          "format": "uri",
          "description": "记忆访问端点"
        },
        "health_check": {
          "type": "string",
          "format": "uri",
          "description": "健康检查端点"
        }
      }
    },
    "AuthenticationConfig": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["oauth2", "api_key", "certificate", "jwt"],
          "description": "认证类型"
        },
        "token_endpoint": {
          "type": "string",
          "format": "uri",
          "description": "令牌端点"
        },
        "public_key": {
          "type": "string",
          "description": "公钥"
        },
        "certificate_chain": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "证书链"
        },
        "scopes": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "权限范围"
        }
      }
    },
    "ResourceLimits": {
      "type": "object",
      "properties": {
        "max_concurrent_tasks": {
          "type": "integer",
          "minimum": 1,
          "description": "最大并发任务数"
        },
        "max_memory_usage": {
          "type": "integer",
          "description": "最大内存使用量 (MB)"
        },
        "max_cpu_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "最大CPU使用率"
        },
        "rate_limit": {
          "type": "object",
          "properties": {
            "requests_per_minute": {
              "type": "integer",
              "minimum": 1
            },
            "burst_size": {
              "type": "integer",
              "minimum": 1
            }
          }
        }
      }
    },
    "ReputationScore": {
      "type": "object",
      "properties": {
        "overall_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "总体声誉分数"
        },
        "reliability": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "可靠性"
        },
        "quality": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "质量"
        },
        "cooperation": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "合作度"
        },
        "innovation": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "创新性"
        },
        "update_count": {
          "type": "integer",
          "minimum": 0,
          "description": "更新次数"
        },
        "last_updated": {
          "type": "string",
          "format": "date-time",
          "description": "最后更新时间"
        }
      }
    },
    "LoadMetrics": {
      "type": "object",
      "properties": {
        "cpu_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "CPU使用率"
        },
        "memory_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "内存使用率"
        },
        "active_tasks": {
          "type": "integer",
          "minimum": 0,
          "description": "活跃任务数"
        },
        "queue_length": {
          "type": "integer",
          "minimum": 0,
          "description": "队列长度"
        },
        "average_response_time": {
          "type": "number",
          "minimum": 0,
          "description": "平均响应时间 (ms)"
        },
        "last_activity": {
          "type": "string",
          "format": "date-time",
          "description": "最后活动时间"
        }
      }
    }
  }
}
```

### 2. 智能体状态对象

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class AgentStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentState:
    """
    智能体状态对象
    """
    agent_id: str
    status: AgentStatus = AgentStatus.INITIALIZING
    current_task_id: Optional[str] = None
    active_collaborations: List[str] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: Optional[datetime] = None
    error_message: Optional[str] = None
    capabilities_enabled: List[str] = field(default_factory=list)
    current_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "current_task_id": self.current_task_id,
            "active_collaborations": self.active_collaborations,
            "resource_usage": self.resource_usage,
            "performance_metrics": self.performance_metrics,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "error_message": self.error_message,
            "capabilities_enabled": self.capabilities_enabled,
            "current_context": self.current_context
        }
```

## 📨 消息和通信数据结构

### 1. 基础消息格式

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Message",
  "type": "object",
  "required": ["id", "type", "sender", "timestamp", "content"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
      "description": "消息唯一标识符 (UUID)"
    },
    "type": {
      "type": "string",
      "enum": [
        "request",
        "response",
        "notification",
        "broadcast",
        "collaboration_invite",
        "task_assignment",
        "status_update",
        "knowledge_share",
        "consensus_vote",
        "emergency"
      ],
      "description": "消息类型"
    },
    "sender": {
      "$ref": "#/definitions/MessageSender",
      "description": "发送者信息"
    },
    "recipients": {
      "$ref": "#/definitions/MessageRecipients",
      "description": "接收者信息"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "消息时间戳"
    },
    "ttl": {
      "type": "integer",
      "minimum": 0,
      "description": "生存时间 (秒)"
    },
    "priority": {
      "type": "string",
      "enum": ["emergency", "high", "medium", "low"],
      "default": "medium",
      "description": "消息优先级"
    },
    "content": {
      "$ref": "#/definitions/MessageContent",
      "description": "消息内容"
    },
    "context": {
      "$ref": "#/definitions/MessageContext",
      "description": "消息上下文"
    },
    "security": {
      "$ref": "#/definitions/MessageSecurity",
      "description": "安全信息"
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  },
  "definitions": {
    "MessageSender": {
      "type": "object",
      "required": ["agent_id"],
      "properties": {
        "agent_id": {
          "type": "string",
          "description": "发送者智能体ID"
        },
        "agent_name": {
          "type": "string",
          "description": "发送者名称"
        },
        "agent_type": {
          "type": "string",
          "description": "发送者类型"
        },
        "reputation_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "发送者声誉分数"
        },
        "authentication_token": {
          "type": "string",
          "description": "认证令牌"
        }
      }
    },
    "MessageRecipients": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["direct", "broadcast", "multicast", "group", "conditional"],
          "description": "接收类型"
        },
        "agent_ids": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "直接接收者ID列表"
        },
        "group_ids": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "群组ID列表"
        },
        "selection_criteria": {
          "$ref": "#/definitions/RecipientCriteria",
          "description": "接收者选择条件"
        }
      }
    },
    "RecipientCriteria": {
      "type": "object",
      "properties": {
        "capabilities": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "必需的能力"
        },
        "expertise": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "必需的专业领域"
        },
        "availability": {
          "type": "string",
          "enum": ["any", "available", "idle"],
          "description": "可用性要求"
        },
        "reputation_threshold": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "最低声誉要求"
        },
        "geographic_constraints": {
          "type": "object",
          "description": "地理位置约束"
        }
      }
    },
    "MessageContent": {
      "type": "object",
      "required": ["data"],
      "properties": {
        "data": {
          "description": "消息数据 (可以是任意类型)"
        },
        "format": {
          "type": "string",
          "enum": ["text", "json", "xml", "binary", "multimedia"],
          "default": "text",
          "description": "内容格式"
        },
        "encoding": {
          "type": "string",
          "default": "utf-8",
          "description": "编码方式"
        },
        "compression": {
          "type": "string",
          "enum": ["none", "gzip", "deflate"],
          "default": "none",
          "description": "压缩方式"
        },
        "size": {
          "type": "integer",
          "minimum": 0,
          "description": "内容大小 (字节)"
        },
        "checksum": {
          "type": "string",
          "description": "内容校验和"
        }
      }
    },
    "MessageContext": {
      "type": "object",
      "properties": {
        "conversation_id": {
          "type": "string",
          "description": "对话ID"
        },
        "thread_id": {
          "type": "string",
          "description": "线程ID"
        },
        "parent_message_id": {
          "type": "string",
          "description": "父消息ID"
        },
        "session_id": {
          "type": "string",
          "description": "会话ID"
        },
        "task_id": {
          "type": "string",
          "description": "相关任务ID"
        },
        "collaboration_id": {
          "type": "string",
          "description": "协作ID"
        },
        "memory_references": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "相关记忆引用"
        },
        "environmental_context": {
          "type": "object",
          "description": "环境上下文"
        }
      }
    },
    "MessageSecurity": {
      "type": "object",
      "properties": {
        "encryption_algorithm": {
          "type": "string",
          "description": "加密算法"
        },
        "signature": {
          "type": "string",
          "description": "数字签名"
        },
        "access_control": {
          "type": "object",
          "properties": {
            "required_clearance_level": {
              "type": "string",
              "enum": ["public", "confidential", "secret", "top_secret"]
            },
            "authorized_roles": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        },
        "integrity_hash": {
          "type": "string",
          "description": "完整性哈希"
        }
      }
    }
  }
}
```

### 2. 协作任务数据结构

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Collaboration Task",
  "type": "object",
  "required": ["task_id", "title", "type", "initiator", "created_at"],
  "properties": {
    "task_id": {
      "type": "string",
      "pattern": "^task_[a-f0-9]{32}$",
      "description": "任务唯一标识符"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "任务标题"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "任务描述"
    },
    "type": {
      "type": "string",
      "enum": [
        "individual",
        "collaborative",
        "distributed",
        "consensus",
        "competitive",
        "emergency"
      ],
      "description": "任务类型"
    },
    "complexity": {
      "type": "string",
      "enum": ["simple", "moderate", "complex", "expert"],
      "description": "复杂度等级"
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"],
      "default": "medium",
      "description": "优先级"
    },
    "status": {
      "$ref": "#/definitions/TaskStatus",
      "description": "任务状态"
    },
    "initiator": {
      "type": "string",
      "description": "任务发起者智能体ID"
    },
    "participants": {
      "$ref": "#/definitions/TaskParticipants",
      "description": "参与者信息"
    },
    "requirements": {
      "$ref": "#/definitions/TaskRequirements",
      "description": "任务要求"
    },
    "resources": {
      "$ref": "#/definitions/TaskResources",
      "description": "任务资源"
    },
    "timeline": {
      "$ref": "#/definitions/TaskTimeline",
      "description": "时间线"
    },
    "constraints": {
      "$ref": "#/definitions/TaskConstraints",
      "description": "约束条件"
    },
    "deliverables": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/TaskDeliverable"
      },
      "description": "交付物"
    },
    "collaboration_strategy": {
      "$ref": "#/definitions/CollaborationStrategy",
      "description": "协作策略"
    },
    "quality_criteria": {
      "$ref": "#/definitions/QualityCriteria",
      "description": "质量标准"
    },
    "progress": {
      "$ref": "#/definitions/TaskProgress",
      "description": "进度信息"
    },
    "communication_log": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/CommunicationLogEntry"
      },
      "description": "沟通日志"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "最后更新时间"
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  },
  "definitions": {
    "TaskStatus": {
      "type": "object",
      "required": ["current_status"],
      "properties": {
        "current_status": {
          "type": "string",
          "enum": [
            "draft",
            "pending_approval",
            "approved",
            "assigned",
            "in_progress",
            "waiting_dependencies",
            "under_review",
            "completed",
            "failed",
            "cancelled",
            "on_hold"
          ]
        },
        "status_history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "status": {
                "type": "string"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              },
              "changed_by": {
                "type": "string"
              },
              "reason": {
                "type": "string"
              }
            }
          }
        },
        "completion_percentage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        }
      }
    },
    "TaskParticipants": {
      "type": "object",
      "properties": {
        "assigned_agents": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/AssignedAgent"
          }
        },
        "required_roles": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/RequiredRole"
          }
        },
        "collaboration_model": {
          "type": "string",
          "enum": [
            "hierarchical",
            "peer_to_peer",
            "leader_follower",
            "democratic"
          ],
          "description": "协作模式"
        },
        "max_participants": {
          "type": "integer",
          "minimum": 1
        },
        "min_participants": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "AssignedAgent": {
      "type": "object",
      "required": ["agent_id", "role"],
      "properties": {
        "agent_id": {
          "type": "string"
        },
        "role": {
          "type": "string",
          "enum": [
            "leader",
            "coordinator",
            "specialist",
            "reviewer",
            "observer"
          ]
        },
        "responsibilities": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "allocated_time": {
          "type": "integer",
          "description": "分配的时间 (分钟)"
        },
        "contribution_weight": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "贡献权重"
        },
        "status": {
          "type": "string",
          "enum": [
            "invited",
            "accepted",
            "declined",
            "active",
            "completed",
            "removed"
          ]
        }
      }
    },
    "TaskRequirements": {
      "type": "object",
      "properties": {
        "functional_requirements": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "non_functional_requirements": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "required_capabilities": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "required_tools": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "input_data": {
          "type": "object",
          "properties": {
            "format": {
              "type": "string"
            },
            "schema": {
              "type": "object"
            },
            "source": {
              "type": "string"
            }
          }
        },
        "output_format": {
          "type": "object",
          "properties": {
            "format": {
              "type": "string"
            },
            "schema": {
              "type": "object"
            },
            "destination": {
              "type": "string"
            }
          }
        }
      }
    },
    "CollaborationStrategy": {
      "type": "object",
      "properties": {
        "coordination_pattern": {
          "type": "string",
          "enum": ["sequential", "parallel", "pipeline", "hybrid"]
        },
        "decision_making": {
          "type": "string",
          "enum": [
            "consensus",
            "majority_vote",
            "weighted_vote",
            "delegation",
            "autocratic"
          ]
        },
        "conflict_resolution": {
          "type": "string",
          "enum": ["negotiation", "arbitration", "escalation", "voting"]
        },
        "knowledge_sharing": {
          "type": "string",
          "enum": ["open", "restricted", "need_to_know", "hierarchical"]
        },
        "synchronization_method": {
          "type": "string",
          "enum": ["real_time", "batch", "event_driven", "scheduled"]
        }
      }
    }
  }
}
```

## 🧠 记忆数据结构

### 1. 记忆对象模型

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Memory Object",
  "type": "object",
  "required": [
    "memory_id",
    "content",
    "memory_type",
    "creator_id",
    "created_at"
  ],
  "properties": {
    "memory_id": {
      "type": "string",
      "pattern": "^mem_[a-f0-9]{32}$",
      "description": "记忆唯一标识符"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "记忆标题"
    },
    "content": {
      "type": "string",
      "description": "记忆内容"
    },
    "summary": {
      "type": "string",
      "maxLength": 500,
      "description": "记忆摘要"
    },
    "memory_type": {
      "type": "string",
      "enum": ["episodic", "semantic", "procedural", "working", "long_term"],
      "description": "记忆类型"
    },
    "creator_id": {
      "type": "string",
      "description": "创建者智能体ID"
    },
    "source": {
      "type": "string",
      "description": "记忆来源"
    },
    "access_control": {
      "$ref": "#/definitions/MemoryAccessControl",
      "description": "访问控制"
    },
    "content_structure": {
      "$ref": "#/definitions/ContentStructure",
      "description": "内容结构"
    },
    "quality_metrics": {
      "$ref": "#/definitions/QualityMetrics",
      "description": "质量指标"
    },
    "usage_statistics": {
      "$ref": "#/definitions/UsageStatistics",
      "description": "使用统计"
    },
    "version_info": {
      "$ref": "#/definitions/VersionInfo",
      "description": "版本信息"
    },
    "relationships": {
      "$ref": "#/definitions/MemoryRelationships",
      "description": "关联关系"
    },
    "embedding": {
      "$ref": "#/definitions/MemoryEmbedding",
      "description": "向量嵌入"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "最后更新时间"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "过期时间"
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  },
  "definitions": {
    "MemoryAccessControl": {
      "type": "object",
      "required": ["access_level", "owner_id"],
      "properties": {
        "access_level": {
          "type": "string",
          "enum": ["private", "group", "public", "restricted"],
          "description": "访问级别"
        },
        "owner_id": {
          "type": "string",
          "description": "所有者ID"
        },
        "authorized_agents": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "授权智能体列表"
        },
        "authorized_groups": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "授权群组列表"
        },
        "access_conditions": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/AccessCondition"
          },
          "description": "访问条件"
        },
        "privacy_level": {
          "type": "string",
          "enum": ["public", "internal", "confidential", "secret"],
          "description": "隐私级别"
        }
      }
    },
    "ContentStructure": {
      "type": "object",
      "properties": {
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "标签"
        },
        "keywords": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "关键词"
        },
        "entities": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/ExtractedEntity"
          },
          "description": "提取的实体"
        },
        "concepts": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/ExtractedConcept"
          },
          "description": "提取的概念"
        },
        "topics": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "主题"
        },
        "language": {
          "type": "string",
          "description": "语言"
        },
        "format": {
          "type": "string",
          "enum": ["text", "json", "xml", "markdown", "binary"],
          "description": "格式"
        }
      }
    },
    "ExtractedEntity": {
      "type": "object",
      "required": ["text", "type"],
      "properties": {
        "text": {
          "type": "string",
          "description": "实体文本"
        },
        "type": {
          "type": "string",
          "description": "实体类型"
        },
        "start_pos": {
          "type": "integer",
          "description": "开始位置"
        },
        "end_pos": {
          "type": "integer",
          "description": "结束位置"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "置信度"
        },
        "attributes": {
          "type": "object",
          "description": "实体属性"
        }
      }
    },
    "QualityMetrics": {
      "type": "object",
      "properties": {
        "accuracy_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "准确性分数"
        },
        "relevance_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "相关性分数"
        },
        "completeness_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "完整性分数"
        },
        "timeliness_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "时效性分数"
        },
        "trust_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "信任度分数"
        },
        "verification_count": {
          "type": "integer",
          "minimum": 0,
          "description": "验证次数"
        },
        "quality_assessments": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/QualityAssessment"
          },
          "description": "质量评估记录"
        }
      }
    },
    "MemoryEmbedding": {
      "type": "object",
      "properties": {
        "vector": {
          "type": "array",
          "items": {
            "type": "number"
          },
          "description": "嵌入向量"
        },
        "model": {
          "type": "string",
          "description": "嵌入模型"
        },
        "dimension": {
          "type": "integer",
          "description": "向量维度"
        },
        "generated_at": {
          "type": "string",
          "format": "date-time",
          "description": "生成时间"
        }
      }
    }
  }
}
```

## 🤝 协作会话数据结构

### 1. 协作会话对象

```python
@dataclass
class CollaborationSession:
    """
    协作会话对象
    """
    session_id: str
    title: str
    description: str
    initiator_id: str
    participants: List[str]
    session_type: str  # brainstorming, problem_solving, decision_making, etc.

    # 会话状态
    status: str  # planning, active, paused, completed, cancelled
    current_phase: str
    phases: List[CollaborationPhase]

    # 时间信息
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None

    # 协作规则
    collaboration_rules: Dict[str, Any] = field(default_factory=dict)
    decision_mechanism: str = "consensus"  # consensus, majority, weighted, etc.
    quorum_requirement: float = 0.6

    # 会话内容
    messages: List[str] = field(default_factory=list)
    decisions: List[CollaborationDecision] = field(default_factory=list)
    artifacts: List[CollaborationArtifact] = field(default_factory=list)

    # 结果和评估
    outcomes: List[str] = field(default_factory=list)
    satisfaction_scores: Dict[str, float] = field(default_factory=dict)
    effectiveness_metrics: Dict[str, Any] = field(default_factory=dict)

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationPhase:
    """
    协作阶段
    """
    phase_id: str
    name: str
    description: str
    objectives: List[str]
    duration_estimate: int  # minutes

    # 阶段状态
    status: str  # pending, active, completed, skipped
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 参与者和角色
    required_participants: List[str] = field(default_factory=list)
    active_participants: List[str] = field(default_factory=list)
    facilitator: Optional[str] = None

    # 阶段规则
    phase_rules: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)

    # 产出
    deliverables: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "duration_estimate": self.duration_estimate,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "required_participants": self.required_participants,
            "active_participants": self.active_participants,
            "facilitator": self.facilitator,
            "phase_rules": self.phase_rules,
            "success_criteria": self.success_criteria,
            "deliverables": self.deliverables,
            "insights": self.insights
        }
```

## 📊 性能和监控数据结构

### 1. 性能指标

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Performance Metrics",
  "type": "object",
  "required": ["metric_id", "timestamp", "source", "values"],
  "properties": {
    "metric_id": {
      "type": "string",
      "description": "指标唯一标识符"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "测量时间戳"
    },
    "source": {
      "type": "object",
      "required": ["type", "id"],
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "agent",
            "system",
            "collaboration",
            "memory",
            "communication"
          ],
          "description": "数据源类型"
        },
        "id": {
          "type": "string",
          "description": "数据源标识符"
        }
      }
    },
    "values": {
      "type": "object",
      "properties": {
        "response_time_ms": {
          "type": "number",
          "minimum": 0,
          "description": "响应时间 (毫秒)"
        },
        "throughput_rps": {
          "type": "number",
          "minimum": 0,
          "description": "吞吐量 (请求/秒)"
        },
        "cpu_usage_percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "CPU使用率 (%)"
        },
        "memory_usage_mb": {
          "type": "number",
          "minimum": 0,
          "description": "内存使用量 (MB)"
        },
        "network_latency_ms": {
          "type": "number",
          "minimum": 0,
          "description": "网络延迟 (毫秒)"
        },
        "error_rate_percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "错误率 (%)"
        },
        "success_rate_percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "成功率 (%)"
        },
        "collaboration_efficiency": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "协作效率"
        },
        "knowledge_utilization": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "知识利用率"
        },
        "consensus_time_seconds": {
          "type": "number",
          "minimum": 0,
          "description": "共识达成时间 (秒)"
        }
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "session_id": {
          "type": "string",
          "description": "会话ID"
        },
        "task_id": {
          "type": "string",
          "description": "任务ID"
        },
        "collaboration_id": {
          "type": "string",
          "description": "协作ID"
        },
        "environment": {
          "type": "string",
          "enum": ["development", "testing", "staging", "production"],
          "description": "环境"
        },
        "load_level": {
          "type": "string",
          "enum": ["low", "medium", "high", "peak"],
          "description": "负载级别"
        }
      }
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "标签"
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  }
}
```

## 🔧 配置和设置数据结构

### 1. 系统配置

```python
@dataclass
class SystemConfiguration:
    """
    系统配置对象
    """
    # 基础配置
    system_id: str
    environment: str  # development, testing, production
    version: str

    # 网络配置
    network_config: NetworkConfig

    # 安全配置
    security_config: SecurityConfig

    # 性能配置
    performance_config: PerformanceConfig

    # 协作配置
    collaboration_config: CollaborationConfig

    # 记忆配置
    memory_config: MemoryConfig

    # 监控配置
    monitoring_config: MonitoringConfig

    # 日志配置
    logging_config: LoggingConfig

    # 更新时间
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "system_id": self.system_id,
            "environment": self.environment,
            "version": self.version,
            "network_config": self.network_config.to_dict(),
            "security_config": self.security_config.to_dict(),
            "performance_config": self.performance_config.to_dict(),
            "collaboration_config": self.collaboration_config.to_dict(),
            "memory_config": self.memory_config.to_dict(),
            "monitoring_config": self.monitoring_config.to_dict(),
            "logging_config": self.logging_config.to_dict(),
            "last_updated": self.last_updated.isoformat()
        }

@dataclass
class NetworkConfig:
    """网络配置"""
    max_connections: int = 1000
    connection_timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: int = 1  # seconds
    compression_enabled: bool = True
    encryption_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_connections": self.max_connections,
            "connection_timeout": self.connection_timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "compression_enabled": self.compression_enabled,
            "encryption_required": self.encryption_required
        }

@dataclass
class CollaborationConfig:
    """协作配置"""
    max_concurrent_sessions: int = 100
    default_consensus_threshold: float = 0.6
    session_timeout_minutes: int = 60
    max_participants_per_session: int = 20
    auto_save_interval: int = 5  # minutes
    conflict_resolution_strategy: str = "voting"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "default_consensus_threshold": self.default_consensus_threshold,
            "session_timeout_minutes": self.session_timeout_minutes,
            "max_participants_per_session": self.max_participants_per_session,
            "auto_save_interval": self.auto_save_interval,
            "conflict_resolution_strategy": self.conflict_resolution_strategy
        }
```

---

这个完整的数据结构定义为多智能体协作协议提供了标准化的数据格式和接口规范，确保不同组件和智能体之间的互操作性和数据一致性。所有结构都支持扩展性，可以根据具体需求进行定制和扩展。
