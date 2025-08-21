# Agent Data Migration Guide

本指南将帮助您将旧的 agent 数据从 JSON 文件迁移到新的数据库模型中。

## 概览

迁移过程包含以下步骤：
1. 数据格式转换（JSON → 新模型格式）
2. 数据验证和清理
3. 导入到数据库

## 文件说明

- `migrate_agents.py` - 主要迁移脚本，将旧 JSON 格式转换为新模型格式
- `import_migrated_agents.py` - 数据库导入脚本，将转换后的数据导入数据库
- `migrated_agents.json` - 迁移后的数据文件（脚本执行后生成）

## 数据映射关系

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| `agent_name` | `display_name` | 显示名称 |
| `agent_name` | `name` | 生成唯一标识符（用于 @ 提及） |
| `description` | `description` | 描述信息 |
| `prompts_data` | `system_prompt` | 系统提示词 |
| `modelconfig` | `model_preferences` | 模型配置 |
| `use_count` | `usage_count` | 使用次数 |
| `active` | `is_active` | 是否激活 |
| `is_feature_agent` | `agent_type` | 代理类型 |
| `language` | `personality_config.language` | 语言设置 |

## 执行步骤

### 第一步：运行数据迁移脚本

```bash
cd d:/codes/xiaoguang-next-gen
python scripts/migrate_agents.py
```

**预期输出：**
- 显示迁移进度
- 生成 `scripts/migrated_agents.json` 文件
- 显示迁移统计信息

**成功标志：**
```
Migration completed successfully!
Migrated 191/191 agents
Output file: scripts\migrated_agents.json
```

### 第二步：检查迁移结果

查看生成的 `scripts/migrated_agents.json` 文件：

```bash
# 查看文件结构
python -c "
import json
with open('scripts/migrated_agents.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print('Migration Info:', data['migration_info'])
    print('Sample Agent:', json.dumps(data['agents'][0], indent=2, ensure_ascii=False)[:500])
"
```

### 第三步：更新用户ID（重要）

迁移脚本会生成一个默认的用户ID。您需要：

1. 在您的用户表中找到一个实际的用户UUID
2. 或者创建一个专门用于迁移的用户
3. 更新 `migrated_agents.json` 中的用户ID：

```python
# 更新用户ID脚本
import json

# 替换为您的实际用户UUID
ACTUAL_USER_ID = "your-actual-user-uuid-here"

with open('scripts/migrated_agents.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 更新所有代理的创建者ID
for agent in data['agents']:
    agent['created_by'] = ACTUAL_USER_ID

# 更新迁移信息
data['migration_info']['default_user_id'] = ACTUAL_USER_ID

with open('scripts/migrated_agents.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated user ID to: {ACTUAL_USER_ID}")
```

### 第四步：配置数据库连接

编辑 `scripts/import_migrated_agents.py` 文件，更新数据库连接信息：

```python
# 更新这行
DATABASE_URL = "postgresql://username:password@localhost:5432/xiaoguang_db"

# 替换为您的实际数据库信息：
# - username: 数据库用户名
# - password: 数据库密码  
# - localhost:5432: 数据库主机和端口
# - xiaoguang_db: 数据库名称
```

### 第五步：运行数据库导入

```bash
cd d:/codes/xiaoguang-next-gen
python scripts/import_migrated_agents.py
```

**注意事项：**
- 脚本会提示确认后才执行导入
- 如果用户不存在，会自动创建默认用户
- 如果代理已存在（按名称），会跳过导入
- 所有操作都在事务中执行，失败时会自动回滚

## 数据转换详情

### 1. 代理名称生成
- 旧的 `agent_name` 用作 `display_name`
- 自动生成符合规范的唯一 `name`（用于 @ 提及）
- 去除特殊字符，避免冲突

### 2. 分类映射
脚本会根据描述自动分类：
- `art` - 绘图、绘画相关
- `development` - 编程、技术相关  
- `language` - 翻译、语言相关
- `writing` - 写作、文字相关
- `music` - 音乐相关
- `assistant` - 小光系列
- `general` - 通用类型

### 3. 能力提取
从描述和系统提示词中自动提取能力标签：
- `code_generation` - 代码生成
- `image_generation` - 图像生成
- `translation` - 翻译
- `writing` - 写作
- `music` - 音乐
- `conversation` - 对话
- `analysis` - 分析
- `teaching` - 教学

### 4. 默认值处理
对于新模型中的必填字段，脚本会生成合理的默认值：
- `version`: "1.0.0"
- `avatar_style`: "default"  
- `conversation_style`: 根据描述推断
- `follower_count`: 0
- `required_permissions`: []

## 故障排除

### 常见问题

**1. 编码问题**
如果看到乱码，确保：
- 文件编码为 UTF-8
- Python 脚本中正确处理 encoding='utf-8'

**2. 数据库连接失败**
检查：
- DATABASE_URL 是否正确
- 数据库是否运行
- 用户权限是否足够
- 网络连接是否正常

**3. 用户ID 不存在**
- 确保更新了正确的用户UUID
- 或让脚本创建默认用户

**4. 代理名称冲突**
- 脚本会自动处理名称冲突
- 重复运行会跳过已存在的代理

### 验证导入结果

```sql
-- 检查导入的代理数量
SELECT COUNT(*) FROM agents;

-- 查看代理分类分布
SELECT category, COUNT(*) 
FROM agents 
GROUP BY category 
ORDER BY COUNT(*) DESC;

-- 查看代理类型分布
SELECT agent_type, COUNT(*) 
FROM agents 
GROUP BY agent_type;

-- 检查使用次数统计
SELECT 
    MAX(usage_count) as max_usage,
    MIN(usage_count) as min_usage,
    AVG(usage_count) as avg_usage
FROM agents;
```

## 回滚操作

如果需要回滚导入的数据：

```sql
-- 删除所有迁移的代理（谨慎使用）
DELETE FROM agents 
WHERE agent_metadata->>'legacy_agent_id' IS NOT NULL;

-- 或根据创建时间删除
DELETE FROM agents 
WHERE created_at > '2024-08-21 00:00:00';
```

## 后续步骤

1. **验证数据完整性** - 检查关键字段是否正确
2. **更新头像** - 如需要，上传并更新代理头像URL  
3. **权限配置** - 根据需要配置代理权限
4. **测试功能** - 在前端测试代理功能是否正常
5. **备份数据** - 为生产环境创建数据备份

## 联系支持

如果遇到问题：
1. 检查日志输出中的错误信息
2. 验证数据库连接和权限
3. 确认所有依赖已正确安装
4. 查看 BFF 服务的相关文档