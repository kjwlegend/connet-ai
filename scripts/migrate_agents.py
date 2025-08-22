#!/usr/bin/env python3
"""
Agent data migration script from legacy JSON format to new AIAgentModel structure.

This script migrates agent data from the old xiaoguang_llm_agents format
to the new database model structure defined in AIAgentModel.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


def parse_legacy_model_config(model_config_str: str) -> Dict[str, Any]:
    """Parse legacy model config string into new format."""
    try:
        config = json.loads(model_config_str)
        return {
            "default_model": "gpt-4.1-mini",
            "fallback_models": ["gpt-4.1-mini", "claude-3.7-sonnet"],
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 4096),
            "top_p": 1.0,
            "presence_penalty": config.get("presence_penalty", 0.0),
            "frequency_penalty": config.get("frequency_penalty", 0.0),
        }
    except Exception:
        return {
            "default_model": "gpt-4.1-mini",
            "temperature": 0.3,
            "max_tokens": 4096,
        }


def extract_system_prompt(prompts_data_str: str) -> str:
    """Extract system prompt from legacy prompts_data format."""
    try:
        prompts = json.loads(prompts_data_str)
        if isinstance(prompts, list) and len(prompts) > 0:
            return prompts[0].get("content", "")
    except Exception:
        pass
    return ""


def generate_agent_name(display_name: str, existing_names: set) -> str:
    """Generate unique agent name for mentions from display name.
    If the name is in Chinese, generate an English name.
    """

    def is_chinese(text: str) -> bool:
        # Check if the text contains any CJK characters
        return any("\u4e00" <= char <= "\u9fff" for char in text)

    def chinese_to_pinyin(text: str) -> str:
        try:
            from pypinyin import lazy_pinyin

            pinyin_list = lazy_pinyin(text)
            return "_".join(pinyin_list)
        except ImportError:
            # Fallback: just use 'agent' if pypinyin is not installed
            return "agent"

    # Remove parentheses and special characters
    if is_chinese(display_name):
        base_name = chinese_to_pinyin(display_name)
    else:
        base_name = re.sub(r"[^\w\u4e00-\u9fff]", "_", display_name.lower())
        base_name = base_name.strip("_")

    if base_name not in existing_names:
        return base_name

    # Add number suffix if name exists
    counter = 1
    while f"{base_name}_{counter}" in existing_names:
        counter += 1
    return f"{base_name}_{counter}"


def categorize_agent(agent_name: str, description: str) -> str:
    """Categorize agent based on name and description."""
    agent_name_lower = agent_name.lower()
    description_lower = description.lower()

    if "绘图" in agent_name or "绘画" in description or "艺术" in description:
        return "art"
    elif "编程" in description or "代码" in description or "技术" in description:
        return "development"
    elif "翻译" in description or "语言" in description:
        return "language"
    elif "写作" in description or "文字" in description:
        return "writing"
    elif "音乐" in description or "歌曲" in description:
        return "music"
    elif "小光" in agent_name:
        return "assistant"
    else:
        return "general"


def extract_capabilities(description: str, system_prompt: str) -> List[str]:
    """Extract capabilities from description and system prompt."""
    capabilities = []
    text = (description + " " + system_prompt).lower()

    capability_keywords = {
        "code_generation": ["编程", "代码", "开发"],
        "image_generation": ["绘图", "绘画", "图像"],
        "translation": ["翻译", "语言"],
        "writing": ["写作", "文字", "创作"],
        "music": ["音乐", "歌曲", "作曲"],
        "conversation": ["对话", "聊天", "交流"],
        "analysis": ["分析", "解析", "分析师"],
        "teaching": ["教学", "教师", "指导"],
    }

    for capability, keywords in capability_keywords.items():
        if any(keyword in text for keyword in keywords):
            capabilities.append(capability)

    return capabilities if capabilities else ["general_assistance"]


def extract_tags(description: str, category: str) -> List[str]:
    """Extract tags from description and category."""
    tags = [category]

    tag_keywords = {
        "中文": ["zh-CN", "chinese"],
        "english": ["en", "english"],
        "creative": ["创意", "创作", "艺术"],
        "technical": ["技术", "专业", "工程"],
        "professional": ["专业", "正式"],
        "development": ["开发", "编程", "代码"],
        "art": ["艺术", "绘画", "设计"],
        "music": ["音乐", "作曲", "创作"],
        "writing": ["写作", "文字", "创作"],
        "translation": ["翻译", "语言"],
        "conversation": ["对话", "聊天", "交流"],
        "analysis": ["分析", "解析", "分析师"],
        "teaching": ["教学", "教师", "指导"],
        "storytelling": ["故事", "讲故事", "创作"],
        "general_assistance": ["通用", "助手", "帮助"],
    }

    description_lower = description.lower()
    for tag, keywords in tag_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            tags.append(tag)

    return list(set(tags))


def determine_conversation_style(description: str, system_prompt: str) -> str:
    """Determine conversation style from description and system prompt."""
    text = (description + " " + system_prompt).lower()

    if "专业" in text or "正式" in text:
        return "professional"
    elif "幽默" in text or "有趣" in text or "活泼" in text:
        return "humorous"
    elif "友好" in text or "亲切" in text or "温暖" in text:
        return "casual"
    else:
        return "professional"


def migrate_agent_data(
    legacy_agent: Dict[str, Any], default_user_id: str, existing_names: set
) -> Dict[str, Any]:
    """Migrate a single agent from legacy format to new format."""

    # Extract basic info
    agent_name = generate_agent_name(legacy_agent.get("agent_name", ""), existing_names)
    existing_names.add(agent_name)

    display_name = legacy_agent.get("agent_name", "Unknown Agent")
    description = legacy_agent.get("description", "")
    introduction = legacy_agent.get("chat_intro", "")
    system_prompt = extract_system_prompt(legacy_agent.get("prompts_data", ""))

    # Parse model config
    model_preferences = parse_legacy_model_config(legacy_agent.get("modelconfig", "{}"))

    # Categorize and extract metadata
    category = categorize_agent(display_name, description)
    capabilities = extract_capabilities(description, system_prompt)
    tags = extract_tags(description, category)
    conversation_style = determine_conversation_style(description, system_prompt)

    # Handle avatar
    avatar_url = None
    legacy_image = legacy_agent.get("image", "")
    if legacy_image and legacy_image.startswith("avatars/"):
        avatar_url = f"https://xiaoguangai.oss-cn-shanghai.aliyuncs.com/{legacy_image}"

    # Convert timestamps
    created_at = datetime.fromisoformat(
        legacy_agent.get("created_at", datetime.now().isoformat())
    )
    updated_at = datetime.fromisoformat(
        legacy_agent.get("updated_at", datetime.now().isoformat())
    )

    # Build new agent data
    new_agent = {
        "id": str(uuid.uuid4()),
        "name": agent_name,
        "display_name": display_name,
        "description": description,
        "introduction": introduction,
        "agent_type": (
            "custom" if not legacy_agent.get("is_feature_agent") else "system"
        ),
        "version": "1.0.0",
        "status": "active" if legacy_agent.get("active", 1) else "inactive",
        "is_public": True,
        "is_active": bool(legacy_agent.get("active", 1)),
        "avatar_url": avatar_url,
        "avatar_style": "default",
        "conversation_style": conversation_style,
        "system_prompt": system_prompt,
        "personality_config": {
            "role": display_name,
            "communication_style": conversation_style,
        },
        "model_preferences": model_preferences,
        "capabilities": capabilities,
        "required_permissions": [],
        "tags": tags,
        "category": category,
        "usage_count": 0,
        "follower_count": 0,
        "agent_metadata": {},
        "description_embedding": None,
        "capabilities_embedding": None,
        "created_by": default_user_id,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "last_used_at": None,
    }

    return new_agent


def main():
    """Main migration function."""
    # Configuration
    input_file = Path("agents/xiaoguang_llm_agents_202508192254.json")
    output_file = Path("scripts/migrated_agents.json")

    # Default user ID (you should replace this with actual user UUID)
    default_user_id = "45beb035-0c92-4da1-a23d-6fcbd45f6d9b"
    print(f"Using default user ID: {default_user_id}")
    print(
        "Please note: You should replace this with an actual user UUID from your users table"
    )

    # Load legacy data
    print(f"Loading legacy agent data from {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            legacy_data = json.load(f)
    except Exception as e:
        print(f"Error loading legacy data: {e}")
        return

    legacy_agents = legacy_data.get("xiaoguang_llm_agents", [])
    print(f"Found {len(legacy_agents)} agents to migrate")

    # Migrate agents
    migrated_agents = []
    existing_names = set()

    for i, legacy_agent in enumerate(legacy_agents):
        try:
            print(
                f"Migrating agent {i+1}/{len(legacy_agents)}: {legacy_agent.get('agent_name', 'Unknown')}"
            )
            migrated_agent = migrate_agent_data(
                legacy_agent, default_user_id, existing_names
            )
            migrated_agents.append(migrated_agent)
        except Exception as e:
            print(
                f"Error migrating agent {legacy_agent.get('agent_name', 'Unknown')}: {e}"
            )
            continue

    # Save migrated data
    output_data = {
        "migration_info": {
            "source_file": str(input_file),
            "migration_date": datetime.now().isoformat(),
            "total_agents": len(legacy_agents),
            "migrated_agents": len(migrated_agents),
            "default_user_id": default_user_id,
        },
        "agents": migrated_agents,
    }

    print(f"Saving migrated data to {output_file}...")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Migration completed successfully!")
    print(f"Migrated {len(migrated_agents)}/{len(legacy_agents)} agents")
    print(f"Output file: {output_file}")
    print("\nNext steps:")
    print("1. Review the migrated_agents.json file")
    print("2. Update the default_user_id with actual user UUID")
    print("3. Use the database import script to insert data into your database")


if __name__ == "__main__":
    main()
