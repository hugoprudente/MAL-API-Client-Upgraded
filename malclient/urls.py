from __future__ import annotations

from typing import Literal

__all__ = [
    "MAL_API_HOST",
    "MAL_OAUTH_BASE",
    "MalApiVersion",
    "oauth_authorize_url",
    "oauth_token_url",
    "rest_base_url",
]

MAL_API_HOST = "https://api.myanimelist.net"
MAL_OAUTH_BASE = "https://myanimelist.net/v1"

MalApiVersion = Literal["v1", "v2"]


def rest_base_url(version: MalApiVersion = "v2") -> str:
    """Base URL for MAL REST API (`v2` is the supported API)."""
    return f"{MAL_API_HOST}/{version}/"


def oauth_authorize_url() -> str:
    return f"{MAL_OAUTH_BASE}/oauth2/authorize"


def oauth_token_url() -> str:
    return f"{MAL_OAUTH_BASE}/oauth2/token"