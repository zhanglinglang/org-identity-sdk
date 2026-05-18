"""Builder 模块单元测试"""

import pytest
from org_identity.builder import IdentityBuilder


def test_build_minimal():
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试科技有限公司")
        .set_agent(name="测试助手", version="1.0.0", description="一个测试Agent")
        .set_accountability(contact_phone="+8613800138000", contact_email="test@example.com")
        .build()
    )
    assert card["protocol_version"] == "ATH/v1"
    assert card["org_identity"]["uscc"] == "91110108MA01ABCDEF"
    assert card["org_identity"]["legal_name"] == "测试科技有限公司"
    assert card["agent_profile"]["name"] == "测试助手"
    assert card["agent_profile"]["version"] == "1.0.0"
    assert card["accountability"]["contact_email"] == "test@example.com"


def test_card_has_id_and_timestamps():
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试")
        .set_agent(name="A", version="1.0.0", description="d")
        .set_accountability(contact_phone="+8613800138000", contact_email="e@t.com")
        .build()
    )
    assert "card_id" in card
    assert "issued_at" in card
    assert "expires_at" in card
    assert len(card["card_id"]) == 36  # UUID4


def test_add_skill():
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试")
        .set_agent(name="A", version="1.0.0", description="d")
        .add_skill("search", "搜索", "搜索能力", tags=["search"], examples=["search: python"])
        .set_accountability(contact_phone="+8613800138000", contact_email="e@t.com")
        .build()
    )
    assert len(card["agent_profile"]["skills"]) == 1
    assert card["agent_profile"]["skills"][0]["id"] == "search"


def test_add_capability():
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试")
        .set_agent(name="A", version="1.0.0", description="d", capabilities=["chat"])
        .add_capability("search")
        .set_accountability(contact_phone="+8613800138000", contact_email="e@t.com")
        .build()
    )
    assert "chat" in card["agent_profile"]["capabilities"]
    assert "search" in card["agent_profile"]["capabilities"]


def test_set_expiry():
    card = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试")
        .set_agent(name="A", version="1.0.0", description="d")
        .set_accountability(contact_phone="+8613800138000", contact_email="e@t.com")
        .set_expiry(days=365)
        .build()
    )
    import datetime
    issued = datetime.datetime.fromisoformat(card["issued_at"])
    expires = datetime.datetime.fromisoformat(card["expires_at"])
    delta = (expires - issued).days
    assert delta == 365


def test_build_json():
    builder = (
        IdentityBuilder()
        .set_org(uscc="91110108MA01ABCDEF", legal_name="测试")
        .set_agent(name="A", version="1.0.0", description="d")
        .set_accountability(contact_phone="+8613800138000", contact_email="e@t.com")
    )
    json_str = builder.build_json()
    assert '"protocol_version"' in json_str
    assert '"ATH/v1"' in json_str
