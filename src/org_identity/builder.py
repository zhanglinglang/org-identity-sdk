"""
身份卡片构造器 (Builder Pattern)

用法:
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01XXXXXX", legal_name="某某科技有限公司")
        .set_agent(name="客服助手", version="1.0.0", description="智能客服Agent")
        .set_accountability(contact_phone="+8613800138000", contact_email="admin@example.com")
        .build()
    )
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any


class IdentityBuilder:
    """一步一链式构造 org-identity 身份卡片。"""

    def __init__(self):
        self._data: dict[str, Any] = {
            "protocol_version": "ATH/v1",
            "card_id": str(uuid.uuid4()),
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=180)).isoformat(),
            "org_identity": {},
            "agent_profile": {},
            "accountability": {},
        }

    # ── 组织身份 ─────────────────────────────────────────────
    def set_org(
        self,
        uscc: str,
        legal_name: str,
        short_name: str = "",
        agent_registration_id: str = "",
        security_cert_level: str = "L1",
        registered_address: str = "",
        business_scope: str = "",
    ) -> "IdentityBuilder":
        self._data["org_identity"] = {
            "uscc": uscc,
            "legal_name": legal_name,
            "short_name": short_name,
            "agent_registration_id": agent_registration_id,
            "security_cert_level": security_cert_level,
            "registered_address": registered_address,
            "business_scope": business_scope,
        }
        return self

    # ── Agent 描述 ───────────────────────────────────────────
    def set_agent(
        self,
        name: str,
        version: str,
        description: str,
        capabilities: list[str] | None = None,
        endpoint_url: str = "",
        input_modes: list[str] | None = None,
        output_modes: list[str] | None = None,
        skills: list[dict[str, Any]] | None = None,
    ) -> "IdentityBuilder":
        self._data["agent_profile"] = {
            "name": name,
            "version": version,
            "description": description,
            "capabilities": capabilities or [],
            "endpoint_url": endpoint_url,
            "input_modes": input_modes or ["text"],
            "output_modes": output_modes or ["text"],
            "skills": skills or [],
        }
        return self

    def add_skill(self, skill_id: str, name: str, description: str, tags: list[str] | None = None, examples: list[str] | None = None) -> "IdentityBuilder":
        """向 agent_profile 追加一个技能声明。"""
        self._data["agent_profile"].setdefault("skills", []).append({
            "id": skill_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "examples": examples or [],
        })
        return self

    def add_capability(self, capability: str) -> "IdentityBuilder":
        """追加一个能力标签。"""
        self._data["agent_profile"].setdefault("capabilities", []).append(capability)
        return self

    # ── 责任追溯 ─────────────────────────────────────────────
    def set_accountability(
        self,
        responsible_entity: str = "",
        contact_person: str = "",
        contact_phone: str = "",
        contact_email: str = "",
        privacy_contact: str = "",
        data_processing_scope: str = "conversation_only",
        data_retention_policy: str = "",
    ) -> "IdentityBuilder":
        self._data["accountability"] = {
            "responsible_entity": responsible_entity or self._data["org_identity"].get("legal_name", ""),
            "contact_person": contact_person,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "privacy_contact": privacy_contact,
            "data_processing_scope": data_processing_scope,
            "data_retention_policy": data_retention_policy,
        }
        return self

    # ── 有效期 ───────────────────────────────────────────────
    def set_expiry(self, days: int = 180) -> "IdentityBuilder":
        """设置卡片有效期（天），默认 180 天。"""
        self._data["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        return self

    def set_expiry_date(self, dt: datetime) -> "IdentityBuilder":
        """直接指定过期时间。"""
        self._data["expires_at"] = dt.isoformat()
        return self

    # ── 扩展 ─────────────────────────────────────────────────
    def set_extension(self, key: str, value: Any) -> "IdentityBuilder":
        """设置扩展字段。"""
        self._data.setdefault("extensions", {})[key] = value
        return self

    # ── 构建 ─────────────────────────────────────────────────
    def build(self) -> dict[str, Any]:
        """返回完整的身份卡片字典。"""
        return self._data

    def build_json(self, indent: int = 2) -> str:
        """返回格式化的 JSON 字符串。"""
        import json as _json
        return _json.dumps(self._data, indent=indent, ensure_ascii=False)
