# 计划：统一 Python AI 服务响应格式

## 背景

Python AI 服务（FastAPI）各端点直接返回原始 JSON，错误使用 FastAPI 默认的 `{"detail": "..."}` 格式。Go 后端使用统一信封 `{"code": 0, "message": "success", "data": {...}}`，两者不一致导致前端需要两套响应处理逻辑。

目标：在 Python 侧加入响应包装中间件，让所有 `/api/*` 响应都遵循与 Go 相同的信封格式，并同步更新 Go 服务端解析逻辑和前端 `aiApi` 拦截器。

---

## 改动范围

涉及 4 个文件，共 5 处修改。

---

## 文件 1：`ai-service/main.py`

### 改动 1-a：添加 `import json`

```python
# 第 1 行，在 import time 之前添加
import json
import time
```

### 改动 1-b：在 `RequestLoggingMiddleware` 类定义之后、`app.add_middleware` 之前，插入以下内容（当前第 54 行空行之后）

```python
# 错误码映射，与 Go 后端保持一致
_HTTP_TO_CODE: dict[int, int] = {
    400: 40000,
    401: 40100,
    403: 40100,
    404: 40400,
    422: 40001,
}
_SKIP_PATHS = {"/health"}


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """将所有 /api/* JSON 响应包装为统一信封 {code, message, data}。"""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 健康检查端点保持原始格式（供 Docker/Nginx 基础设施使用）
        if request.url.path in _SKIP_PATHS:
            return response

        # 只处理 JSON 响应
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # 读取流式响应体
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            chunks.append(chunk)
        body = b"".join(chunks)

        try:
            original = json.loads(body)
        except Exception:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type,
            )

        status = response.status_code

        if status < 400:
            envelope = {"code": 0, "message": "success", "data": original}
        else:
            code = _HTTP_TO_CODE.get(status, 50000)
            if isinstance(original, dict) and "detail" in original:
                detail = original["detail"]
                message = detail if isinstance(detail, str) else str(detail)
            else:
                message = "error"
            envelope = {"code": code, "message": message}

        new_body = json.dumps(envelope).encode("utf-8")
        headers = dict(response.headers)
        headers["content-length"] = str(len(new_body))

        return Response(
            content=new_body,
            status_code=status,
            headers=headers,
            media_type="application/json",
        )
```

### 改动 1-c：注册中间件（在现有 `app.add_middleware(RequestLoggingMiddleware)` 之后）

```python
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ResponseEnvelopeMiddleware)  # 新增
```

**中间件执行顺序说明**：Starlette 后注册的中间件外层包裹先执行，调用链为：
`ResponseEnvelopeMiddleware → RequestLoggingMiddleware → handler`。
`X-Request-ID` 由 `RequestLoggingMiddleware` 先写入响应头，`ResponseEnvelopeMiddleware` 通过 `dict(response.headers)` 保留。

---

## 文件 2：`backend/services/gold_analysis.go`

Python 服务包装后，Go 收到的格式变为：
```json
{"code": 0, "message": "success", "data": {"content": "...", "modelUsed": "...", "promptHash": "..."}}
```

### 改动 2-a：在 `AIServiceResponse` 结构体之后（第 39 行后）添加信封结构体

```go
// aiServiceEnvelope 是 Python AI 服务统一响应信封
type aiServiceEnvelope struct {
	Code    int                `json:"code"`
	Message string             `json:"message"`
	Data    *AIServiceResponse `json:"data"`
}
```

### 改动 2-b：更新 `fetchFromAIService` 中的 JSON 解析逻辑（第 100-105 行）

```go
// 原来
var result AIServiceResponse
if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
    return nil, fmt.Errorf("decode response failed: %w", err)
}
return &result, nil

// 改为
var envelope aiServiceEnvelope
if err := json.NewDecoder(resp.Body).Decode(&envelope); err != nil {
    return nil, fmt.Errorf("decode response failed: %w", err)
}
if envelope.Code != 0 {
    return nil, fmt.Errorf("AI service error (code=%d): %s", envelope.Code, envelope.Message)
}
if envelope.Data == nil {
    return nil, fmt.Errorf("AI service returned empty data")
}
return envelope.Data, nil
```

无需更改 import（`encoding/json` 和 `fmt` 已存在）。现有 HTTP 状态码非 200 的快速失败检查（第 96-98 行）保持不变。

---

## 文件 3：`frontend/src/api/index.js`

为 `aiApi` 实例添加与 `api` 相同的响应拦截器，在第 80 行（`aiApi` 创建结束的 `}`）之后、第 82 行（`// Finance Data API`）之前插入：

```js
// 响应拦截器 - 解包统一响应信封 { code, message, data }
aiApi.interceptors.response.use(
  response => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) {
        response.data = res.data
        return response
      }
      const err = new Error(res.message || 'Request failed')
      err.code = res.code
      err.response = response
      return Promise.reject(err)
    }
    return response
  },
  error => Promise.reject(error)
)
```

拦截器解包后，`response.data` 变为信封内层 `data` 字段。`finance.js` 中 `res.data.results`（第 84 行）和 `r.data.results`（第 161 行）的取值逻辑**不需要改动**，因为解包后 `response.data` 仍是 `{"results": [...]}`。

---

## 文件 4：`frontend/src/stores/finance.js`

仅需修改错误处理（第 169 行），从 FastAPI 错误格式改为统一格式：

```js
// 原来（第 169 行）
error.value = err.response?.data?.detail || 'Failed to fetch data'

// 改为
error.value = err.message || 'Failed to fetch data'
```

---

## 改动后数据流

```
Python /api/finance/search 返回:
  {"code": 0, "message": "success", "data": {"results": [...]}}

aiApi 拦截器解包:
  response.data = {"results": [...]}

finance.js 取值:
  res.data.results  →  [...] ✓  (与改前一致)
```

```
Python /api/gold/analyze 返回:
  {"code": 0, "message": "success", "data": {"content": "...", "modelUsed": "...", "promptHash": "..."}}

Go fetchFromAIService 解析:
  envelope.Data = &AIServiceResponse{Content: "...", ...}

Go 返回给前端:
  {"code": 0, "message": "success", "data": {...GoldAnalysis model...}}
```

---

## 验证方式

1. **Python 服务**：启动后访问 `curl http://localhost:8000/api/finance/search?keyword=平安`，应返回 `{"code":0,"message":"success","data":{"results":[...]}}`；访问 `/health` 应仍返回原始 `{"status":"ok","service":"ai-service"}`。
2. **Go 后端**：启动后访问 `GET /api/v1/gold/today`，应正常返回黄金分析数据（或 AI 服务错误时返回明确错误信息）。
3. **前端**：打开 FinanceView，搜索股票/基金应正常显示结果；打开 GoldAnalysis 页面应正常加载分析内容。
