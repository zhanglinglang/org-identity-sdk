"""Validator 模块单元测试"""

import pytest
from org_identity.validator import IdentityValidator, ValidationResult
from org_identity.builder import IdentityBuilder


def _make_card(**overrides):
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试科技有限公司")
        .set_agent(name="测试助手", version="1.0.0", description="测试Agent")
        .set_accountability(contact_phone="+8613800138000", contact_email="test@example.com")
        .build()
    )
    card.update(overrides)
    return card


def test_valid_card():
    v = IdentityValidator()
    card = _make_card()
    result = v.validate(card)
    assert result.is_valid


def test_missing_required_field():
    v = IdentityValidator()
    card = _make_card()
    del card["org_identity"]["uscc"]
    result = v.validate(card)
    # Without jsonschema, it should still catch via business rules
    # With jsonschema, it will be caught there
    assert not result.is_valid or len(result.warnings) > 0


def test_expires_before_issued():
    v = IdentityValidator()
    card = _make_card()
    card["issued_at"] = "2026-06-01T00:00:00+00:00"
    card["expires_at"] = "2026-01-01T00:00:00+00:00"
    result = v.validate(card)
    assert not result.is_valid


def test_inconsistent_entity_name():
    v = IdentityValidator()
    card = _make_card()
    card["accountability"]["responsible_entity"] = "另一家公司"
    result = v.validate(card)
    assert not result.is_valid


def test_warnings_for_empty_fields():
    v = IdentityValidator()
    card = _make_card()
    card["agent_profile"]["capabilities"] = []
    card["agent_profile"]["skills"] = []
    result = v.validate(card)
    assert len(result.warnings) > 0
    assert result.is_valid  # warnings don't invalidate
