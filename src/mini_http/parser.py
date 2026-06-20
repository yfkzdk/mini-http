"""Stub — HTTP request parser."""

from dataclasses import dataclass, field


@dataclass
class HttpRequest:
    method: str = ""
    path: str = ""
    version: str = ""
    headers: dict = field(default_factory=dict)
    body: bytes = b""


def parse_request(data: bytes):
    return None
