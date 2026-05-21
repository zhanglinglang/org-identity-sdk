# org-identity-sdk API 参考手册

> **版本**: 0.1.0 · **协议**: ATH/v1 · **Python**: 3.9+

---

## 目录

- [快速导航](#快速导航)
- [OrgIdentityClient](#orgidentityclient) — 统一入口
- [IdentityBuilder](#identitybuilder) — 卡片构造器
- [IdentityValidator](#identityvalidator) — 校验器
- [IdentityExporter](#identityexporter) — 导出器
- [PhoneVerifier](#phoneverifier) — 确权验证器
- [数据结构](#数据结构)
  - [ValidationResult](#validationresult)
  - [VerificationResult](#verificationresult)
  - [VerificationSession](#verificationsession)
- [可插拔接口](#可插拔接口)
  - [SmsProvider (Protocol)](#smsprovider-protocol)
  - [ConsoleSmsProvider](#consolesmsprovider)

---

## 快速导航

```python
# 所有公共 API 均可从顶层包直接导入
from org_identity import (
    OrgIdentityClient,   # 一行代码入口，推荐首选
    IdentityBuilder,     # 链式构造器，精细控制
    IdentityValidator,   # 格式 + 业务逻辑校验
    IdentityExporter,    # 多格式导出（JSON / AgentCard / 摘要）
    PhoneVerifier,       # 法人手机确权 + 签名
)
```

| 场景 | 推荐入口 |
|------|----------|
| 快速生成 + 校验一张卡片 | [`OrgIdentityClient`](#orgidentityclient) |
| 需要链式调用的精细控制 | [`IdentityBuilder`](#identitybuilder) |
| 只想校验已有卡片 | [`IdentityValidator`](#identityvalidator) |
| 对接 A2A 协议导出 | [`IdentityExporter`](#identityexporter) |
| 自定义短信通道 | [`SmsProvider`](#smsprovider-protocol) |

---

## OrgIdentityClient

**统一客户端，封装 Builder / Validator / Exporter / Verifier 四大模块。**
一行代码即可完成身份卡片的生命周期管理。

### 导入

```python
from org_identity import OrgIdentityClient
```

### 构造方法

```python
client = OrgIdentityClient(
    sms_provider: SmsProvider | None = None,   # 自定义短信适配器，默认 ConsoleSmsProvider
    schema_path: str | Path | None = None,     # 自定义 Schema 路径，默认使用内置 Schema
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sms_provider` | `SmsProvider \| None` | `None` | 短信发送适配器。传入自定义实现可对接任意短信服务商。 |
| `schema_path` | `str \| Path \| None` | `None` | JSON Schema 文件路径，默认使用 `src/org_identity/schema/org-identity.schema.json`。 |

---

### generate_identity_card()

**一行生成符合 ATH/v1 协议的身份卡片。**

```python
card: dict = client.generate_identity_card(
    uscc,               # str — 统一社会信用代码（必填）
    legal_name,         # str — 法人实体全称（必填）
    agent_name,         # str — Agent 名称（必填）
    agent_version,      # str — Agent 版本号，语义化版本（必填）
    agent_description,  # str — Agent 功能描述（必填）
    **kwargs,           # 以下均为可选关键字参数
)
```

#### 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `uscc` | `str` | 统一社会信用代码，18 位。如 `"91110108MA01ABCDEF"` |
| `legal_name` | `str` | 法人实体全称。如 `"南京灵枢铸药智能科技有限公司"` |
| `agent_name` | `str` | Agent 名称。如 `"医药研发智能助手"` |
| `agent_version` | `str` | 版本号，建议语义化版本。如 `"1.0.0"` |
| `agent_description` | `str` | Agent 功能描述。如 `"专注于药物分子筛选与临床试验数据挖掘的智能体"` |

#### 可选关键字参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `short_name` | `str` | `""` | 组织简称 |
| `agent_registration_id` | `str` | `""` | 智能体备案号 |
| `security_cert_level` | `str` | `"L1"` | 安全等级认证：`"L1"`, `"L2"`, `"L3"` |
| `registered_address` | `str` | `""` | 注册地址 |
| `business_scope` | `str` | `""` | 经营范围 |
| `capabilities` | `list[str]` | `[]` | Agent 能力标签列表 |
| `endpoint_url` | `str` | `""` | Agent 服务端点 URL |
| `input_modes` | `list[str]` | `["text"]` | 支持的输入模式 |
| `output_modes` | `list[str]` | `["text"]` | 支持的输出模式 |
| `skills` | `list[dict]` | `[]` | 技能声明列表 |
| `responsible_entity` | `str` | `""` | 责任主体名称（默认同 legal_name） |
| `contact_person` | `str` | `""` | 联系人姓名 |
| `contact_phone` | `str` | `""` | 联系电话（建议 E.164 格式） |
| `contact_email` | `str` | `""` | 联系邮箱 |
| `privacy_contact` | `str` | `""` | 数据隐私联系人 |
| `data_processing_scope` | `str` | `"conversation_only"` | 数据处理范围 |
| `data_retention_policy` | `str` | `""` | 数据保留策略说明 |
| `expiry_days` | `int` | `180` | 卡片有效期（天） |

#### 返回值

`dict` — 完整的身份卡片字典，结构见 [身份卡片结构](../README.md#身份卡片结构)。

#### 示例

```python
card = client.generate_identity_card(
    uscc="91110108MA01ABCDEF",
    legal_name="南京灵枢铸药智能科技有限公司",
    agent_name="医药研发智能助手",
    agent_version="1.0.0",
    agent_description="专注于药物分子筛选与临床试验数据挖掘的智能体",
    capabilities=["文献检索", "分子对接", "临床试验分析"],
    endpoint_url="https://agent.lingshuyaozhi.com/a2a",
    contact_phone="+8613800138000",
    contact_email="admin@lingshuyaozhi.com",
    data_processing_scope="conversation_only",
    security_cert_level="L2",
)
```

---

### validate()

**校验身份卡片（JSON Schema + 业务逻辑）。**

```python
result: ValidationResult = client.validate(
    card,           # dict — 身份卡片字典
    strict=True,    # bool — 是否严格模式（校验 USCC 格式）
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `card` | `dict` | — | 身份卡片字典 |
| `strict` | `bool` | `True` | 严格模式开启时，USCC 格式会做正则校验（18 位格式） |

#### 返回值

[`ValidationResult`](#validationresult) — 可直接当 `bool` 判断：`if result:` 等价于 `if result.is_valid`。

#### 示例

```python
result = client.validate(card)
if result:
    print("校验通过")
else:
    for err in result.errors:
        print(f"错误: {err}")
    for warn in result.warnings:
        print(f"警告: {warn}")
```

---

### init_verification()

**发起法人手机确权验证，发送短信验证码。**

```python
session: VerificationResult = client.init_verification(
    uscc,   # str — 统一社会信用代码
    phone,  # str — 法人手机号（E.164 格式）
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `uscc` | `str` | 统一社会信用代码 |
| `phone` | `str` | 法人手机号，建议 E.164 格式（如 `"+8613800138000"`） |

#### 返回值

[`VerificationResult`](#verificationresult) — `verified=False`，携带 `session_id` 供后续 `confirm_verification()` 使用。

#### 安全限制

- 同一 USCC 在 24 小时内最多发起 3 次验证尝试
- 验证码有效期 5 分钟
- 单次会话最多尝试 5 次

#### 示例

```python
session = client.init_verification(
    uscc="91110108MA01ABCDEF",
    phone="+8613800138000",
)
print(session.message)  # "验证码已发送至 **********8000，5分钟内有效"
```

---

### confirm_verification()

**确认短信验证码。**

```python
result: VerificationResult = client.confirm_verification(
    session_id,  # str — init_verification 返回的会话 ID
    code,        # str — 6 位验证码
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | `str` | 由 `init_verification()` 返回的会话 ID |
| `code` | `str` | 用户收到的 6 位短信验证码 |

#### 返回值

[`VerificationResult`](#verificationresult) — `verified=True` 表示确权成功。

---

### verify_and_sign()

**确认验证码并对卡片签名（一步完成）。**

```python
signed_card: dict = client.verify_and_sign(
    card,              # dict — 身份卡片字典
    session_id,        # str — 会话 ID
    code,              # str — 6 位验证码
    private_key_pem="",# str — PEM 格式私钥（可选）
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `card` | `dict` | — | 待签名的身份卡片 |
| `session_id` | `str` | — | 由 `init_verification()` 返回的会话 ID |
| `code` | `str` | — | 6 位验证码 |
| `private_key_pem` | `str` | `""` | PEM 格式私钥；为空则使用占位签名（开发/测试用） |

#### 返回值

`dict` — 带签名的新卡片（深拷贝，不修改原卡片）。

#### 异常

`ValueError` — 确权失败时抛出，`message` 包含失败原因。

#### 示例

```python
# 发起验证
session = client.init_verification("91110108MA01ABCDEF", "+8613800138000")

# 用户输入验证码后一步完成
code = input("请输入短信验证码: ")
signed_card = client.verify_and_sign(card, session.session_id, code)

# 查看签名信息
print(signed_card["signature"])
# {
#   "algorithm": "RS256",
#   "value": "...",
#   "verified_at": "2026-05-21T...",
#   "verification_method": "legal_rep_phone"
# }
```

---

### sign_card()

**对已确权的卡片进行数字签名（不重新发验证码）。**

```python
signed_card: dict = client.sign_card(
    card,              # dict — 身份卡片字典
    session_id,        # str — 已完成确权的会话 ID
    private_key_pem="",# str — PEM 格式私钥（可选）
)
```

适用于已完成确权但需要重新签名的场景。

---

### export()

**获取多格式导出器实例。**

```python
exporter: IdentityExporter = client.export(card)
```

#### 返回值

[`IdentityExporter`](#identityexporter) — 支持 `.to_json()` / `.to_agentcard()` / `.to_signed_card()` / `.summary()`。

---

## IdentityBuilder

**链式调用构造器，适合需要精细控制卡片字段的场景。**

### 导入

```python
from org_identity import IdentityBuilder
```

### 使用方法

```python
builder = IdentityBuilder()
# 链式调用 .set_xxx() 方法
card = builder.build()
```

---

### set_org()

**设置组织身份信息。**

```python
builder.set_org(
    uscc,                      # str — 统一社会信用代码（必填）
    legal_name,                # str — 法人实体全称（必填）
    short_name="",             # str — 组织简称
    agent_registration_id="",  # str — 智能体备案号
    security_cert_level="L1",  # str — 安全等级: "L1" | "L2" | "L3"
    registered_address="",     # str — 注册地址
    business_scope="",         # str — 经营范围
) -> IdentityBuilder  # 返回自身，支持链式调用
```

---

### set_agent()

**设置 Agent 描述信息。**

```python
builder.set_agent(
    name,                  # str — Agent 名称（必填）
    version,               # str — 版本号（必填）
    description,           # str — 功能描述（必填）
    capabilities=None,     # list[str] | None — 能力标签列表
    endpoint_url="",       # str — 服务端点 URL
    input_modes=None,      # list[str] | None — 输入模式（默认 ["text"]）
    output_modes=None,     # list[str] | None — 输出模式（默认 ["text"]）
    skills=None,           # list[dict] | None — 技能列表
) -> IdentityBuilder
```

---

### add_skill()

**向 agent_profile 追加一个技能声明。**

```python
builder.add_skill(
    skill_id,       # str — 技能唯一标识
    name,           # str — 技能名称
    description,    # str — 技能描述
    tags=None,      # list[str] | None — 标签列表
    examples=None,  # list[str] | None — 示例列表
) -> IdentityBuilder
```

#### 示例

```python
builder.add_skill(
    skill_id="drug_screening",
    name="药物筛选",
    description="基于分子对接算法的候选药物筛选",
    tags=["pharma", "ai"],
    examples=["筛选 100 万分子库中与靶点 XYZ 亲和力最高的候选化合物"],
)
```

---

### add_capability()

**追加一个能力标签。**

```python
builder.add_capability(
    capability,  # str — 能力名称
) -> IdentityBuilder
```

---

### set_accountability()

**设置责任追溯信息。**

```python
builder.set_accountability(
    responsible_entity="",         # str — 责任主体名称
    contact_person="",             # str — 联系人
    contact_phone="",              # str — 联系电话
    contact_email="",              # str — 联系邮箱
    privacy_contact="",            # str — 数据隐私联系人
    data_processing_scope="conversation_only",  # str — 数据处理范围
    data_retention_policy="",      # str — 数据保留策略
) -> IdentityBuilder
```

`data_processing_scope` 可选值：

| 值 | 含义 |
|------|------|
| `"conversation_only"` | 仅处理当前对话数据 |
| `"limited_retention"` | 有限保留（需配合 `data_retention_policy`） |
| `"full_access"` | 完整访问（需声明用途） |

---

### set_expiry()

**设置卡片有效期（天）。**

```python
builder.set_expiry(
    days=180,  # int — 有效天数，从当前时间起算
) -> IdentityBuilder
```

---

### set_expiry_date()

**直接指定过期时间。**

```python
builder.set_expiry_date(
    dt,  # datetime — 过期时间
) -> IdentityBuilder
```

---

### set_extension()

**设置扩展字段，用于添加自定义信息。**

```python
builder.set_extension(
    key,    # str — 扩展键
    value,  # Any — 扩展值
) -> IdentityBuilder
```

所有扩展字段存放在 `card["extensions"]` 字典中。

---

### build()

**返回完整的身份卡片字典。**

```python
card: dict = builder.build()
```

---

### build_json()

**返回格式化的 JSON 字符串。**

```python
json_str: str = builder.build_json(indent=2)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `indent` | `int` | `2` | JSON 缩进空格数 |

---

### Builder 链式调用完整示例

```python
card = (
    IdentityBuilder()
    .set_org(
        uscc="91110108MA01ABCDEF",
        legal_name="南京灵枢铸药智能科技有限公司",
        security_cert_level="L2",
    )
    .set_agent(
        name="医药研发助手",
        version="1.0.0",
        description="专注于药物研发的智能体",
        capabilities=["文献检索", "分子对接"],
        endpoint_url="https://agent.lingshuyaozhi.com/a2a",
    )
    .add_skill(
        skill_id="drug_screening",
        name="药物筛选",
        description="基于分子对接的候选药物筛选",
    )
    .set_accountability(
        contact_phone="+8613800138000",
        contact_email="admin@lingshuyaozhi.com",
        data_processing_scope="conversation_only",
    )
    .set_expiry(days=180)
    .set_extension("department", "AI研发部")
    .build()
)
```

---

## IdentityValidator

**基于 JSON Schema 2020-12 的身份卡片校验器，附带业务逻辑完整性检查。**

### 导入

```python
from org_identity import IdentityValidator
```

### 构造方法

```python
validator = IdentityValidator(
    schema_path: str | Path | None = None,  # 自定义 Schema 路径
)
```

---

### validate()

**对一张身份卡片执行完整校验。**

```python
result: ValidationResult = validator.validate(
    card,          # dict — 身份卡片字典
    strict=True,   # bool — 严格模式
)
```

#### 校验流程

1. **JSON Schema 校验**：对照 `org-identity.schema.json` 进行字段完整性校验
2. **业务逻辑检查**：
   - `expires_at` 必须晚于 `issued_at`
   - `responsible_entity` 应与 `legal_name` 一致
   - 严格模式下校验 USCC 18 位格式
3. **最佳实践提醒**：缺失 `capabilities`、`skills`、`contact_person`、`signature` 时产生警告

#### 返回值

[`ValidationResult`](#validationresult) — 字段见下方。

---

## IdentityExporter

**多格式导出器。由 `OrgIdentityClient.export(card)` 获取实例，也可以直接构造。**

### 导入

```python
from org_identity import IdentityExporter
```

### 构造方法

```python
exporter = IdentityExporter(card)  # dict — 身份卡片字典
```

---

### to_json()

**导出完整的 org-identity JSON。**

```python
json_str: str = exporter.to_json(
    path=None,    # str | Path | None — 可选的文件保存路径
    indent=2,     # int — JSON 缩进
)
```

传入 `path` 时同时写入文件，始终返回 JSON 字符串。

---

### to_dict()

**返回卡片的深拷贝字典。**

```python
card_copy: dict = exporter.to_dict()
```

---

### to_agentcard()

**导出为 Google A2A AgentCard 兼容格式。**

```python
agentcard_str: str = exporter.to_agentcard(
    path=None,    # str | Path | None — 可选的文件保存路径
    indent=2,     # int — JSON 缩进
)
```

导出的 AgentCard JSON 结构：

```json
{
  "name": "...",
  "description": "...",
  "url": "...",
  "version": "...",
  "capabilities": {"streaming": false},
  "skills": [...],
  "provider": {
    "organization": "...",
    "url": "...",
    "contact": "...",
    "privacy_contact": "...",
    "data_processing_scope": "..."
  },
  "org_identity_card_id": "..."
}
```

> **兼容性说明**: AgentCard 字段是 org-identity 的子集，导出不会丢失核心语义。组织身份、备案号、安全等级等国内特有字段通过 `provider` 对象传递。

---

### to_signed_card()

**导出带签名的完整卡片。实际上是 `to_json()` 的别名。**

```python
signed_str: str = exporter.to_signed_card(
    path=None,
    indent=2,
)
```

---

### summary()

**返回人类可读的卡片摘要文本。**

```python
summary_text: str = exporter.summary()
```

输出示例：

```
════════════════════════════════════════
Org-Identity 身份卡片摘要
════════════════════════════════════════
卡片 ID:      a5a9df23-4d5a-410b-...
协议版本:     ATH/v1

── 组织身份 ──
名称:         南京灵枢铸药智能科技有限公司
USCC:         91110108MA01ABCDEF
安全等级:     L1

── Agent 信息 ──
名称:         医药研发智能助手
版本:         1.0.0
能力:         文献检索, 分子对接
端点:         https://agent.lingshuyaozhi.com/a2a

── 责任信息 ──
责任主体:     南京灵枢铸药智能科技有限公司
联系方式:     admin@lingshuyaozhi.com
数据处理:     conversation_only

── 签名状态 ──
已签名:       是
签名方式:     legal_rep_phone
════════════════════════════════════════
```

---

## PhoneVerifier

**法人手机验证码确权。实现 USCC + 法人手机的验证流程。**

### 导入

```python
from org_identity import PhoneVerifier
```

### 构造方法

```python
verifier = PhoneVerifier(
    sms_provider: SmsProvider | None = None,
)
```

---

### init_verification()

**发起确权验证，发送验证码。**

```python
result: VerificationResult = verifier.init_verification(
    uscc,   # str — 统一社会信用代码
    phone,  # str — 法人手机号（E.164 格式）
)
```

#### 安全限制

| 限制项 | 值 |
|--------|-----|
| 单次验证码有效期 | 5 分钟 |
| 单次会话最大尝试次数 | 5 次 |
| 同一 USCC 24h 内最大发起次数 | 3 次 |

---

### confirm()

**确认验证码。**

```python
result: VerificationResult = verifier.confirm(
    session_id,  # str — 会话 ID
    code,        # str — 6 位验证码
)
```

---

### sign_card()

**对通过确权的卡片进行数字签名.**

```python
signed_card: dict = verifier.sign_card(
    card,                # dict — 待签名卡片
    session_id,          # str — 已完成确权的会话 ID
    private_key_pem="",  # str — PEM 格式私钥
)
```

- 传入 `private_key_pem`：使用 RS256 + SHA256 进行真正的数字签名
- 不传 `private_key_pem`：使用占位签名（"PLACEHOLDER_SIGNATURE_" 前缀 + card_id 的 SHA256），适用于开发和测试

---

## 数据结构

### ValidationResult

**校验结果，由 `IdentityValidator.validate()` 返回。**

```python
@dataclass
class ValidationResult:
    is_valid: bool           # 校验是否通过
    errors: list[str]        # 错误列表（Schema + Business）
    warnings: list[str]      # 警告列表（最佳实践提醒）

    def __bool__(self) -> bool:  # 可直接当 bool 使用
        return self.is_valid
```

#### 使用方式

```python
result = validator.validate(card)

# 方式一：bool 判断
if result:
    print("通过")

# 方式二：显式字段
if not result.is_valid:
    for err in result.errors:
        print(f"[ERROR] {err}")
for warn in result.warnings:
    print(f"[WARN] {warn}")
```

---

### VerificationResult

**确权验证结果，由 `PhoneVerifier.init_verification()` / `confirm()` 返回。**

```python
@dataclass
class VerificationResult:
    verified: bool       # 是否确权成功
    message: str         # 人类可读的状态消息
    session_id: str      # 会话 ID（init_verification 成功时返回）
```

---

### VerificationSession

**内部数据结构，通常不直接使用。**

```python
@dataclass
class VerificationSession:
    session_id: str      # 会话 ID
    uscc: str            # 统一社会信用代码
    phone: str           # 法人手机号
    code_hash: str       # 验证码 SHA256 哈希
    created_at: float    # 创建时间戳
    expires_at: float    # 过期时间戳
    attempts: int = 0    # 已尝试次数

    @property
    def is_expired(self) -> bool: ...
```

---

## 可插拔接口

### SmsProvider (Protocol)

**短信发送接口协议。实现此接口即可对接任意短信服务商。**

```python
class SmsProvider(Protocol):
    def send(self, phone: str, message: str) -> bool:
        """发送短信。

        Args:
            phone: 目标手机号（E.164 格式）。
            message: 短信内容。

        Returns:
            True 表示发送成功，False 表示失败。
        """
        ...
```

#### 自定义实现示例

```python
import requests

class AliyunSmsProvider:
    """阿里云短信服务适配器。"""

    def __init__(self, access_key_id: str, access_key_secret: str, sign_name: str):
        self._ak = access_key_id
        self._sk = access_key_secret
        self._sign = sign_name

    def send(self, phone: str, message: str) -> bool:
        # 这里接入阿里云 SDK
        # 示例仅展示接口约定
        try:
            # response = aliyun_sdk.send_sms(
            #     phone_numbers=phone,
            #     sign_name=self._sign,
            #     template_param={"code": extract_code(message)},
            # )
            return True
        except Exception:
            return False

# 使用自定义适配器
verifier = PhoneVerifier(sms_provider=AliyunSmsProvider(...))
# 或
client = OrgIdentityClient(sms_provider=AliyunSmsProvider(...))
```

---

### ConsoleSmsProvider

**开发/演示用的控制台打印适配器（默认实现）。**

```python
class ConsoleSmsProvider:
    def send(self, phone: str, message: str) -> bool:
        """将短信内容打印到控制台（不实际发送）。"""
        ...
```

运行 `examples/basic_usage.py` 时控制台输出示例：

```
==================================================
[短信模拟] 发送至: +8613800138000
[短信模拟] 内容: 【灵枢智能】您的 Agent 身份确权验证码: 984336，
                  5分钟内有效。请勿泄露给他人。
==================================================
```

---

## 协议版本映射

| 导出目标 | 协议 | 方法 |
|----------|------|------|
| 完整 org-identity JSON | ATH/v1 | `exporter.to_json()` |
| Google AgentCard | A2A | `exporter.to_agentcard()` |
| 带签名的 org-identity | ATH/v1 | `exporter.to_signed_card()` |
| 人类可读摘要 | — | `exporter.summary()` |

---

## 相关链接

- [README](../README.md) — 项目概述、定位对比、核心特性
- [Schema 定义](../schema/org-identity.schema.json) — ATH/v1 JSON Schema 2020-12
- [基本示例](../examples/basic_usage.py) — 30 秒上手
- [进阶示例](../examples/advanced_usage.py) — 自定义适配器、批量签发、A2A 对接
- [CONTRIBUTING](../CONTRIBUTING.md) — 贡献指南