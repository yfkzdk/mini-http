"""Tests for HTTP request parser."""

import pytest
from mini_http.parser import parse_request, HttpRequest


class TestParseRequest:
    def test_simple_get(self):
        data = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
        req = parse_request(data)
        assert req is not None
        assert req.method == "GET"
        assert req.path == "/index.html"
        assert req.version == "HTTP/1.1"
        assert req.headers["Host"] == "localhost"

    def test_post_with_body(self):
        data = b"POST /data HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello"
        req = parse_request(data)
        assert req is not None
        assert req.method == "POST"
        assert req.body == b"hello"

    def test_missing_host(self):
        data = b"GET / HTTP/1.1\r\n\r\n"
        req = parse_request(data)
        assert req is None  # invalid — no Host

    def test_path_traversal(self):
        data = b"GET /../secret HTTP/1.1\r\nHost: localhost\r\n\r\n"
        req = parse_request(data)
        assert req is None  # blocked

    def test_incomplete(self):
        data = b"GET / HTTP/1.1\r\nHo"
        req = parse_request(data)
        assert req is None  # incomplete — wait for more data

    def test_empty(self):
        assert parse_request(b"") is None

    def test_malformed(self):
        data = b"garbage\r\n\r\n"
        req = parse_request(data)
        assert req is None
