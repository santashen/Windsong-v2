# Flyway 数据库迁移重构计划

## Context

当前 Go 后端使用 GORM `AutoMigrate` 在应用启动时自动创建/更新数据库表结构，数据库管理与应用部署耦合。本次重构将数据库迁移职责从 Go 应用中分离，交由 Flyway 管理，实现数据库版本化迁移、部署解耦。

## 涉及文件

| 文件 | 操作 |
|---|---|
| `db/migrations/V1__initial_schema.sql` | **新建** — 初始 schema |
| `backend/database/database.go` | **修改** — 移除 AutoMigrate |
| `docker-compose.yml` | **修改** — 添加 flyway 服务 |
| `docker-compose.prod.yml` | **修改** — 添加 flyway 服务，更新 backend depends_on |
| `docker-compose.test.yml` | **修改** — 添加 flyway 服务，更新 backend depends_on |
| `.github/workflows/deploy.yml` | **修改** — 拉取 flyway 镜像，切换到 Compose V2 |

---

## Step 1: 创建 SQL 迁移文件

**新建** `db/migrations/V1__initial_schema.sql`

根据 GORM 模型定义（Post、Photo、GoldAnalysis）编写等价的 DDL，使用 `CREATE TABLE IF NOT EXISTS` 保证幂等性：

- **posts 表**: id (BIGSERIAL PK), slug (UNIQUE NOT NULL), title, date (INDEX), tags (TEXT[]), content (TEXT), content_hash (VARCHAR(64)), is_published (BOOL DEFAULT TRUE, INDEX), created_at, updated_at
- **photos 表**: id (BIGSERIAL PK), url (NOT NULL), thumbnail, title (NOT NULL), description, date (INDEX), location (INDEX), city, country, tags, aspect_ratio, created_at, updated_at
- **gold_analyses 表**: id (BIGSERIAL PK), analysis_date (UNIQUE NOT NULL), content (TEXT NOT NULL), model_used (VARCHAR(50)), prompt_hash (VARCHAR(64)), created_at, updated_at

> 注意：GORM 默认将无 `size` tag 的 string 映射为 `TEXT`（非 VARCHAR(256)），需以实际数据库 schema 为准。实施前应通过 `\d tablename` 确认。

## Step 2: 修改 Go 后端

**修改** `backend/database/database.go`

- 删除 `migrate()` 函数及其调用
- 删除 `"windsong/models"` import
- 保留 `Init()`（仅建立连接）和 `GetDB()`
- 其他 Go 代码（models、services、handlers）无需变更，GORM 继续用于查询

## Step 3: 添加 Flyway 到 docker-compose.yml（开发环境）

在 postgres 服务之后添加 flyway 服务：

```yaml
flyway:
  image: flyway/flyway:10
  container_name: windsong-flyway-dev
  command: migrate
  environment:
    FLYWAY_URL: jdbc:postgresql://postgres:5432/windsong
    FLYWAY_USER: windsong
    FLYWAY_PASSWORD: windsong123
    FLYWAY_BASELINE_ON_MIGRATE: "true"
    FLYWAY_BASELINE_VERSION: "1"
  volumes:
    - ./db/migrations:/flyway/sql:ro
  depends_on:
    postgres:
      condition: service_healthy
```

开发环境中后端由开发者手动运行（`go run main.go`），无需依赖链。开发者执行 `docker compose up -d` 后 Flyway 自动运行迁移。

## Step 4: 添加 Flyway 到 docker-compose.prod.yml（生产环境）

在 postgres 和 backend 之间添加 flyway 服务，并更新 backend 的 depends_on：

```yaml
flyway:
  image: flyway/flyway:10
  container_name: windsong-flyway
  command: migrate
  environment:
    FLYWAY_URL: jdbc:postgresql://postgres:5432/${DB_NAME:-windsong}
    FLYWAY_USER: ${DB_USER:-windsong}
    FLYWAY_PASSWORD: ${DB_PASSWORD}
    FLYWAY_BASELINE_ON_MIGRATE: "true"
    FLYWAY_BASELINE_VERSION: "1"
  volumes:
    - ./db/migrations:/flyway/sql:ro
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - windsong-network
```

backend 的 depends_on 更新为：
```yaml
depends_on:
  postgres:
    condition: service_healthy
  flyway:
    condition: service_completed_successfully
```

> `service_completed_successfully` 确保 Flyway 运行完毕并成功退出后，backend 才启动。

## Step 5: 添加 Flyway 到 docker-compose.test.yml（测试环境）

同 Step 4 模式，添加 flyway 服务并更新 backend depends_on。使用硬编码凭据（windsong/windsong123），加入 `windsong-test` 网络。

## Step 6: 更新 GitHub Actions

**修改** `.github/workflows/deploy.yml`

1. 在 docker pull 部分添加 `docker pull flyway/flyway:10`
2. 将 `docker-compose` 命令替换为 `docker compose`（Compose V2），因为 `service_completed_successfully` 条件需要 Compose V2 支持

```bash
docker pull flyway/flyway:10

docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

## 已有数据库的处理（Baseline 策略）

通过 Flyway 的 `FLYWAY_BASELINE_ON_MIGRATE=true` + `FLYWAY_BASELINE_VERSION=1` 配置：

- **新数据库**（开发/测试）：Flyway 执行 V1 创建所有表
- **已有生产数据库**：Flyway 检测到无 `flyway_schema_history` 表，自动将 V1 标记为已执行（baseline），不会重复创建表。后续只执行 V2+ 的新迁移

## 验证方案

1. **本地开发验证**：
   - 删除本地 postgres_data volume（全新数据库）
   - `docker compose up -d` → 检查 flyway 容器日志确认 V1 执行成功
   - `go run main.go` → 确认后端正常启动并能读写数据

2. **已有数据库验证**：
   - 保留现有 postgres_data volume
   - `docker compose up -d` → 检查 flyway 日志确认 baseline 成功
   - 确认 `flyway_schema_history` 表已创建且 V1 标记为 baseline

3. **生产部署前**：
   - 在服务器上先通过 `pg_dump --schema-only` 导出当前 schema
   - 与 V1__initial_schema.sql 对比确认一致性
