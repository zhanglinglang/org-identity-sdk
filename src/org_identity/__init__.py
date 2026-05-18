"""
org-identity-sdk — 可信智能体协作基础设施

提供标准化的组织-智能体身份卡片生成、验证、签名能力。
兼容 Google A2A AgentCard 及国内 ATH 协议。
"""

__version__ = "0.1.0"
__author__ = "南京灵枢铸药智能科技有限公司"

from .client import OrgIdentityClient
from .builder import IdentityBuilder
from .validator import IdentityValidator
from .exporter import IdentityExporter
from .verifier import PhoneVerifier

__all__ = [
    "OrgIdentityClient",
    "IdentityBuilder",
    "IdentityValidator",
    "IdentityExporter",
    "PhoneVerifier",
]
