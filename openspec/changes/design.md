# Design — mini-http

## ADR-1: select() 事件循环
**决策**: 单线程 select() 处理多连接。和 mini-redis 一致。
**备选**: threading——增加复杂度，不需要。

## ADR-2: 字符级 HTTP 解析
**决策**: 逐字节解析请求行和头部。基于 CRLF 分割。不使用正则或第三方库。
**备选**: h11 库——引入依赖，破坏零依赖原则。

## ADR-3: 文档根目录 + 路径安全检查
**决策**: 所有文件访问限制在 `--root` 指定的目录内。`os.path.realpath` 验证不逃逸。

## ADR-4: 响应构建器模式
**决策**: HttpResponse dataclass → `to_bytes()` 序列化为 HTTP/1.1 响应。
200/400/404/405/501/505 预定义工厂函数。

## 模块依赖
```
__main__ → server → router → parser → (stdlib)
                   → response → (stdlib)
```
