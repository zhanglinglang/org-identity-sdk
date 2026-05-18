"""
org-identity-sdk 基本用法示例

运行: python examples/basic_usage.py
"""

import sys
sys.path.insert(0, "src")

from org_identity import OrgIdentityClient


def main():
    client = OrgIdentityClient()

    # ── 1. 生成身份卡片 ──
    print("1. 生成身份卡片...")
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
        security_cert_level="L1",
    )
    card["agent_profile"]["skills"] = [
        {
            "id": "drug_interaction_check",
            "name": "药物相互作用检查",
            "description": "检查多种药物之间的相互作用风险",
            "tags": ["pharma", "safety"],
            "examples": ["检查阿司匹林和布洛芬的相互作用"],
        }
    ]

    # ── 2. 校验 ──
    print("\n2. 校验卡片...")
    result = client.validate(card)
    if result.is_valid:
        print("   [OK] 校验通过")
    for w in result.warnings:
        print(f"   [!] {w}")

    # ── 3. 导出 ──
    print("\n3. 导出格式...")

    exporter = client.export(card)
    print(f"\n--- Org-Identity JSON (前 200 字符) ---")
    print(exporter.to_json()[:200])

    print(f"\n--- Google AgentCard 兼容格式 (前 200 字符) ---")
    print(exporter.to_agentcard()[:200])

    print(f"\n--- 摘要 ---")
    print(exporter.summary())

    # ── 4. 确权验证（演示） ──
    print("\n4. 确权验证流程 (演示)...")
    session = client.init_verification(uscc="91110108MA01ABCDEF", phone="+8613800138000")
    print(f"   {session.message}")

    # 模拟验证码输入 (演示模式验证码打印在控制台)
    # 实际生产环境由用户从短信获取
    if session.session_id:
        # 演示: 这里需要用户输入验证码
        # code = input("请输入验证码: ")
        # signed_card = client.verify_and_sign(card, session.session_id, code)
        print("   (生产环境: 用户输入短信验证码后完成签名)")
        print("   使用: client.verify_and_sign(card, session.session_id, code)")

    print("\n[OK] 示例完成!")


if __name__ == "__main__":
    main()
