结构化日志实现计划

Context

当前项目的日志能力极其薄弱：Go 后端仅使用 stdlib log 包（纯文本，无级别，无 request ID），Python AI 服务使用 stdlib logging（无结构化，无请求中间件）。生产环境中无法通过日志追踪请求链路、定位错误。本计划实现 README 开发路线图中的结构化日志部分。

---

一、Go 后端

选型：zerolog

轻量、零分配、API 简洁，适合个人博客项目。开发环境输出彩色可读格式，生产环境输出 JSON。

新增依赖

    github.com/rs/zerolog
    github.com/google/uuid

Step 1：创建 backend/logger/logger.go

- 导出 Log zerolog.Logger 包级变量和 Init(isProduction bool) 函数
- 生产环境：JSON 输出到 stdout，日志级别 Info
- 开发环境：zerolog.ConsoleWriter 彩色输出，日志级别 Debug

Step 2：创建三个中间件

backend/middleware/request_id.go — RequestID 中间件

- 读取请求头 X-Request-ID，没有则生成 UUID
- 存入 gin.Context（key: request_id）
- 写入响应头 X-Request-ID

backend/middleware/logger.go — 请求日志中间件 + GetLogger 辅助函数

- 从 context 取 request_id，创建子 logger（绑定 request_id/method/path）
- 存入 gin.Context（key: logger），供 handler 通过 middleware.GetLogger(c) 获取
- 请求完成后记录 status、latency、ip；按状态码选择日志级别（5xx→Error, 4xx→Warn, 其余→Info）

backend/middleware/recovery.go — Panic 恢复中间件

- 替代 gin.Recovery()，panic 时通过 zerolog 记录错误和堆栈

Step 3：修改 backend/main.go

- 在 config.Load() 后调用 logger.Init(cfg.IsProduction())
- gin.Default() → gin.New() + 注册三个新中间件
- 所有 log.* 调用替换为 logger.Log.*

Step 4：迁移现有日志调用

  文件                          	变更                                      
  backend/database/database.go	log.* → logger.Log.*                    
  backend/services/post.go    	log.* → logger.Log.*（4 处）               
  backend/services/photo.go   	修复 ImportFromJSON 中静默吞掉的 DB 错误，添加 logger.Log.Error()
  backend/middleware/auth.go  	认证失败时 GetLogger(c).Warn() 记录            

Step 5：Handler 层添加错误日志

四个 handler 文件（post.go, photo.go, gold_analysis.go, auth.go）的错误分支添加 middleware.GetLogger(c).Error().Err(err).Msg(...) 调用。

---

二、Python AI 服务

选型：structlog

支持 contextvars 自动绑定 request_id，开发/生产双模式输出，与 Go 端 JSON 格式一致。

新增依赖

requirements.txt 添加 structlog

Step 6：ai-service/config.py 添加 ENV 字段

    ENV: str = os.getenv("ENV", "development")

Step 7：创建 ai-service/logging_config.py

- 配置 structlog：生产环境 JSONRenderer，开发环境 ConsoleRenderer
- 日志级别：生产 INFO，开发 DEBUG

Step 8：修改 ai-service/main.py

- 删除 logging.basicConfig 和 logging.getLogger
- 调用 configure_logging()，使用 structlog.get_logger()
- 添加 HTTP 中间件：生成/传播 request_id，用 structlog.contextvars 绑定请求上下文，记录 status/latency/ip
- 现有 logger.error(f"...") 改为 logger.error("...", error=str(e)) 关键字参数风格

Step 9：迁移 service 层日志

  文件                                  	变更                                      
  ai-service/services/finance_data.py 	logging → structlog；修复 except Exception: pass（改为 logger.debug）；f-string → 关键字参数
  ai-service/services/gold_analysis.py	添加 structlog logger，记录分析开始/完成/失败        
  ai-service/services/base_llm.py     	添加 structlog logger，debug 级别记录 LLM 调用   

---

三、验证方式

1. Go 后端：go build ./... 编译通过；启动服务后请求任意 API，终端应输出带 request_id、method、path、status、latency 的结构化日志；设置 ENV=production 时输出 JSON 格式
2. Python AI 服务：pip install -r requirements.txt 后启动服务，请求 /health，终端应输出结构化请求日志
3. 检查响应头包含 X-Request-ID
4. 制造错误请求（如无效 API key），确认日志中有 Warn 级别记录

---

关键文件清单

- backend/main.go — 入口，gin 初始化
- backend/config/config.go — 已有 IsProduction() 方法
- backend/middleware/auth.go — 现有唯一中间件
- backend/routes/routes.go — 路由注册
- backend/database/database.go — 数据库初始化
- backend/services/post.go — 含 4 处 log 调用
- backend/services/photo.go — 含静默错误吞没
- backend/handlers/ — 4 个 handler 文件
- ai-service/main.py — Python 入口
- ai-service/config.py — 配置类
- ai-service/services/ — 3 个 service 文件
