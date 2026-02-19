API 规范化实现计划

Context

当前后端 API 响应格式不统一：有的返回 {"error": "..."}, 有的返回 {"error": "...", "details": "..."}, auth 返回 {"valid": false, "message": "..."}。无错误码体系、无 API 文档、无系统化的参数校验、无版本管理。本计划按 README 中的开发计划，实现四项 API 规范化改造。

---

Step 1: 创建统一响应工具（仅新增，不改行为）

新建 backend/handlers/response.go：

    // 响应信封
    type Response struct {
        Code    int         `json:"code"`
        Message string      `json:"message"`
        Data    interface{} `json:"data,omitempty"`
    }
    
    // 错误码（映射 HTTP 状态码 + 子码）
    const (
        CodeSuccess         = 0
        CodeBadRequest      = 40000
        CodeValidationError = 40001
        CodeUnauthorized    = 40100
        CodeNotFound        = 40400
        CodeInternalError   = 50000
        CodeExternalService = 50200
    )
    
    // 辅助函数
    func Success(c *gin.Context, data interface{})
    func SuccessCreated(c *gin.Context, data interface{})  // 201
    func Error(c *gin.Context, httpStatus, code int, message string)
    func ValidationError(c *gin.Context, err error)  // 解析 validator.ValidationErrors

---

Step 2: API 版本化

修改 backend/routes/routes.go：

- r.Group("/api") → r.Group("/api/v1")（变量名 api → v1，其余路由注册代码不变）
- /health 和 /swagger/ 保持在根路径，不加版本号

修改 frontend/src/api/index.js：

- baseURL: '/api' → baseURL: '/api/v1'

无需修改：

- frontend/nginx.conf — location /api/ 前缀匹配已覆盖 /api/v1/
- frontend/vite.config.js — proxy /api 前缀匹配已覆盖 /api/v1

---

Step 3: 所有 handler + middleware 应用统一响应格式

将所有 c.JSON(status, gin.H{...}) 替换为 Success() / Error() 调用：

  文件                       	改动点                                     
  handlers/auth.go         	4 处 c.JSON → Success / Error            
  handlers/post.go         	6 处 c.JSON → Success / Error            
  handlers/photo.go        	~12 处 c.JSON → Success / Error / SuccessCreated
  handlers/gold_analysis.go	2 处 c.JSON → Success / Error            
  middleware/auth.go       	1 处 → 导入 handlers.Response 构造错误响应       
  routes/routes.go         	2 处内联 handler（health、hello）→ handlers.Success

---

Step 4: 前端适配统一响应格式

修改 frontend/src/api/index.js — 添加响应拦截器自动解包信封：

    api.interceptors.response.use(
      response => {
        const res = response.data
        if (res && typeof res === 'object' && 'code' in res) {
          if (res.code === 0) {
            response.data = res.data  // 解包：外层 data 替换为内层 data
            return response
          }
          const err = new Error(res.message || 'Request failed')
          err.code = res.code
          err.response = response
          return Promise.reject(err)
        }
        return response  // 非信封响应透传（如 ai-api）
      },
      error => Promise.reject(error)
    )

解包后 response.data 直接就是业务数据，大部分 store 无需改动（blog.js、gallery.js 的 response.data.posts 等访问路径不变）。

需要调整 catch 块的 store：

- stores/gold.js — err.response?.data?.error → err.message
- stores/auth.js — err.response?.data?.message → err.message

---

Step 5: 请求参数校验增强

修改 handlers/photo.go：

- PhotoInput 增强 binding tags：url 校验、datetime=2006-01-02 替代手动 time.Parse、max 长度限制
- 新增 PhotoListQuery struct（form + binding tags），替换手动 strconv.Atoi

修改 handlers/post.go：

- 新增 PostListQuery struct，替换手动 strconv.Atoi

所有 ShouldBindJSON / ShouldBindQuery 错误统一走 ValidationError() 辅助函数，返回结构化校验失败信息。

---

Step 6: Swagger/OpenAPI 文档

安装依赖：

    go install github.com/swaggo/swag/cmd/swag@latest
    go get github.com/swaggo/gin-swagger github.com/swaggo/files

修改 backend/main.go — 顶部添加 API 元信息注释（title、version、BasePath /api/v1、securityDefinitions）

修改 4 个 handler 文件 — 每个方法添加 swaggo 注释（Summary、Params、Success/Failure response types）

修改 backend/routes/routes.go — 添加 Swagger UI 路由：

    r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

修改 frontend/nginx.conf — 添加 /swagger/ 代理：

    location /swagger/ {
        proxy_pass http://windsong-backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

生成文档：cd backend && swag init（生成 docs/ 目录，提交到仓库）

---

完整文件清单

  操作  	文件                               
  新建  	backend/handlers/response.go     
  生成  	backend/docs/（swag init）         
  修改  	backend/main.go                  
  修改  	backend/routes/routes.go         
  修改  	backend/handlers/auth.go         
  修改  	backend/handlers/post.go         
  修改  	backend/handlers/photo.go        
  修改  	backend/handlers/gold_analysis.go
  修改  	backend/middleware/auth.go       
  修改  	backend/go.mod（新增 swaggo 依赖）     
  修改  	frontend/src/api/index.js        
  修改  	frontend/src/stores/gold.js      
  修改  	frontend/src/stores/auth.js      
  修改  	frontend/nginx.conf              

验证方式

1. cd backend && go build — 编译通过
2. cd backend && swag init — 文档生成成功
3. 启动数据库 + 后端，curl 验证响应格式：
   - curl localhost:8080/health → {"code":0,"message":"success","data":{...}}
   - curl localhost:8080/api/v1/posts → {"code":0,"message":"success","data":{"posts":[...],"pagination":{...}}}
   - curl localhost:8080/api/v1/posts/nonexistent → {"code":40400,"message":"Post not found"}
4. 访问 localhost:8080/swagger/index.html — Swagger UI 正常展示
5. 启动前端，验证博客列表、相册、黄金分析页面正常加载数据
