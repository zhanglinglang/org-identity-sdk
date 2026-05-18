# org-identity-sdk · 可信智能体协作基础设施

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocol-ATH%2Fv1-orange.svg)](https://github.com/lingzhu-ai/org-identity-spec)

> **让 Agent 之间不仅能对话，更能放心对话。**

---

## 这是什么？

`org-identity-sdk` 是一套面向智能体协作环境的 **身份可信基础设施**。

在 A2A（Agent-to-Agent）通信场景中，现有协议解决了"能不能说话"的问题（通信协议层），Google 的 AgentCard 抽象了"你是谁"的声明（身份描述层）。

但还缺关键的一环——**"能不能放心说话"**。

`org-identity-sdk` 补齐了这一层：

```
┌──────────────────────────────────────────────────┐
│              信任层 · org-identity                │
│  "能不能放心说话"                                  │
│  → 组织身份认证  → 能力声明  → 责任可追溯          │
├──────────────────────────────────────────────────┤
│             身份层 · Google AgentCard              │
│  "你是谁"                                        │
├──────────────────────────────────────────────────┤
│             通信层 · A2A / ATH                     │
│  "能不能说话"                                     │
└──────────────────────────────────────────────────┘
```

---

## 核心特性

- 🔐 **组织身份认证**：统一社会信用代码 + 法人手机验证码确权
- 📋 **标准化声明**：ATH/v1 协议定义的身份卡片 Schema（JSON Schema 约束）
- 🔗 **协议兼容**：一张卡片，同时支持 ATH/v1 和 Google A2A AgentCard
- ✍️ **数字签名**：确权后可签发防篡改的签名身份卡片
- 🧩 **一行代码**：Builder 模式，链式调用，零学习成本
- 🔌 **可插拔架构**：短信通道、签名算法、校验规则均可替换

---

## 快速开始

### 安装

```bash
pip install org-identity-sdk
```

### 30 秒上手

```python
from org_identity import OrgIdentityClient

client = OrgIdentityClient()

# 一行代码生成身份卡片
card = client.generate_identity_card(
    uscc="91110108MA01XXXXXX",
    legal_name="你的公司名称",
    agent_name="你的智能体",
    agent_version="1.0.0",
    agent_description="描述你的智能体",
    contact_phone="+8613800138000",
    contact_email="admin@example.com",
)

# 校验
result = client.validate(card)
print("✓ 校验通过" if result.is_valid else "✗ 校验失败")

# 导出为 Google AgentCard 兼容格式
exporter = client.export(card)
agentcard_json = exporter.to_agentcard()
```

### 确权 & 签名

```python
# 1. 发起手机验证
session = client.init_verification(uscc="91110108MA01XXXXXX", phone="+8613800138000")
print(session.message)  # "验证码已发送至 ****8000"

# 2. 用户输入验证码后签名
code = input("请输入短信验证码: ")
signed_card = client.verify_and_sign(card, session.session_id, code)

# 3. 导出签名卡片
exporter = client.export(signed_card)
print(exporter.summary())
```

---

## 身份卡片结构

```json
{
  "protocol_version": "ATH/v1",
  "card_id": "uuid-v4",
  "issued_at": "2026-05-18T00:00:00Z",
  "expires_at": "2026-11-14T00:00:00Z",
  "org_identity": {
    "uscc": "统一社会信用代码",
    "legal_name": "法人实体名称",
    "security_cert_level": "L1 | L2 | L3"
  },
  "agent_profile": {
    "name": "Agent 名称",
    "version": "语义化版本",
    "capabilities": ["能力列表"],
    "skills": [{"id": "...", "name": "...", "description": "..."}]
  },
  "accountability": {
    "responsible_entity": "责任主体",
    "contact_phone": "+86...",
    "contact_email": "...",
    "data_processing_scope": "conversation_only | ..."
  },
  "signature": {
    "algorithm": "RS256",
    "verification_method": "legal_rep_phone"
  }
}
```

完整 Schema 定义: [schema/org-identity.schema.json](schema/org-identity.schema.json)

---

## 项目结构

```
org-identity-sdk/
├── schema/                          # JSON Schema 标准定义
│   └── org-identity.schema.json
├── src/org_identity/                # Python SDK
│   ├── __init__.py
│   ├── client.py                    # 统一客户端（一行代码入口）
│   ├── builder.py                   # 卡片构造器
│   ├── validator.py                 # 格式 + 业务逻辑校验
│   ├── verifier.py                  # 法人手机确权
│   └── exporter.py                  # 多格式导出
├── examples/
│   └── basic_usage.py               # 完整使用示例
├── tests/
│   ├── test_builder.py
│   └── test_validator.py
├── pyproject.toml
├── LICENSE (Apache 2.0)
└── README.md
```

---

## 协议规范 · ATH/v1

ATH（Agent Trustworthy Handshake / 智能体可信握手协议）是 `org-identity-sdk` 遵循的身份声明协议。

| 版本 | 状态 | 说明 |
|------|------|------|
| ATH/v1 | 🚧 Draft | 初始版本，与 Google A2A AgentCard 双向兼容 |

ATH/v1 的核心原则:
- **身份公开**: 任何 Agent 可公开声明其所属组织
- **能力声明**: Agent 必须声明其技能和能力范围
- **责任追溯**: 提供真实可用的联系方式
- **最小数据**: 只声明必要字段，按需扩展
- **可验证性**: 支持数字签名后的防篡改验证

---

## License

Apache 2.0 · © 2026 南京灵枢铸药智能科技有限公司

---

## 参与贡献

我们以 **开放讨论** 的姿态推进这个项目。

欢迎通过 Issue / PR 参与:
- [GitHub](https://github.com/lingzhu-ai/org-identity-sdk)
- ModelScope（即将上线）

贡献指南: [CONTRIBUTING.md](CONTRIBUTING.md)
