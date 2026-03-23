# Stock API Docker 部署说明

本项目包含完整的 Docker 部署配置，可以一键启动 stock-api 服务及其依赖。

## 文件说明

- `Dockerfile`: 应用容器镜像构建文件
- `docker-compose.yml`: 多容器编排配置
- `.dockerignore`: Docker 构建忽略文件
- `conf/Config.py`: 已更新支持环境变量配置

## 服务架构

```
┌─────────────────────────────────────────────────┐
│                   Docker Network                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   PostgreSQL  │    │    Redis     │          │
│  │   (5433)     │    │    (6379)    │          │
│  └──────┬───────┘    └──────┬───────┘          │
│         │                     │                   │
│         └──────────┬──────────┘                   │
│                    │                              │
│         ┌──────────▼──────────┐                   │
│         │     stock-api        │                   │
│         │      (8000)          │                   │
│         └──────────────────────┘                   │
└─────────────────────────────────────────────────┘
```

## 快速开始

### 1. 启动所有服务

```bash
cd stock-api
docker-compose up -d
```

### 2. 查看服务状态

```bash
docker-compose ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f stock-api
```

### 4. 访问应用

- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 5. 停止服务

```bash
# 停止但保留数据
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

## 环境变量配置

可以通过修改 `docker-compose.yml` 中的环境变量来配置服务：

### 数据库配置
- `DB_HOST`: 数据库主机（默认: postgres）
- `DB_PORT`: 数据库端口（默认: 5432）
- `DB_NAME`: 数据库名称（默认: stock）
- `DB_USER`: 数据库用户（默认: postgres）
- `DB_PASSWORD`: 数据库密码（默认: postgres）

### Redis 配置
- `REDIS_HOST`: Redis 主机（默认: redis）
- `REDIS_PORT`: Redis 端口（默认: 6379）
- `REDIS_DB`: Redis 数据库（默认: 0）

## 数据持久化

- PostgreSQL 数据: 存储在 `postgres_data` 卷中
- Redis 数据: 存储在 `redis_data` 卷中

## 故障排查

### 查看服务健康状态
```bash
docker inspect --format='{{.State.Health.Status}}' stock-api-app
docker inspect --format='{{.State.Health.Status}}' stock-api-postgres
docker inspect --format='{{.State.Health.Status}}' stock-api-redis
```

### 重新构建镜像
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 技术栈

- **应用**: FastAPI + Uvicorn
- **数据库**: PostgreSQL 14
- **缓存**: Redis 7
- **Python**: 3.9