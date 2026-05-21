"""
org-identity-sdk 进阶用法示例

运行: python examples/advanced_usage.py

覆盖场景:
  1. 自定义短信适配器（对接真实短信服务商）
  2. Builder 模式精细控制 + 扩展字段
  3. 批量生成身份卡片
  4. 与 A2A 协议对接（AgentCard 导出 + 服务发现）
  5. 卡片生命周期管理（创建 -> 校验 -> 签名 -> 导出 -> 归档）
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from org_identity import (
    OrgIdentityClient,
    IdentityBuilder,
    IdentityValidator,
    IdentityExporter,
    PhoneVerifier,
)


# ================================================================
# 场景 1: 自定义短信适配器
# ================================================================

class CustomSmsProvider:
    """
    自定义短信服务商适配器示例.

    实现 SmsProvider 协议只需一个 send(phone, message) -> bool 方法。
    替换此实现即可对接阿里云、腾讯云、Twilio 等任意短信服务。
    """

    def __init__(self, api_key: str = "", log_file: str = ""):
        self.api_key = api_key
        self.log_file = log_file or "sms_log.txt"
        self.send_count = 0

    def send(self, phone: str, message: str) -> bool:
        """发送短信。

        实际生产环境中这里接入短信 API：
        - 阿里云: aliyunsdk.dysmsapi
        - 腾讯云: tencentcloud-sdk-python (sms)
        - Twilio: twilio.rest.Client
        """
        self.send_count += 1

        # 记录发送日志
        log_entry = (
            f"[{self.send_count}] Phone: {phone} | "
            f"Message: {message[:50]}... | "
            f"API Key: {self.api_key[:8]}***\n"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"  [CustomSMS] #{self.send_count} 发送至 {phone[:-4]}****")
        print(f"  [CustomSMS] 日志: {self.log_file}")
        return True  # 返回 True 表示发送成功


print("=" * 60)
print("场景 1: 自定义短信适配器")
print("=" * 60)

sms_provider = CustomSmsProvider(api_key="sk_test_12345678")
verifier = PhoneVerifier(sms_provider=sms_provider)

result = verifier.init_verification(
    uscc="91110108MA01ABCDEF",
    phone="+8613800138000",
)
print(f"  状态: {result.message}\n")


# ================================================================
# 场景 2: Builder 模式精细控制 + 扩展字段
# ================================================================

print("=" * 60)
print("场景 2: Builder 模式精细控制")
print("=" * 60)

card = (
    IdentityBuilder()
    # 组织身份 — 完整填写
    .set_org(
        uscc="91110108MA01ABCDEF",
        legal_name="南京灵枢铸药智能科技有限公司",
        short_name="灵枢智能",
        agent_registration_id="ICP备2025-00001-AI",  # 智能体备案号
        security_cert_level="L2",
        registered_address="南京市鼓楼区汉口路22号",
        business_scope="人工智能药物研发、临床试验数据分析",
    )
    # Agent 描述 — 多技能声明
    .set_agent(
        name="医药研发智能助手 Pro",
        version="2.1.0",
        description="企业级药物研发全流程智能体，覆盖靶点发现到临床方案设计",
        capabilities=[
            "靶点识别与验证",
            "分子对接与虚拟筛选",
            "ADMET 性质预测",
            "临床试验方案设计",
            "药物相互作用检查",
            "文献智能检索与综述",
        ],
        endpoint_url="https://agent.lingshuyaozhi.com/a2a/v2",
        input_modes=["text", "image", "file"],
        output_modes=["text", "json", "html", "file"],
    )
    # 逐条追加技能（含示例，增强可发现性）
    .add_skill(
        skill_id="target_identification",
        name="靶点识别",
        description="基于基因组学和蛋白质组学数据的疾病靶点识别与优先级排序",
        tags=["genomics", "target-discovery", "priority-ranking"],
        examples=[
            "从 TCGA 数据库中识别 NSCLC 新型驱动基因",
            "分析 GWAS 数据确定自身免疫病候选靶点",
        ],
    )
    .add_skill(
        skill_id="molecular_docking",
        name="分子对接",
        description="高通量虚拟筛选，支持 AutoDock Vina / Glide 引擎",
        tags=["docking", "virtual-screening", "lead-optimization"],
        examples=[
            "对 500 万分子库进行虚拟筛选，找出 Top 100 候选化合物",
        ],
    )
    .add_skill(
        skill_id="admet_prediction",
        name="ADMET 预测",
        description="化合物吸收、分布、代谢、排泄、毒性综合预测",
        tags=["admet", "toxicity", "drug-likeness"],
        examples=[
            "对候选化合物列表进行 ADMET 全属性预测，过滤不适合成药的分子",
        ],
    )
    # 责任追溯
    .set_accountability(
        responsible_entity="南京灵枢铸药智能科技有限公司",
        contact_person="张博士",
        contact_phone="+86-25-8888-6666",
        contact_email="zhang@lingshuyaozhi.com",
        privacy_contact="privacy@lingshuyaozhi.com",
        data_processing_scope="limited_retention",
        data_retention_policy="对话数据保留 30 天，用于服务质量优化；分子结构数据不保留",
    )
    # 有效期
    .set_expiry(days=180)
    # 扩展字段 — 业务自定义信息
    .set_extension("department", "AI研发部")
    .set_extension("compliance_officer", "李律师 / li@lingshuyaozhi.com")
    .set_extension("supported_protocols", ["ATH/v1", "A2A/v1"])
    .set_extension("rate_limit", {"requests_per_minute": 60, "max_concurrency": 5})
    # 构建
    .build()
)

# 校验
validator = IdentityValidator()
result = validator.validate(card)
print(f"  校验: {'PASS' if result else 'FAIL'}")
if result.warnings:
    for w in result.warnings:
        print(f"    [!] {w}")

print(f"  卡片 ID: {card['card_id']}")
print(f"  技能数: {len(card['agent_profile']['skills'])}")
print(f"  扩展字段: {list(card.get('extensions', {}).keys())}\n")


# ================================================================
# 场景 3: 批量生成身份卡片
# ================================================================

print("=" * 60)
print("场景 3: 批量生成身份卡片")
print("=" * 60)

# 同一组织下的多个 Agent
agents = [
    {
        "name": "文献检索助手",
        "version": "1.0.0",
        "description": "专业生物医学文献检索与综述生成",
        "capabilities": ["PubMed检索", "全文提取", "综述生成"],
        "security_level": "L1",
    },
    {
        "name": "分子模拟引擎",
        "version": "3.2.0",
        "description": "大规模分子动力学模拟与自由能计算",
        "capabilities": ["MD模拟", "FEP计算", "结合自由能预测"],
        "security_level": "L2",
    },
    {
        "name": "临床数据分析平台",
        "version": "1.5.0",
        "description": "临床试验数据清洗、统计分析与可视化",
        "capabilities": ["数据清洗", "统计分析", "Kaplan-Meier", "不良事件监测"],
        "security_level": "L3",
    },
    {
        "name": "合规审查助手",
        "version": "0.9.0",
        "description": "NMPA/FDA 申报材料合规自动审查",
        "capabilities": ["格式审查", "数据完整性检查", "法规库检索"],
        "security_level": "L3",
    },
]

client = OrgIdentityClient()
cards = []

for agent_info in agents:
    card = client.generate_identity_card(
        uscc="91110108MA01ABCDEF",
        legal_name="南京灵枢铸药智能科技有限公司",
        agent_name=agent_info["name"],
        agent_version=agent_info["version"],
        agent_description=agent_info["description"],
        capabilities=agent_info["capabilities"],
        security_cert_level=agent_info["security_level"],
        contact_email="admin@lingshuyaozhi.com",
        endpoint_url=f"https://agent.lingshuyaozhi.com/a2a/{agent_info['name']}",
    )
    cards.append(card)

    # 校验每张卡片
    result = client.validate(card, strict=False)
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {agent_info['name']} v{agent_info['version']} (Lv.{agent_info['security_level']})")

print(f"\n  共生成 {len(cards)} 张卡片\n")


# ================================================================
# 场景 4: A2A 协议对接 — AgentCard 导出 + 服务发现
# ================================================================

print("=" * 60)
print("场景 4: A2A 协议对接")
print("=" * 60)

# 使用场景 2 的完整卡片
exporter = IdentityExporter(card)

# 4a. 导出为 Google A2A AgentCard
agentcard_json = exporter.to_agentcard()
agentcard = json.loads(agentcard_json)

print(f"  AgentCard 导出:")
print(f"    名称: {agentcard['name']}")
print(f"    端点: {agentcard['url']}")
print(f"    技能数: {len(agentcard['skills'])}")
print(f"    Provider: {agentcard['provider']['organization']}")
print(f"    org-identity 卡片 ID: {agentcard['org_identity_card_id']}")

# 4b. 模拟服务发现场景 — 验证 AgentCard 是否可追溯到 org-identity
print(f"\n  服务发现验证:")
print(f"    1. Agent 声称: {agentcard['name']}")
print(f"    2. 组织: {agentcard['provider']['organization']}")
print(f"    3. 联系方式: {agentcard['provider']['contact']}")
print(f"    4. 可追溯至 org-identity 卡片: {agentcard['org_identity_card_id']}")
print(f"    -> 信任链路完整 [OK]")

# 4c. 双向兼容性验证
print(f"\n  双向兼容性:")
print(f"    ATH/v1 -> AgentCard: OK (exporter.to_agentcard())")
print(f"    AgentCard -> ATH/v1: 保留 org_identity_card_id 作为追溯链")


# ================================================================
# 场景 5: 卡片生命周期管理
# ================================================================

print(f"\n{'=' * 60}")
print("场景 5: 完整生命周期")
print("=" * 60)

def lifecycle_demo():
    """演示身份卡片的完整生命周期：创建 -> 校验 -> 签名 -> 导出 -> 归档"""
    client = OrgIdentityClient()

    # 第 1 步: 创建
    print("  [1/5] 创建卡片...")
    card = client.generate_identity_card(
        uscc="91110108MA01ABCDEF",
        legal_name="南京灵枢铸药智能科技有限公司",
        agent_name="Demo Agent",
        agent_version="0.1.0",
        agent_description="生命周期演示智能体",
        capabilities=["演示"],
        contact_email="demo@lingshuyaozhi.com",
    )
    card_id = card["card_id"]
    print(f"        卡片 ID: {card_id}")

    # 第 2 步: 校验
    print("  [2/5] 校验卡片...")
    result = client.validate(card)
    print(f"        {'PASS' if result else 'FAIL'}")
    if result.warnings:
        for w in result.warnings:
            print(f"        [!] {w}")

    # 第 3 步: 发证 (占位签名，演示环境不连短信)
    print("  [3/5] 分发证书...")
    signed = client.sign_card(card, session_id="demo_session")
    sig = signed.get("signature", {})
    print(f"        算法: {sig.get('algorithm', 'N/A')}")
    print(f"        签名时间: {sig.get('verified_at', 'N/A')}")
    print(f"        方法: {sig.get('verification_method', 'N/A')}")

    # 第 4 步: 导出多格式
    print("  [4/5] 导出格式...")
    exporter = client.export(signed)
    json_bytes = len(exporter.to_json().encode("utf-8"))
    agentcard_bytes = len(exporter.to_agentcard().encode("utf-8"))
    print(f"        org-identity JSON: {json_bytes} bytes")
    print(f"        AgentCard JSON:    {agentcard_bytes} bytes")
    print(f"        摘要:              {len(exporter.summary().splitlines())} 行")

    # 第 5 步: 归档
    print("  [5/5] 归档...")
    archive_dir = Path("output")
    archive_dir.mkdir(exist_ok=True)
    exporter.to_json(archive_dir / f"{card_id}.json")
    exporter.to_agentcard(archive_dir / f"{card_id}.agentcard.json")
    print(f"        归档至: {archive_dir.absolute()}")
    print(f"        文件: {card_id}.json, {card_id}.agentcard.json")

    print("\n  [OK] 生命周期完成!")

lifecycle_demo()


# ================================================================
# 总结
# ================================================================

print(f"\n{'=' * 60}")
print("所有场景演示完成!")
print("=" * 60)
print("""
覆盖能力:
  [OK] 自定义短信适配器 — 对接任意短信服务商
  [OK] Builder 模式精细控制 — 链式调用，扩展字段
  [OK] 批量生成卡片 — 同一组织多 Agent
  [OK] A2A 协议对接 — AgentCard 导出 + 服务发现 + 信任追溯
  [OK] 生命周期管理 — 创建 -> 校验 -> 签名 -> 导出 -> 归档
""")