"""HTTP/1.1 request parser — RFC 7230 §3."""

from dataclasses import dataclass, field


@dataclass
class HttpRequest:
    method: str = ""
    path: str = ""
    version: str = ""
    headers: dict = field(default_factory=dict)
    body: bytes = b""


def parse_request(data: bytes):
    """Parse raw HTTP request bytes. Returns HttpRequest or None if incomplete/invalid."""
    if not data:
        return None

    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return None

    # Split headers from body
    parts = text.split("\r\n\r\n", 1)
    if len(parts) < 1:
        return None
    header_section = parts[0]
    body = parts[1].encode() if len(parts) > 1 else b""

    lines = header_section.split("\r\n")
    if not lines:
        return None

    # Parse request line
    request_line = lines[0].split(" ")
    if len(request_line) < 3:
        return None

    method = request_line[0].upper()
    path = request_line[1]
    version = request_line[2]

    # Validate method
    if method not in ("GET", "POST"):
        return HttpRequest(method=method, path=path, version=version)

    # Validate version
    if not version.startswith("HTTP/1."):
        return HttpRequest(method=method, path=path, version=version)

    # Parse headers
    headers = {}
    has_host = False
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        headers[key] = value
        if key.lower() == "host":
            has_host = True

    # Host header mandatory for HTTP/1.1
    if version == "HTTP/1.1" and not has_host:
        return None

    # Path traversal check
    if ".." in path:
        return None

    # Read body based on Content-Length
    content_length = int(headers.get("Content-Length", "0"))
    if content_length > 0 and len(body) < content_length:
        return None  # incomplete body

    return HttpRequest(
        method=method,
        path=path,
        version=version,
        headers=headers,
        body=body[:content_length],
    )
