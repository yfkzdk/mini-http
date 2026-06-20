"""Request router — dispatch GET/POST, serve files."""

import os
from .parser import HttpRequest
from .response import HttpResponse, ok_response, error_response, mime_type


def route(request: HttpRequest, doc_root: str) -> HttpResponse:
    if request.method == "GET":
        return _handle_get(request.path, doc_root)
    elif request.method == "POST":
        return _handle_post(request)
    else:
        return error_response(405)


def _handle_get(path: str, doc_root: str) -> HttpResponse:
    if path == "/":
        path = "/index.html"
    full_path = os.path.normpath(os.path.join(doc_root, path.lstrip("/")))
    if not full_path.startswith(os.path.normpath(doc_root)):
        return error_response(400)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return error_response(404)
    try:
        with open(full_path, "rb") as f:
            body = f.read()
        return ok_response(body, mime_type(full_path))
    except OSError:
        return error_response(404)


def _handle_post(request: HttpRequest) -> HttpResponse:
    return HttpResponse(200, {
        "Content-Type": "text/plain",
        "Content-Length": "2",
        "Connection": "keep-alive",
    }, b"OK")
