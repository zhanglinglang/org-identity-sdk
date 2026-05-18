"""
统一客户端 — 一行代码完成所有操作

用法:
    from org_identity import OrgIdentityClient

    client = OrgIdentityClient()

    # 生成身份卡片
    card = client.generate_identity_card(
        uscc="91110108MA01XXXXXX",
        legal_name="南京灵枢铸药智能科技有限公司",
        agent_name="医药研发助手",
        agent_version="1.0.0",
        agent_description="专注于药物研发领域的智能体",
        contact_phone="+8613800138000",
        contact_email="admin@lingshuyaozhi.com",
    )

    # 发起确权
    session = client.init_verification(uscc="91110108MA01XXXXXX", phone="+8613800138000")

    # 确认验证码并签名
    signed = client.verify_and_sign(card, session.session_id, code="123456")
"""

from __future__ import annotations

from pathlib import Path

from .builder import IdentityBuilder
from .validator import IdentityValidator, ValidationResult
from .exporter import IdentityExporter
from .verifier import PhoneVerifier, SmsProvider, VerificationResult


class OrgIdentityClient:
    """org-identity SDK 统一入口。

    封装 Builder / Validator / Exporter / Verifier 四大模块，
    提供一行代码即可完成身份卡片生命周期管理的能力。
    """

    def __init__(self, sms_provider: SmsProvider | None = None, schema_path: str | Path | None = None):
        self._verifier = PhoneVerifier(sms_provider=sms_provider)
        self._validator = IdentityValidator(schema_path=schema_path)

    # ── 生成卡片 ─────────────────────────────────────────────
    def generate_identity_card(
        self,
        uscc: str,
        legal_name: str,
        agent_name: str,
        agent_version: str,
        agent_description: str,
        **kwargs,
    ) -> dict:
        """一行生成符合 ATH/v1 协议的身份卡片。

        Args:
            uscc: 统一社会信用代码。
            legal_name: 法人实体全称。
            agent_name: Agent 名称。
            agent_version: Agent 版本号 (语义化版本)。
            agent_description: Agent 功能描述。

        Keyword Args (all optional):
            short_name, agent_registration_id, security_cert_level,
            registered_address, business_scope,
            capabilities, endpoint_url, input_modes, output_modes, skills,
            responsible_entity, contact_person, contact_phone, contact_email,
            privacy_contact, data_processing_scope, data_retention_policy,
            expiry_days.

        Returns:
            完整的身份卡片字典。
        """
        builder = IdentityBuilder()

        # 组织身份
        builder.set_org(
            uscc=uscc,
            legal_name=legal_name,
            short_name=kwargs.get("short_name", ""),
            agent_registration_id=kwargs.get("agent_registration_id", ""),
            security_cert_level=kwargs.get("security_cert_level", "L1"),
            registered_address=kwargs.get("registered_address", ""),
            business_scope=kwargs.get("business_scope", ""),
        )

        # Agent 描述
        builder.set_agent(
            name=agent_name,
            version=agent_version,
            description=agent_description,
            capabilities=kwargs.get("capabilities", []),
            endpoint_url=kwargs.get("endpoint_url", ""),
            input_modes=kwargs.get("input_modes", ["text"]),
            output_modes=kwargs.get("output_modes", ["text"]),
            skills=kwargs.get("skills", []),
        )

        # 责任追溯
        builder.set_accountability(
            responsible_entity=kwargs.get("responsible_entity", ""),
            contact_person=kwargs.get("contact_person", ""),
            contact_phone=kwargs.get("contact_phone", ""),
            contact_email=kwargs.get("contact_email", ""),
            privacy_contact=kwargs.get("privacy_contact", ""),
            data_processing_scope=kwargs.get("data_processing_scope", "conversation_only"),
            data_retention_policy=kwargs.get("data_retention_policy", ""),
        )

        # 有效期
        expiry_days = kwargs.get("expiry_days", 180)
        builder.set_expiry(days=expiry_days)

        return builder.build()

    # ── 校验 ─────────────────────────────────────────────────
    def validate(self, card: dict, strict: bool = True) -> ValidationResult:
        """校验身份卡片。

        Args:
            card: 身份卡片字典。
            strict: 严格模式（校验 USCC 格式）。

        Returns:
            ValidationResult (可直接当 bool 判断)。
        """
        return self._validator.validate(card, strict=strict)

    # ── 确权 & 签名 ──────────────────────────────────────────
    def init_verification(self, uscc: str, phone: str) -> VerificationResult:
        """发起法人手机确权验证。

        Args:
            uscc: 统一社会信用代码。
            phone: 法人手机号。

        Returns:
            VerificationResult (verified=False, 携带 session_id)。
        """
        return self._verifier.init_verification(uscc, phone)

    def confirm_verification(self, session_id: str, code: str) -> VerificationResult:
        """确认手机验证码。

        Args:
            session_id: init_verification 返回的会话 ID。
            code: 6 位验证码。

        Returns:
            VerificationResult (verified=True 表示通过)。
        """
        return self._verifier.confirm(session_id, code)

    def sign_card(self, card: dict, session_id: str, private_key_pem: str = "") -> dict:
        """对已确权的卡片进行数字签名。

        Args:
            card: 身份卡片字典。
            session_id: 完成确权的会话 ID。
            private_key_pem: 签名私钥（PEM 格式，为空使用占位签名）。

        Returns:
            带签名的卡片字典。
        """
        return self._verifier.sign_card(card, session_id, private_key_pem)

    def verify_and_sign(self, card: dict, session_id: str, code: str, private_key_pem: str = "") -> dict:
        """确认验证码并对卡片签名（一步完成）。"""
        result = self.confirm_verification(session_id, code)
        if not result.verified:
            raise ValueError(f"确权失败: {result.message}")
        return self.sign_card(card, session_id, private_key_pem)

    # ── 导出 ─────────────────────────────────────────────────
    def export(self, card: dict) -> IdentityExporter:
        """获取导出器实例。

        Returns:
            IdentityExporter: 支持 to_json / to_agentcard / to_signed_card / summary。
        """
        return IdentityExporter(card)
