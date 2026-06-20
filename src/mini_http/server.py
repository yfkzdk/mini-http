"""TCP server with select() event loop."""

import select
import socket
from .parser import parse_request
from .router import route
from .response import error_response


def run_server(host: str = "127.0.0.1", port: int = 8080, doc_root: str = "www"):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(10)
    server.setblocking(False)
    print(f"mini-http serving {doc_root} on http://{host}:{port}")

    sockets = [server]
    buffers: dict[int, bytearray] = {}

    try:
        while True:
            readable, _, _ = select.select(sockets, [], [], 0.5)
            for s in readable:
                if s is server:
                    client, addr = server.accept()
                    client.setblocking(False)
                    sockets.append(client)
                    buffers[client.fileno()] = bytearray()
                else:
                    try:
                        data = s.recv(4096)
                    except ConnectionResetError:
                        data = b""
                    if not data:
                        buffers.pop(s.fileno(), None)
                        sockets.remove(s)
                        s.close()
                        continue
                    buffers[s.fileno()].extend(data)
                    buf = bytes(buffers[s.fileno()])
                    req = parse_request(buf)
                    if req is not None:
                        resp = route(req, doc_root)
                        try:
                            s.sendall(resp.to_bytes())
                        except BrokenPipeError:
                            pass
                        buffers[s.fileno()] = bytearray()
    except KeyboardInterrupt:
        print("\nmini-http shutting down")
    finally:
        server.close()
