"""
身份卡片导出器 — 支持多种格式输出

用法:
    exporter = IdentityExporter(card)
    exporter.to_json("card.json")
    exporter.to_agentcard("agentcard.json")     # Google A2A 兼容格式
    exporter.to_signed_card("signed.json")       # 带签名的完整卡片
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


# ── Google AgentCard 字段映射 ───────────────────────────────
_AGENTCARD_MAPPING = {
    "name": ("agent_profile", "name"),
    "description": ("agent_profile", "description"),
    "url": ("agent_profile", "endpoint_url"),
    "version": ("agent_profile", "version"),
    # 扩展映射: capabilities → skills (反向)
}

# capability → AgentCard skill 的转换
def _capabilities_to_skills(caps: list[str]) -> list[dict]:
    return [
        {
            "id": cap.lower().replace(" ", "_"),
            "name": cap,
            "description": cap,
        }
        for cap in caps
    ]


class IdentityExporter:
    """多格式身份卡片导出器。"""

    def __init__(self, card: dict):
        self._card = card

    # ── 完整 JSON ────────────────────────────────────────────
    def to_json(self, path: str | Path | None = None, indent: int = 2) -> str:
        """导出完整的 org-identity JSON。"""
        payload = json.dumps(self._card, indent=indent, ensure_ascii=False)
        if path:
            Path(path).write_text(payload, encoding="utf-8")
        return payload

    def to_dict(self) -> dict:
        """返回字典副本。"""
        return copy.deepcopy(self._card)

    # ── Google A2A AgentCard 兼容格式 ────────────────────────
    def to_agentcard(self, path: str | Path | None = None, indent: int = 2) -> str:
        """导出为 Google A2A AgentCard 兼容格式。

        Google AgentCard 规范:
        https://github.com/google/A2A/blob/main/specification/spec.md

        注: AgentCard 字段是 org-identity 的子集，不会丢失核心语义。
        """
        agent = self._card.get("agent_profile", {})
        acc = self._card.get("accountability", {})

        agentcard = {
            "name": agent.get("name", ""),
            "description": agent.get("description", ""),
            "url": agent.get("endpoint_url", ""),
            "version": agent.get("version", ""),
            "capabilities": {
                "streaming": False,  # 默认值
            },
            "skills": agent.get("skills", []),
            # 将 org-identity 的扩展信息注入到 AgentCard
            "provider": {
                "organization": self._card.get("org_identity", {}).get("legal_name", ""),
                "url": agent.get("endpoint_url", ""),
                "contact": acc.get("contact_email", ""),
                "privacy_contact": acc.get("privacy_contact", ""),
                "data_processing_scope": acc.get("data_processing_scope", ""),
            },
            # org-identity 的原始卡片 ID 作为扩展字段
            "org_identity_card_id": self._card.get("card_id", ""),
        }

        # 如果技能列表为空，从 capabilities 生成
        if not agentcard["skills"]:
            agentcard["skills"] = _capabilities_to_skills(agent.get("capabilities", []))

        payload = json.dumps(agentcard, indent=indent, ensure_ascii=False)
        if path:
            Path(path).write_text(payload, encoding="utf-8")
        return payload

    # ── 带签名的完整卡片 ─────────────────────────────────────
    def to_signed_card(self, path: str | Path | None = None, indent: int = 2) -> str:
        """导出带签名信息的完整卡片。"""
        return self.to_json(path=path, indent=indent)

    # ── 摘要 ─────────────────────────────────────────────────
    def summary(self) -> str:
        """返回人类可读的卡片摘要。"""
        org = self._card.get("org_identity", {})
        agent = self._card.get("agent_profile", {})
        acc = self._card.get("accountability", {})
        sig = self._card.get("signature")

        lines = [
            "═" * 60,
            "Org-Identity 身份卡片摘要",
            "═" * 60,
            f"卡片 ID:      {self._card.get('card_id', 'N/A')}",
            f"协议版本:     {self._card.get('protocol_version', 'N/A')}",
            "",
            "── 组织身份 ──",
            f"名称:         {org.get('legal_name', 'N/A')}",
            f"USCC:         {org.get('uscc', 'N/A')}",
            f"安全等级:     {org.get('security_cert_level', 'N/A')}",
            "",
            "── Agent 信息 ──",
            f"名称:         {agent.get('name', 'N/A')}",
            f"版本:         {agent.get('version', 'N/A')}",
            f"能力:         {', '.join(agent.get('capabilities', [])) or '未声明'}",
            f"端点:         {agent.get('endpoint_url', '未设置')}",
            "",
            "── 责任信息 ──",
            f"责任主体:     {acc.get('responsible_entity', 'N/A')}",
            f"联系方式:     {acc.get('contact_email', 'N/A')}",
            f"数据处理:     {acc.get('data_processing_scope', 'N/A')}",
            "",
            "── 签名状态 ──",
            f"已签名:       {'是' if sig else '否'}",
        ]
        if sig:
            lines.append(f"签名方式:     {sig.get('verification_method', 'N/A')}")
            lines.append(f"签名时间:     {sig.get('verified_at', 'N/A')}")
        lines.append("═" * 60)
        return "\n".join(lines)
