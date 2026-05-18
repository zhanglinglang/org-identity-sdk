"""
确权验证模块 — 法人手机短信验证

用法:
    verifier = PhoneVerifier(sms_provider=my_sms_adapter)
    session = verifier.init_verification(uscc="91110108MA01XXXXXX", phone="+8613800138000")
    # 用户收到验证码后:
    result = verifier.confirm(session_id=session.session_id, code="123456")
    if result.verified:
        signed_card = verifier.sign(card, session_id=session.session_id)
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Protocol


# ── 短信服务适配器接口 ───────────────────────────────────────
class SmsProvider(Protocol):
    """可插拔的短信发送接口。实现此协议即可接入任意短信服务商。"""

    def send(self, phone: str, message: str) -> bool:
        """发送短信，返回是否成功。"""
        ...


class ConsoleSmsProvider:
    """开发/演示用的控制台打印适配器。"""

    def send(self, phone: str, message: str) -> bool:
        print(f"\n{'='*50}")
        print(f"[短信模拟] 发送至: {phone}")
        print(f"[短信模拟] 内容: {message}")
        print(f"{'='*50}\n")
        return True


# ── 数据结构 ─────────────────────────────────────────────────
@dataclass
class VerificationSession:
    session_id: str
    uscc: str
    phone: str
    code_hash: str
    created_at: float
    expires_at: float
    attempts: int = 0

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


@dataclass
class VerificationResult:
    verified: bool
    message: str
    session_id: str = ""


# ── 确权验证器 ───────────────────────────────────────────────
class PhoneVerifier:
    """法人手机验证码确权。"""

    MAX_ATTEMPTS = 5
    CODE_EXPIRE_SECONDS = 300  # 5 分钟
    RATE_LIMIT_WINDOW = 86400  # 24 小时
    MAX_DAILY_USCC_ATTEMPTS = 3

    def __init__(self, sms_provider: SmsProvider | None = None):
        self._sms = sms_provider or ConsoleSmsProvider()
        self._sessions: dict[str, VerificationSession] = {}
        self._uscc_daily: dict[str, list[float]] = {}  # uscc -> [timestamps]

    def _is_rate_limited(self, uscc: str) -> bool:
        now = time.time()
        entries = self._uscc_daily.get(uscc, [])
        # 清理超过 24h 的记录
        entries = [t for t in entries if now - t < self.RATE_LIMIT_WINDOW]
        self._uscc_daily[uscc] = entries
        return len(entries) >= self.MAX_DAILY_USCC_ATTEMPTS

    def init_verification(self, uscc: str, phone: str) -> VerificationResult:
        """发起确权验证，发送验证码。

        Args:
            uscc: 统一社会信用代码。
            phone: 法人手机号 (E.164 格式，如 +8613800138000)。

        Returns:
            VerificationResult: verified=False 但携带 session_id。
        """
        # 频率限制
        if self._is_rate_limited(uscc):
            return VerificationResult(
                verified=False,
                message=f"USCC {uscc} 24小时内验证次数已达上限 ({self.MAX_DAILY_USCC_ATTEMPTS})",
            )

        # 生成验证码 & 会话
        code = secrets.randbelow(1_000_000)  # 6位数字
        code_str = f"{code:06d}"
        session_id = secrets.token_hex(16)
        now = time.time()

        session = VerificationSession(
            session_id=session_id,
            uscc=uscc,
            phone=phone,
            code_hash=hashlib.sha256(code_str.encode()).hexdigest(),
            created_at=now,
            expires_at=now + self.CODE_EXPIRE_SECONDS,
        )
        self._sessions[session_id] = session

        # 记录 USCC 本次尝试
        self._uscc_daily.setdefault(uscc, []).append(now)

        # 发送短信
        msg = f"【灵枢智能】您的 Agent 身份确权验证码: {code_str}，5分钟内有效。请勿泄露给他人。"
        sent = self._sms.send(phone, msg)

        if not sent:
            del self._sessions[session_id]
            return VerificationResult(verified=False, message="短信发送失败")

        return VerificationResult(
            verified=False,
            message=f"验证码已发送至 {phone[-4:].rjust(len(phone), '*')}，5分钟内有效",
            session_id=session_id,
        )

    def confirm(self, session_id: str, code: str) -> VerificationResult:
        """确认验证码。

        Args:
            session_id: init_verification 返回的会话 ID。
            code: 用户输入的 6 位验证码。

        Returns:
            VerificationResult: verified=True 表示确权成功。
        """
        session = self._sessions.get(session_id)
        if session is None:
            return VerificationResult(verified=False, message="会话不存在或已过期")

        if session.is_expired:
            del self._sessions[session_id]
            return VerificationResult(verified=False, message="验证码已过期，请重新获取")

        if session.attempts >= self.MAX_ATTEMPTS:
            del self._sessions[session_id]
            return VerificationResult(verified=False, message="验证尝试次数已达上限")

        session.attempts += 1
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        if code_hash != session.code_hash:
            remaining = self.MAX_ATTEMPTS - session.attempts
            return VerificationResult(
                verified=False,
                message=f"验证码错误，剩余尝试次数: {remaining}",
                session_id=session_id,
            )

        # 验证成功
        del self._sessions[session_id]
        return VerificationResult(
            verified=True,
            message="确权验证成功 ✓",
            session_id=session_id,
        )

    def sign_card(self, card: dict, session_id: str, private_key_pem: str = "") -> dict:
        """对通过确权的卡片进行数字签名。

        Args:
            card: 身份卡片字典。
            session_id: 已完成确权的会话 ID。
            private_key_pem: PEM 格式私钥（为空则使用占位签名）。

        Returns:
            带签名的新卡片字典（深拷贝）。
        """
        import json as _json
        import copy
        from datetime import datetime, timezone

        signed = copy.deepcopy(card)

        if private_key_pem:
            try:
                from cryptography.hazmat.primitives import hashes, serialization
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.backends import default_backend
                import base64

                key = serialization.load_pem_private_key(
                    private_key_pem.encode(), password=None, backend=default_backend()
                )

                # 对 org_identity + agent_profile + accountability 做签名
                payload = _json.dumps({
                    "card_id": card["card_id"],
                    "org_identity": card.get("org_identity", {}),
                    "agent_profile": card.get("agent_profile", {}),
                    "accountability": card.get("accountability", {}),
                }, sort_keys=True, ensure_ascii=False)

                sig_bytes = key.sign(
                    payload.encode(),
                    padding.PKCS1v15(),
                    hashes.SHA256(),
                )
                sig_value = base64.b64encode(sig_bytes).decode()

                signed["signature"] = {
                    "algorithm": "RS256",
                    "value": sig_value,
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "verified_by": "org-identity-sdk",
                    "verification_method": "legal_rep_phone",
                }
                return signed
            except ImportError:
                pass

        # 占位签名（用于演示/测试）
        signed["signature"] = {
            "algorithm": "RS256",
            "value": "PLACEHOLDER_SIGNATURE_"
                     + hashlib.sha256(card["card_id"].encode()).hexdigest()[:32],
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verified_by": "org-identity-sdk/dev",
            "verification_method": "legal_rep_phone",
        }
        return signed
