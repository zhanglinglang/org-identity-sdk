# org-identity-sdk · 可信智能体协作基础设施

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocol-ATH%2Fv1-orange.svg)](https://gitee.com/lingshuzhuyao/org-identity-sdk)
[![Gitee Stars](https://gitee.com/lingshuzhuyao/org-identity-sdk/badge/star.svg?theme=dark)](https://gitee.com/lingshuzhuyao/org-identity-sdk)
[![Tests](https://img.shields.io/badge/tests-11%2F11%20passed-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/status-alpha-yellow.svg)]()

> **让 Agent 之间不仅能对话，更能放心对话。**

---

## 📖 目录

- [为什么需要 org-identity](#为什么需要-org-identity)
- [定位对比](#定位对比)
- [快速开始](#快速开始)
- [演示输出](#演示输出)
- [核心特性](#核心特性)
- [身份卡片结构](#身份卡片结构)
- [架构设计](#架构设计)
- [项目结构](#项目结构)
- [安装后验证](#安装后验证)
- [API 文档](#api-文档)
- [项目状态](#项目状态)
- [相关链接](#相关链接)
- [协议规范](#协议规范)
- [参与贡献](#参与贡献)
- [License](#license)

---

## 为什么需要 org-identity

智能体协作生态正快速演进，但**信任基础设施**严重滞后：

| 维度 | 现状 | 缺失 |
|------|------|------|
| 通信协议 | A2A / ATH 已解决 Agent 间通信 | ✅ 已解决 |
| 身份声明 | Google AgentCard 定义了"我是谁" | ⚠️ 部分解决 |
| **组织认证** | **无标准方案** | ❌ **完全空白** |
| **责任追溯** | **无法确定谁来负责** | ❌ **完全空白** |
| **合规适配** | **没有考虑国内监管要求** | ❌ **完全空白** |

`org-identity-sdk` 补齐了后三层——让 Agent 之间的协作建立在**可验证的组织身份**和**可追溯的责任链路**之上。

---

## 定位对比

```
┌─────────────────────────────────────────────────────────┐
│                 信任层 · org-identity                     │
│  "能不能放心说话"                                         │
│  组织身份认证 → 能力声明 → 责任可追溯 → 数字签名           │
├─────────────────────────────────────────────────────────┤
│             身份声明层 · Google AgentCard                  │
│  "你是谁"                                                │
│  → org-identity 可直接导出 AgentCard 兼容格式              │
├─────────────────────────────────────────────────────────┤
│             通信协议层 · A2A / ATH                         │
│  "能不能说话"                                             │
│  → 阿里 AgentScope / 腾讯 trpc-a2a-go / Google A2A        │
└─────────────────────────────────────────────────────────┘
```

### 三方对比

| 特性 | A2A 协议 | Google AgentCard | **org-identity** |
|------|:--------:|:----------------:|:----------------:|
| Agent 间通信 | ✅ 核心能力 | ❌ 不涉及 | ❌ 不涉及 |
| 身份声明 | ❌ | ✅ 名称/描述/技能 | ✅ 完整组织身份 |
| 统一社会信用代码 (USCC) | ❌ | ❌ | ✅ |
| 智能体备案号 | ❌ | ❌ | ✅ |
| 安全等级认证 | ❌ | ❌ | ✅ L1/L2/L3 |
| 法人手机确权 | ❌ | ❌ | ✅ 短信验证码 |
| 数字签名防篡改 | ❌ | ❌ | ✅ RS256 |
| 数据处理范围声明 | ❌ | ❌ | ✅ |
| 责任主体 + 联系方式 | ❌ | ⚠️ 仅描述 | ✅ 结构化字段 |
| AgentCard 兼容导出 | — | — | ✅ 双向兼容 |
| 监管合规适配 | ❌ | ❌ | ✅ 支持扩展 |
| 开源协议 | — | Apache 2.0 | Apache 2.0 |

> **org-identity 不替代 A2A 或 AgentCard，而是在它们的上层补齐信任维度。**

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

# 校验卡片
result = client.validate(card)
print("✓ 校验通过" if result.is_valid else "✗ 校验失败")

# 导出为 Google AgentCard 兼容格式
agentcard_json = client.export(card).to_agentcard()
```

### 确权 & 签名

```python
# 1. 发起手机验证
session = client.init_verification(
    uscc="91110108MA01XXXXXX",
    phone="+8613800138000"
)
print(session.message)  # "验证码已发送至 ****8000"

# 2. 用户输入验证码后签名
code = input("请输入短信验证码: ")
signed_card = client.verify_and_sign(card, session.session_id, code)

# 3. 导出签名卡片摘要
print(client.export(signed_card).summary())
```

---

## 演示输出

运行 `python examples/basic_usage.py` 的实际输出：

```
1. 生成身份卡片...

2. 校验卡片...
   [OK] 校验通过
   [!] [Tip] 建议填写 accountability.contact_person
   [!] [Tip] 卡片未签名，建议完成确权验证后添加签名

3. 导出格式...

--- Google AgentCard 兼容格式 (前 200 字符) ---
{
  "name": "医药研发智能助手",
  "description": "专注于药物分子筛选与临床试验数据挖掘的智能体",
  "url": "https://agent.lingshuyaozhi.com/a2a",
  "version": "1.0.0",
  "capabilities": { "streaming": false },
  "skills": [ ... ]
}

--- 摘要 ---
════════════════════════════════════════════════════
Org-Identity 身份卡片摘要
════════════════════════════════════════════════════
卡片 ID:      a5a9df23-4d5a-410b-ae1f-ef527c99c7ed
协议版本:     ATH/v1

── 组织身份 ──
名称:         南京灵枢铸药智能科技有限公司
USCC:         91110108MA01ABCDEF
安全等级:     L1

── Agent 信息 ──
名称:         医药研发智能助手
版本:         1.0.0
能力:         文献检索, 分子对接, 临床试验分析
端点:         https://agent.lingshuyaozhi.com/a2a

── 责任信息 ──
责任主体:     南京灵枢铸药智能科技有限公司
联系方式:     admin@lingshuyaozhi.com
数据处理:     conversation_only

── 签名状态 ──
已签名:       否
════════════════════════════════════════════════════

4. 确权验证流程 (演示)...

==================================================
[短信模拟] 发送至: +8613800138000
[短信模拟] 内容: 【灵枢智能】您的 Agent 身份确权验证码: 984336，
                  5分钟内有效。请勿泄露给他人。
==================================================

   验证码已发送至 **********8000，5分钟��有效

[OK] 示例完成!
```

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 🔐 **组织身份认证** | 统一社会信用代码 (USCC) + 法人手机验证码确权 |
| 📋 **标准化 Schema** | ATH/v1 协议，JSON Schema 2020-12 约束，字段完整性校验 |
| 🔗 **协议兼容** | 一张卡片同时支持 ATH/v1 和 Google A2A AgentCard |
| ✍️ **数字签名** | 确权后签发 RS256 签名的防篡改身份卡片 |
| 🧩 **Builder 模式** | 链式调用，零学习成本，一行代码生成完整卡片 |
| 🔌 **可插拔架构** | 短信通道、签名算法、校验规则、存储后端均可替换 |
| 🛡️ **安全设计** | 24h 内同一 USCC 最多 3 次验证尝试，验证码 5 分钟有效期 |
| ⏰ **卡片有效期** | 签发后 6 个月自动过期，需重新确权 |

---

## 身份卡片结构

```json
{
  "protocol_version": "ATH/v1",
  "card_id": "uuid-v4",
  "issued_at": "2026-05-18T00:00:00Z",
  "expires_at": "2026-11-14T00:00:00Z",

  "org_identity": {
    "uscc": "91110108MA01ABCDEF",
    "legal_name": "法人实体名称",
    "agent_registration_id": "智能体备案号（可选）",
    "security_cert_level": "L1 | L2 | L3",
    "establishment_date": "2020-01-01"
  },

  "agent_profile": {
    "name": "Agent 名称",
    "version": "1.0.0",
    "description": "Agent 简介",
    "url": "https://agent.example.com/a2a",
    "capabilities": ["capability1", "capability2"],
    "skills": [
      {"id": "skill-1", "name": "技能名", "description": "技能描述"}
    ]
  },

  "accountability": {
    "responsible_entity": "责任主体名称",
    "contact_person": "联系人（可选）",
    "contact_phone": "+86-xxx-xxxxxxxx",
    "contact_email": "admin@example.com",
    "data_processing_scope": "conversation_only | limited_retention | full_access",
    "privacy_policy_url": "https://example.com/privacy"
  },

  "signature": {
    "algorithm": "RS256",
    "verification_method": "legal_rep_phone",
    "signed_at": "2026-05-18T00:00:00Z",
    "value": "base64-encoded-signature"
  }
}
```

> 完整 Schema 定义: [schema/org-identity.schema.json](schema/org-identity.schema.json)

---

## 架构设计

```
                       ┌──────────────────────────────┐
                       │       OrgIdentityClient       │
                       │       (一行代码入口)            │
                       └─────────────┬────────────────┘
                                     │
          ┌──────────────┬───────────┼───────────┬──────────────┐
          ▼              ▼           ▼           ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Builder  │  │Validator │  │ Verifier  │  │ Exporter │  │  Schema  │
    │ 卡片构造  │  │ 格式校验  │  │ 手机确权  │  │ 多格式导出 │  │ JSON Sch │
    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                        可插拔接口层                               │
    │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
    │  │ SmsProvider│  │SignProvider│  │StoreProvider│  │RuleProvider│ │
    │  │ 短信通道   │  │ 签名算法   │  │ 存储后端    │  │ 校验规则   │ │
    │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
    └──────────────────────────────────────────────────────────────────┘
```

### 确权流程

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ 开发者    │     │  org-identity │     │ 短信服务  │
└────┬─────┘     └──────┬───────┘     └────┬─────┘
     │ 1.输入USCC       │                  │
     │─────────────────►│                  │
     │                  │ 2.查工商信息      │
     │                  │ 返回法人手机(脱敏) │
     │                  │                  │
     │ 3.确认法人手机    │                  │
     │◄─────────────────│                  │
     │ 4.发起验证        │                  │
     │─────────────────►│ 5.发送验证码      │
     │                  │─────────────────►│
     │                  │                  │
     │ 6.输入验证码      │                  │
     │─────────────────►│ 7.校验验证码      │
     │                  │─────────────────►│
     │ 8.签发证书  ◄────│                  │
     │  (签名后的       │                  │
     │   org-identity)  │                  │
```

---

## 项目结构

```
org-identity-sdk/
├── schema/                          # JSON Schema 标准定义
│   └── org-identity.schema.json     # ATH/v1 Schema (JSON Schema 2020-12)
├── src/org_identity/                # Python SDK
│   ├── __init__.py                  # 包入口 + 版本信息
│   ├── client.py                    # 统一客户端（一行代码入口）
│   ├── builder.py                   # 卡片构造器 (Builder 模式)
│   ├── validator.py                 # 格式 + 业务逻辑双重校验
│   ├── verifier.py                  # 法人手机确权 + 会话管理
│   └── exporter.py                  # 多格式导出 (org-id / AgentCard / Summary)
├── docs/
│   └── api_reference.md              # 完整 API 参考手册
├── examples/
│   ├── basic_usage.py                # 基本使用示例
│   └── advanced_usage.py             # 进阶使用示例
├── tests/
│   ├── test_builder.py              # 构造器单元测试
│   └── test_validator.py            # 校验器单元测试
├── pyproject.toml                   # 项目配置
├── LICENSE                          # Apache 2.0
├── CONTRIBUTING.md                  # 贡献指南
└── README.md                        # 本文件
```

---

## 协议规范 · ATH/v1

ATH（Agent Trustworthy Handshake / 智能体可信握手协议）是 `org-identity-sdk` 遵循的身份声明协议。

| 版本 | 状态 | 说明 |
|------|------|------|
| ATH/v1 | 🚧 Draft | 初始版本，与 Google A2A AgentCard 双向兼容 |

### 核心原则

| 原则 | 说明 |
|------|------|
| **身份公开** | 任何 Agent 可公开声明其所属组织 |
| **能力声明** | Agent 必须声明其技能和能力范围 |
| **责任追溯** | 提供真实可用的联系方式 |
| **最小数据** | 只声明必要字段，按需扩展 |
| **可验证性** | 支持数字签名后的防篡改验证 |

---

## 参与贡献

我们以**开放讨论**的姿态推进这个项目。

欢迎通过 Issue / PR 参与：

- 🐛 [提交 Bug](https://gitee.com/lingshuzhuyao/org-identity-sdk/issues)
- 💡 [提出建议](https://gitee.com/lingshuzhuyao/org-identity-sdk/issues)
- 📝 [完善文档](https://gitee.com/lingshuzhuyao/org-identity-sdk/pulls)

贡献指南: [CONTRIBUTING.md](CONTRIBUTING.md)

### 开发者

```bash
# 克隆仓库
git clone https://gitee.com/lingshuzhuyao/org-identity-sdk.git
cd org-identity-sdk

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v
```

---

## 安装后验证

```bash
# 克隆仓库
git clone https://gitee.com/lingshuzhuyao/org-identity-sdk.git
cd org-identity-sdk

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试 (11 个测试用例)
pytest tests/ -v

# 运行基本示例
python examples/basic_usage.py

# 运行进阶示例
python examples/advanced_usage.py
```

---

## API 文档

| 文档 | 说明 |
|------|------|
| [API 参考手册](docs/api_reference.md) | 所有公共类、方法、参数、返回值的完整文档 |
| [基本示例](examples/basic_usage.py) | 30 秒上手：生成卡片 → 校验 → 导出 → 摘要 |
| [进阶示例](examples/advanced_usage.py) | 自定义适配器、批量签发、A2A 对接、生命周期管理 |

---

## 项目状态

| 指标 | 状态 |
|------|------|
| 版本 | v0.1.0 (Alpha) |
| 协议 | ATH/v1 (Draft) |
| Python | 3.9+ |
| 测试 | 11/11 通过 |
| License | Apache 2.0 |

> **ATH/v1 当前为 Draft 状态**。初始版本与 Google A2A AgentCard 双向兼容。欢迎通过 Issue 参与讨论和反馈。

---

## 相关链接

| 资源 | 链接 |
|------|------|
| Gitee 仓库 | https://gitee.com/lingshuzhuyao/org-identity-sdk |
| GitHub 镜像 | https://github.com/lingzhu-ai/org-identity-sdk |
| Schema 定义 | [schema/org-identity.schema.json](schema/org-identity.schema.json) |
| Google A2A 协议 | https://github.com/google/A2A |
| 提交 Bug | https://gitee.com/lingshuzhuyao/org-identity-sdk/issues |
| 贡献指南 | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## License

[Apache 2.0](LICENSE) · © 2026 南京灵枢铸药智能科技有限公司