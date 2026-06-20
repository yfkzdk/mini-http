"""Integration tests — full HTTP request-response cycle."""

from mini_http.parser import parse_request
from mini_http.router import route
from mini_http.response import error_response


class TestRouting:
    def test_get_index(self):
        req = parse_request(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        resp = route(req, "www")
        assert resp.status_code == 200
        assert resp.body

    def test_get_nonexistent(self):
        req = parse_request(b"GET /nonexist HTTP/1.1\r\nHost: localhost\r\n\r\n")
        resp = route(req, "www")
        assert resp.status_code == 404

    def test_method_not_allowed(self):
        req = parse_request(b"DELETE /file HTTP/1.1\r\nHost: localhost\r\n\r\n")
        assert req is not None
        resp = route(req, "www")
        assert resp.status_code == 405

    def test_response_format(self):
        req = parse_request(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        resp = route(req, "www")
        raw = resp.to_bytes()
        assert b"HTTP/1.1" in raw
        assert b"Content-Length" in raw


class TestErrorResponses:
    def test_400_bad_request(self):
        resp = error_response(400)
        assert resp.status_code == 400
        assert b"400" in resp.to_bytes()

    def test_404_not_found(self):
        resp = error_response(404)
        assert resp.status_code == 404

    def test_501_not_implemented(self):
        resp = error_response(501)
        assert resp.status_code == 501
