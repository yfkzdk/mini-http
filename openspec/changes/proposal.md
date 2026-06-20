# mini-http — 形式化规格

## Step 0a: 外部需求

**来源**: HTTP/1.1 RFC 7230 (ietf.org)——国际标准，非自己编造
**验收标准**: 浏览器访问 `http://localhost:8080/index.html` 正常显示页面；curl 发送 GET/POST 返回正确响应

## 目标

实现一个 HTTP/1.1 兼容的静态文件服务器。解析 HTTP 请求，返回正确的响应。零依赖 Python stdlib(socket)。

## 边界

### 范围内
- 解析 HTTP 请求行(method/path/version), 头部, body
- GET: 读取文件返回 200(Content-Type/Content-Length)
- POST: 接收 body
- 错误响应: 400/404/405/501/505
- MIME 类型推断(基于文件扩展名)
- 路径遍历防护(禁止 `../` 访问父目录)
- Content-Length 正确设置
- 单线程事件循环(select)
- Keep-Alive(复用同一个连接)

### 范围外
- HTTPS/TLS
- chunked Transfer-Encoding
- CGI/FastCGI
- 并发多线程
- 虚拟主机(单 Host)
- Cookie/Session

## 数据模型

```
HttpRequest:
  method: str           # GET/POST/...
  path: str             # /index.html
  version: str          # HTTP/1.1
  headers: dict         # {"Host": "localhost", ...}
  body: bytes           # raw request body

HttpResponse:
  status_code: int      # 200/400/404/405/501/505
  status_text: str      # OK/Bad Request/Not Found...
  headers: dict         # {"Content-Type": "text/html", ...}
  body: bytes           # response body (can be empty)
```

## 不变量

1. **响应格式**: 所有响应符合 `HTTP/1.1 STATUS\r\nHeader: Value\r\n\r\n[body]` 格式
2. **路径安全**: 解析后的路径不能逃逸文档根目录(../ 拒绝)
3. **Content-Length**: 有 body 的响应必须包含正确的 Content-Length
4. **Host 头**: HTTP/1.1 请求缺少 Host 头 → 400 Bad Request

## 函数规格

### parse_request(data: bytes) → HttpRequest | None
```
前置: data 为 TCP 接收的原始字节流
后置: 返回解析后的 HttpRequest, 不完整则返回 None
异常: 解析错误 → 不抛异常, 返回 None(由上层处理错误响应)
```

### build_response(request: HttpRequest, doc_root: str) → HttpResponse
```
前置: request 已解析, doc_root 存在
后置: 返回 HttpResponse
      GET + 文件存在 → 200 + body
      GET + 文件不存在 → 404
      方法不是 GET/POST → 405
      路径含 ../ → 400
      版本不是 HTTP/1.x → 505
```

### mime_type(path: str) → str
```
前置: path 为文件路径
后置: 根据扩展名返回 MIME 类型(.html→text/html, .css→text/css, ...)
      未知扩展名→application/octet-stream
```

### run_server(host: str, port: int, doc_root: str) → None
```
前置: port 可用, doc_root 存在
后置: 启动 TCP 服务器, 接受连接, 处理 HTTP 请求
      循环: bind→listen→accept→recv→parse→build→send→close
      直到进程被终止
```

## 测试场景

| ID | 场景 | 输入 | 期望 |
|----|------|------|------|
| T1 | GET 存在文件 | `GET /index.html HTTP/1.1` | 200 + Content-Type + body |
| T2 | GET 不存在文件 | `GET /nonexist HTTP/1.1` | 404 Not Found |
| T3 | GET 根路径 | `GET / HTTP/1.1` | 200(若有 index.html)或 404 |
| T4 | POST | `POST /data HTTP/1.1` + body | 200 OK |
| T5 | 路径遍历 | `GET /../secret HTTP/1.1` | 400 Bad Request |
| T6 | 非 GET/POST | `DELETE /file HTTP/1.1` | 405 Method Not Allowed |
| T7 | 无 Host 头 | `GET / HTTP/1.1`(无 Host) | 400 Bad Request |
| T8 | 非 HTTP/1.x | `GET / HTTP/2.0` | 505 Version Not Supported |
| T9 | 畸形请求 | `garbage data\r\n\r\n` | 400 |
| T10 | Keep-Alive | 同一连接发两个GET | 两个独立响应 |

## 项目结构

```
mini-http/
├── src/mini_http/
│   ├── __init__.py
│   ├── __main__.py       # CLI: python -m mini_http [--port 8080] [--root ./www]
│   ├── server.py         # TCP server + select event loop
│   ├── parser.py         # HTTP请求解析
│   ├── response.py       # HTTP响应构建 + MIME + 错误页面
│   └── router.py         # 路由分发(GET→文件, POST→接收)
├── tests/
│   ├── test_parser.py
│   ├── test_response.py
│   └── test_integration.py
├── www/                  # 默认文档根目录(index.html等)
└── openspec/changes/proposal.md
```

## 预计规模

| 模块 | 预计行数 |
|------|:--:|
| parser.py | 120 |
| response.py | 100 |
| router.py | 80 |
| server.py | 100 |
| __main__.py | 25 |
| **合计** | **~425** |
