"""HTTP response builder — RFC 7230 §3.1.2."""

from dataclasses import dataclass, field
import os
import html


STATUS_TEXTS = {
    200: "OK", 400: "Bad Request", 404: "Not Found",
    405: "Method Not Allowed", 501: "Not Implemented", 505: "HTTP Version Not Supported",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css", ".js": "application/javascript",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".svg": "image/svg+xml",
    ".ico": "image/x-icon", ".json": "application/json",
    ".txt": "text/plain", ".pdf": "application/pdf",
}


@dataclass
class HttpResponse:
    status_code: int = 200
    headers: dict = field(default_factory=dict)
    body: bytes = b""

    def to_bytes(self) -> bytes:
        status_text = STATUS_TEXTS.get(self.status_code, "Unknown")
        lines = [f"HTTP/1.1 {self.status_code} {status_text}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        header_bytes = "\r\n".join(lines).encode() + b"\r\n"
        return header_bytes + self.body


def ok_response(body: bytes, content_type: str) -> HttpResponse:
    return HttpResponse(200, {
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
        "Connection": "keep-alive",
    }, body)


def error_response(code: int) -> HttpResponse:
    text = STATUS_TEXTS.get(code, "Error")
    body = f"<h1>{code} {text}</h1>".encode()
    return HttpResponse(code, {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": str(len(body)),
        "Connection": "close" if code == 400 else "keep-alive",
    }, body)


def mime_type(path: str) -> str:
    _, ext = os.path.splitext(path)
    return MIME_TYPES.get(ext.lower(), "application/octet-stream")
