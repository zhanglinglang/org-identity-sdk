"""
身份卡片校验器

用法:
    v = IdentityValidator()
    result = v.validate(card_dict)
    if result.is_valid:
        print("✓ 通过")
    else:
        for err in result.errors:
            print(f"✗ {err}")
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


_SCHEMA_PATH = Path(__file__).parent / "schema" / "org-identity.schema.json"


@dataclass
class ValidationResult:
    """校验结果。"""
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid


class IdentityValidator:
    """基于 JSON Schema 的身份卡片校验器，附带业务逻辑完整性检查。"""

    def __init__(self, schema_path: str | Path | None = None):
        self._schema: dict | None = None
        self._schema_path = schema_path or _SCHEMA_PATH
        if not _HAS_JSONSCHEMA:
            import warnings
            warnings.warn("jsonschema 未安装，仅执行业务逻辑校验。安装: pip install jsonschema")

    def _load_schema(self) -> dict:
        if self._schema is None:
            with open(self._schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)
        return self._schema

    def validate(self, card: dict, strict: bool = True) -> ValidationResult:
        """对一张身份卡片执行完整校验。

        Args:
            card: 身份卡片字典。
            strict: True 时 USCC 格式会做正则校验。

        Returns:
            ValidationResult 对象，可直接当 bool 判断。
        """
        result = ValidationResult()

        # ── 1. JSON Schema 校验 ──
        if _HAS_JSONSCHEMA:
            schema = self._load_schema()
            validator = jsonschema.Draft202012Validator(schema)
            schema_errors = sorted(validator.iter_errors(card), key=lambda e: e.path)
            for err in schema_errors:
                path = " → ".join(str(p) for p in err.path) if err.path else "根"
                result.errors.append(f"[Schema] {path}: {err.message}")
        else:
            result.warnings.append("跳过 JSON Schema 校验 (jsonschema 未安装)")

        # ── 2. 业务逻辑完整性 ──
        biz_errs = self._business_rules(card, strict=strict)
        for e in biz_errs:
            result.errors.append(f"[Business] {e}")

        # ── 3. 文档性警告 ──
        biz_warns = self._best_practices(card)
        result.warnings.extend(f"[Tip] {w}" for w in biz_warns)

        result.is_valid = len(result.errors) == 0
        return result

    def _business_rules(self, card: dict, strict: bool) -> list[str]:
        errs: list[str] = []

        # 有效期检查
        expires = card.get("expires_at", "")
        issued = card.get("issued_at", "")
        if expires and issued and expires <= issued:
            errs.append("expires_at 必须晚于 issued_at")

        # responsible_entity 应与 legal_name 一致 (宽松检查)
        org = card.get("org_identity", {})
        acc = card.get("accountability", {})
        re_entity = acc.get("responsible_entity", "")
        legal_name = org.get("legal_name", "")
        if re_entity and legal_name and re_entity != legal_name:
            errs.append(f"responsible_entity ({re_entity}) 与 org_identity.legal_name ({legal_name}) 不一致")

        # USCC 格式 (严格模式)
        if strict:
            uscc = org.get("uscc", "")
            if uscc:
                import re
                if not re.match(r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$', uscc):
                    errs.append(f"uscc 格式不合法: {uscc}")

        return errs

    def _best_practices(self, card: dict) -> list[str]:
        warns: list[str] = []

        agent = card.get("agent_profile", {})
        caps = agent.get("capabilities", [])
        if not caps:
            warns.append("agent_profile.capabilities 为空，建议至少声明一个能力")

        skills = agent.get("skills", [])
        if not skills:
            warns.append("agent_profile.skills 为空，建议声明技能列表以增强可发现性")

        acc = card.get("accountability", {})
        if not acc.get("contact_person"):
            warns.append("建议填写 accountability.contact_person")

        if not card.get("signature"):
            warns.append("卡片未签名，建议完成确权验证后添加签名")

        return warns
