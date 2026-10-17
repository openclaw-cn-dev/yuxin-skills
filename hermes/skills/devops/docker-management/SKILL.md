---
name: docker-management
description: Manage Docker containers, images, volumes, networks, and Compose stacks — lifecycle ops, debugging, cleanup, Dockerfile optimization, and multi-project port isolation for the 渔芯 dev machine.
tags: [docker, containers, devops, infrastructure, compose, images, volumes, networks, debugging, multi-project, port-allocation]
---

# Docker Management

Manage Docker containers, images, volumes, networks, and Compose stacks using standard Docker CLI commands. No additional dependencies beyond Docker itself.

## When to Use

- Run, stop, restart, remove, or inspect containers
- Build, pull, push, tag, or clean up Docker images
- Work with Docker Compose (multi-service stacks)
- Manage volumes or networks
- Debug a crashing container or analyze logs
- Check Docker disk usage or free up space
- **Run automated container cleanup & health checks** (see `references/auto-management.md`)
- Review or optimize a Dockerfile
- **Start a NEW project on the 渔芯 dev machine** (port-conflict aware)

## Prerequisites

- Docker Engine installed and running
- User added to the `docker` group (or use `sudo`)
- Docker Compose v2 (included with modern Docker installations)

Quick check:

```bash
docker --version && docker compose version
```

## Quick Reference

| Task | Command |
|------|---------|
| Run container (background) | `docker run -d --name NAME IMAGE` |
| Stop + remove | `docker stop NAME && docker rm NAME` |
| View logs (follow) | `docker logs --tail 50 -f NAME` |
| Shell into container | `docker exec -it NAME /bin/sh` |
| List all containers | `docker ps -a` |
| Build image | `docker build -t TAG .` |
| Compose up | `docker compose up -d` |
| Compose down | `docker compose down` |
| Disk usage | `docker system df` |
| Cleanup dangling | `docker image prune && docker container prune` |
| **Auto-manage (cron)** | `bash ~/.hermes/skills/devops/docker-management/scripts/docker_mgmt.sh` (每2h, cron `377b51861b4f`) |

### 8. Automated Container Management

渔芯 Docker 环境每 2 小时自动执行容器优化（cron `377b51861b4f`），脚本 `scripts/docker_mgmt.sh`：

| 步骤 | 动作 |
|------|------|
| 1 | 清理超过 24h 的已停止容器 |
| 2 | 删除悬空镜像 |
| 3 | 删除未引用卷（保护运行容器的卷） |
| 4 | 截断 >200MB 的容器日志 |
| 5 | 资源快照 + 健康检查 |

无异常时 cron 输出 [SILENT]，有清理或异常时汇报到飞书。日志：`~/.hermes/logs/docker_mgmt.log`。

当前渔芯生产容器（12 个）：RKR (rkr-redis/postgres/elasticsearch/minio/backend/frontend/celery-beat/processing-pool/processing-pool-2/staging-pool) + FindEra (research-backend/frontend)。

### 9. RKR 知识库的自动启停 cron（白天停 / 晚上跑）

华哥要「让出资源」关容器时，光 stop 容器不够——有 4 个 cron 会自动把知识库拉回来（2026-08-30 实测）：

| cron | 频率 | 动作 |
|---|---|---|
| 启动寻元+知识库 `843dab2fcc6b` | 每天 23:30 | `docker compose up` 拉起 FindEra+RKR 全部容器（rkr_findera_start.sh）|
| 停止寻元+知识库 `8e8a959de80b` | 每天 8:00 | 停容器（rkr_findera_stop.sh）|
| RKR 每日200条补齐 `ff723d73c7a9` | 每 2 分钟 | 跑补齐任务（rkr_daily_catchup.sh）|
| FindEra→RKR 同步 `13383c9e20fd` | 每 10 分钟 | 同步数据（prompt 明确「绝不 docker compose up」，仅同步）|

机制：白天 8 点自动停 → 晚上 23:30 自动启动跑一晚上 → 早上再停，循环。要彻底关掉知识库释放资源，需同时 pause 这几个 cron（尤其 23:30 启动 + 每 2 分钟补齐），否则当晚又会自动拉起。

### 10. 彻底关容器用 compose down，不是 stop+prune

`docker stop` + `docker container prune` 只删容器，compose 编排元数据仍残留 → **Docker Desktop 重启后 compose 项目（restart policy）会自动把容器拉回来**（2026-08-30 复现：stop+prune 清空后，Docker Desktop 一重启容器又回来了）。要彻底关，必须 `cd <项目> && docker compose down`（保留 volume），down 后 compose 元数据清除。停容器后若发现又自己起来了，先查 Docker Desktop 是否重启过 + 上面的自动启停 cron。

### Procedure

### 1. Identify the domain

Figure out which area the request falls into:

- **Container lifecycle** → run, stop, start, restart, rm, pause/unpause
- **Container interaction** → exec, cp, logs, inspect, stats
- **Image management** → build, pull, push, tag, rmi, save/load
- **Docker Compose** → up, down, ps, logs, exec, build, config
- **Volumes & networks** → create, inspect, rm, prune, connect
- **Troubleshooting** → log analysis, exit codes, resource issues
- **Multi-project isolation** → port allocation, container naming, volume naming (渔芯常态)

### 2. Container operations

**Run a new container:**

```bash
# Detached service with port mapping
docker run -d --name web -p 8080:80 nginx

# With environment variables
docker run -d -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=mydb --name db postgres:16

# With persistent data (named volume)
docker run -d -v pgdata:/var/lib/postgresql/data --name db postgres:16

# For development (bind mount source code)
docker run -d -v $(pwd)/src:/app/src -p 3000:3000 --name dev my-app

# Interactive debugging (auto-remove on exit)
docker run -it --rm ubuntu:22.04 /bin/bash

# With resource limits and restart policy
docker run -d --memory=512m --cpus=1.5 --restart=unless-stopped --name app my-app
```

Key flags: `-d` detached, `-it` interactive+tty, `--rm` auto-remove, `-p` port (host:container), `-e` env var, `-v` volume, `--name` name, `--restart` restart policy.

**Manage running containers:**

```bash
docker ps                        # running containers
docker ps -a                     # all (including stopped)
docker stop NAME                 # graceful stop
docker start NAME                # start stopped container
docker restart NAME              # stop + start
docker rm NAME                   # remove stopped container
docker rm -f NAME                # force remove running container
docker container prune           # remove ALL stopped containers
```

**Interact with containers:**

```bash
docker exec -it NAME /bin/sh          # shell access (use /bin/bash if available)
docker exec NAME env                   # view environment variables
docker exec -u root NAME apt update    # run as specific user
docker logs --tail 100 -f NAME         # follow last 100 lines
docker logs --since 2h NAME            # logs from last 2 hours
docker cp NAME:/path/file ./local      # copy file from container
docker cp ./file NAME:/path/           # copy file to container
docker inspect NAME                    # full container details (JSON)
docker stats --no-stream               # resource usage snapshot
docker top NAME                        # running processes
```

### 3. Image management

```bash
# Build
docker build -t my-app:latest .
docker build -t my-app:prod -f Dockerfile.prod .
docker build --no-cache -t my-app .              # clean rebuild
DOCKER_BUILDKIT=1 docker build -t my-app .       # faster with BuildKit

# Pull and push
docker pull node:20-alpine
docker login ghcr.io
docker tag my-app:latest registry/my-app:v1
docker push registry/my-app:v1

# Inspect
docker images                          # list local images
docker history IMAGE                   # see layers
docker inspect IMAGE                   # full details

# Cleanup
docker image prune                     # remove dangling (untagged) images
docker image prune -a                  # remove ALL unused images (careful!)
docker image prune -a --filter "until=168h"   # unused images older than 7 days
```

### 4. Docker Compose

```bash
# Start/stop
docker compose up -d                   # start all services detached
docker compose up -d --build           # rebuild images before starting
docker compose down                    # stop and remove containers
docker compose down -v                 # also remove volumes (DESTROYS DATA)

# Monitoring
docker compose ps                      # list services
docker compose logs -f api             # follow logs for specific service
docker compose logs --tail 50          # last 50 lines all services

# Interaction
docker compose exec api /bin/sh        # shell into running service
docker compose run --rm api npm test   # one-off command (new container)
docker compose restart api             # restart specific service

# Validation
docker compose config                  # validate and view resolved config
```

**Minimal compose.yml example:**

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### 5. Volumes and networks

```bash
# Volumes
docker volume ls                       # list volumes
docker volume create mydata            # create named volume
docker volume inspect mydata           # details (mount point, etc.)
docker volume rm mydata                # remove (fails if in use)
docker volume prune                    # remove unused volumes

# Networks
docker network ls                      # list networks
docker network create mynet            # create bridge network
docker network inspect mynet           # details (connected containers)
docker network connect mynet NAME      # attach container to network
docker network disconnect mynet NAME   # detach container
docker network rm mynet                # remove network
docker network prune                   # remove unused networks
```

### 6. Disk usage and cleanup

Always start with a diagnostic before cleaning:

```bash
# Check what's using space
docker system df                       # summary
docker system df -v                    # detailed breakdown

# Targeted cleanup (safe)
docker container prune                 # stopped containers
docker image prune                     # dangling images
docker volume prune                    # unused volumes
docker network prune                   # unused networks

# Aggressive cleanup (confirm with user first!)
docker system prune                    # containers + images + networks
docker system prune -a                 # also unused images
docker system prune -a --volumes       # EVERYTHING — named volumes too
```

**Warning:** Never run `docker system prune -a --volumes` without confirming with the user. This removes named volumes with potentially important data.

**彻底清空（关停某项目后，2026-08-30 验证）**：`image prune -a` 只能删「不被任何容器引用」的镜像——停止的容器仍算引用。所以顺序必须是：先 `docker container prune -f`（删停止容器）→ 再 `docker image prune -a -f`（此时镜像才全部可删）→ `docker builder prune -a -f`（清 build cache）→ `docker volume prune -f`（清未引用卷）。整条下来 `docker system df` 四项归 0B。

**Docker.raw 是稀疏文件**：`ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` 显示的「460G」是逻辑上限不是真实占用；用 `du -sh ~/Library/Containers/com.docker.docker/Data` 看实际占用（清理后约 2.4G）。别被 ls 的 460G 吓到，也别指望删镜像后 Docker.raw 文件本身缩小——稀疏文件不自动缩容，释放的是实际占用不是文件体积。

**bind mount 数据不随容器/镜像删除**：关停项目前先 `docker inspect <容器> --format '{{range .Mounts}}{{.Type}} {{.Source}}{{"\n"}}{{end}}'` 确认数据是 bind mount（Source 指向宿主机目录）还是 named volume。bind mount 数据删容器/镜像无损（如 RKR 的 pgdata 在 `~/rkr_staging/pgdata`）；named volume 需 `docker volume ls` 确认保留。

**彻底清理顺序（2026-08-30 关闭 RKR 实战验证）**——华哥说「关掉没用的容器让出资源」时，完整释放链路：

1. `docker stop <全部容器>`（`restart=unless-stopped` 的手动 stop **不会**自动拉起，安全）
2. `docker container prune -f`（删停止容器 → 让镜像变「未引用」）
3. `docker image prune -a -f`（删所有未引用镜像，**必须**在 container prune 之后，否则镜像仍被停止容器引用删不掉）
4. `docker builder prune -a -f`（清 build cache，可回收 2-4GB）
5. `docker volume prune -f`（清未引用 volume）
清理后 `docker system df` 全 0B。

**Docker.raw 稀疏文件误判**：`ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` 显示 460G 是**逻辑大小**（稀疏文件），不是实际占用。用 `du -sh ~/Library/Containers/com.docker.docker/Data` 才准（清理后实际 ~2.4G）。删镜像后宿主机 `df` 释放的空间 < `docker system df` 显示的镜像总大小，因 Docker Desktop VM 磁盘不自动缩容——这是正常现象，不是清理失败。

**RKR 数据是 bind mount 不是 named volume**：`~/rkr_staging/pgdata`（7.1G）等通过 bind mount 挂进容器（`docker inspect <c> --format '{{range .Mounts}}{{.Type}} {{.Source}}...'` 可查），删容器/镜像**不影响数据**。恢复 = `cd 项目目录 && docker compose up --build -d`（重建几分钟，数据自动挂回完整无缺）。

### 7. Multi-project port allocation (渔芯常态 — READ BEFORE STARTING A NEW PROJECT)

The 渔芯 dev machine routinely runs several long-lived Docker Compose stacks simultaneously (RKR, FindEra, LookForge, AquaForge, 八卦预测工具, etc.). Default ports like `5432` (postgres), `6379` (redis), `8000` (FastAPI), `5173` (Vite), `9200` (elasticsearch), `9000`/`9001` (MinIO) are **already taken** by RKR — `docker compose up` will fail with `Bind for 0.0.0.0:5432 failed: port is already allocated` on a fresh project unless you remap.

**Diagnostic (always run before writing a new project's docker-compose):**

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

Prints which ports are taken. Cross-reference with the standard allocation table below.

**Standard port allocation table (verified 2026-06-28 on this machine):**

| Service | Default | RKR uses | Recommended for new projects |
|---|---|---|---|
| PostgreSQL | 5432 | 5432 (rkr-postgres) | **5433** |
| Redis | 6379 | 6379 (rkr-redis) | **6380** |
| FastAPI / backend | 8000 | 8000 (rkr-backend) | **8001** or **8002** |
| Vite / React frontend | 5173 | 5173 (rkr-frontend) | **5174** or **5175** |
| Elasticsearch | 9200 | 9200 (rkr-elasticsearch) | **9201** |
| MinIO API | 9000 | 9000 (rkr-minio) | **9002** |
| MinIO console | 9001 | 9001 (rkr-minio) | **9003** |
| Postgres +1 (FindEra) | — | 8003 (findera research backend) | **8004+** |
| Vite +1 (FindEra) | — | 5176 (findera research frontend) | **5177+** |

**Pattern: every project's docker-compose.yml + `.env` must**:

1. Use `POSTGRES_PORT`, `REDIS_PORT`, etc. as **variables in `.env`** (not hardcoded in compose).
2. Map `${POSTGRES_PORT:-5433}:5432` (host port from env, container port stays default).
3. Pin to the project's name in the file/volume names — e.g. `iching_postgres_data` not `postgres_data` — so two projects can't collide on a default-named named volume.
4. Set `container_name: iching-postgres` (project prefix) — makes `docker ps` grep-able and avoids Compose auto-generated names conflicting with stale containers.

**`.env` template:**

```bash
POSTGRES_PORT=5433
POSTGRES_USER=iching
POSTGRES_PASSWORD=iching...more debug endpoints) is on **8001** or **8002**. Don't fight RKR for 8000.
- For an analytics/observability tool: consider **9201** (Elasticsearch) or **6379 → 6380** (Redis).
- For a documentation/SEO tool: Vite frontend can be on **5174**, backend on **8001** if it's lightweight.

**Critical: re-run `docker ps` before committing to a port** — the table above is from 2026-06-28; new projects may have grabbed the next available slot.

## Celery Worker Management (Docker-based stacks)

RKR平台等使用 Docker Compose 部署的 Celery 集群：

```bash
# 查看所有 celery 相关容器状态
docker ps -a --format "{{.Names}}\t{{.Status}}" | grep -i celery

# 检查 worker 是否在跑（注意：worker 进程名不一定是"celery"）
docker exec CONTAINER ps aux | grep -E "celery|worker" | grep -v grep

# 检查 beat 是否在跑（celery beat 负责生成定时任务）
docker ps -a --format "{{.Names}}\t{{.Status}}" | grep celery-beat

# 重启 worker（**不能用 `restart` — 不读 .env**，详见 ⚠️ Pitfall 2）
docker stop rkr-celery-worker
docker rm rkr-celery-worker
docker compose -f /path/to/docker-compose.yml up -d --no-deps celery-worker

# 查看 worker 日志
docker logs --tail 50 -f rkr-celery-worker
```

**Redis 队列深度**：
```bash
docker exec rkr-redis redis-cli -a PASSWORD LLEN celery
```

## RKR 平台 postgres 连接

RKR 数据库名是 `rkr_knowledge`（不是 `rkr`），用户名 `rkr_user`，密码 `rkr_dev_2026`：

```bash
docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -c "SELECT processing_status, COUNT(*) FROM documents GROUP BY processing_status;"
```

查看表结构：`\d documents`

**数据零丢失验证（cold-start / 重建后必做）**：daemon 恢复、health 端点 200 只证明「服务起来了」，不能证明「数据没丢」。用一条计数查询确认 documents + chunks 只增不减：

```bash
docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -c \
  "SELECT (SELECT count(*) FROM documents) AS docs, (SELECT count(*) FROM document_chunks) AS chunks;"
```

判断规则：计数**单调不减**即零丢失（正常每天会微增，因补齐/同步任务在跑）；若较上次心跳的基线数字**下降** = 数据丢失，需告警。基线可从上一轮心跳记录或 `~/rkr_staging/` 备份对照。这个验证比 curl health 更重要，是「自愈声明可核实」的关键证据。

## 大目录 listing 超时问题

容器内 staging 目录文件数过多时，`ls` 会超时。替代方案：

```bash
# 统计文件数量（不过滤，很快）
docker exec CONTAINER find /app/staging -maxdepth 1 -type f 2>/dev/null | wc -l

# 前N个文件
docker exec CONTAINER find /app/staging -maxdepth 1 -type f 2>/dev/null | head -20

# 查看目录大小（排除子目录）
docker exec CONTAINER du -sh /app/staging 2>/dev/null
```

**解除卡住容器的方法**：当容器内目录卡住时（可能是 NFS/overlay 问题），直接 `docker stop && docker rm` 容器，目录会自动解除占用。

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Container exits immediately | Main process finished or crashed | Check `docker logs NAME`, try `docker run -it --entrypoint /bin/sh IMAGE` |
| "port is already allocated" on a NEW project | An existing project already binds that port (e.g. RKR on 5432/6379/8000/5173) | See **Multi-project port allocation** (§7) — pick a free port and pin it in `.env` |
| "no space left on device" | Docker disk full | `docker system df` then targeted prune |
| Can't connect to container | App binds to 127.0.0.1 inside container | App must bind to `0.0.0.0`, check `-p` mapping |
| Permission denied on volume | UID/GID mismatch host vs container | Use `--user $(id -u):$(id -g)` or fix permissions |
| Compose services can't reach each other | Wrong network or service name | Services use service name as hostname, check `docker compose config` |
| Build cache not working | Layer order wrong in Dockerfile | Put rarely-changing layers first (deps before source code) |
| Image too large | No multi-stage build, no .dockerignore | Use multi-stage builds, add a .dockerignore |
| `${VAR}:5432` no default fallback → silent port conflict | Pasting without `:-5433` default in compose; `.env` missing the line | Always use `${POSTGRES_PORT:-5433}:5432` syntax |
| Two projects share a default-named volume (e.g. both `postgres_data`) | Generic volume names collide across stacks | Project-prefix the volume name: `iching_postgres_data` (and `name:` field in compose to make it sticky) |
| pgvector extension missing after first run | `pgvector/pgvector:pg16` image has the lib, but `CREATE EXTENSION vector` must run | Either mount `01_extensions.sql` to `/docker-entrypoint-initdb.d` (first-run only) or run `docker exec iching-postgres psql ... -c 'CREATE EXTENSION vector;'` manually for an already-running container |
| Edited `.env` but container config unchanged | `environment:` in `docker-compose.yml` **overrides `env_file:`**. Editing only `.env` is silently a no-op | See ⚠️ Pitfall 1 — edit both files, then `--force-recreate`. Verify with `docker exec NAME printenv YOUR_VAR` |
| `docker compose restart` doesn't pick up new `.env` | `restart` reuses existing container, including its stored env vars | See ⚠️ Pitfall 2 — use `up -d --force-recreate --no-deps SVC` after editing config |
| Redis queue ballooning with no log activity | Beat is still running but worker pool was stopped/removed without replacement | See ⚠️ Pitfall 3 — always recreate workers immediately; check `redis-cli LLEN celery` |

### Recovering a container's bind-mount source path

When a task references a project directory that you can't find on the host (e.g. a cron instruction lists `~/Desktop/.../FindEra/` but the folder has moved or you have the wrong path), the **bind mount source** of the running container is the most reliable source of truth — it always matches whatever the operator actually deployed.

```bash
# Get bind-mount source paths as JSON
docker inspect NAME --format '{{json .Mounts}}' | python3 -m json.tool

# Just the source paths, one per line (handy for grepping)
docker inspect NAME --format '{{range .Mounts}}{{if eq .Type "bind"}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}{{end}}'
```

The `Source` field is the host path that the operator bind-mounted into `Destination` inside the container — it points at the real project root, even if you've been told the wrong directory. This is faster and more reliable than `find /` for projects that may live under long CJK paths with spaces.

The same trick also surfaces named-volume mount points (`docker volume inspect VOLUME` for the same info), but bind mounts are the ones most likely to map to a user-facing project directory.

> ⚠️ The JSON output can include sensitive-looking strings (paths under `$HOME`, container IDs). When piping into shell, prefer `--format '{{...}}'` extraction over dumping the raw JSON if you'll echo it back to a notification or log.

## Docker Desktop Cold-Start Recovery

When Docker Desktop itself has been shut down (not just containers stopped), the full recovery sequence is needed. This is distinct from restarting a running container.

```bash
# Step 1: Launch Docker Desktop (non-blocking)
open -a Docker

# Step 2: Wait for Docker engine to respond
for i in $(seq 1 30); do
  if docker ps 2>/dev/null >/dev/null; then
    echo "Docker ready (${i}s)"
    break
  fi
  sleep 2
done

# Step 3: Switch to desktop-linux context
docker context use desktop-linux

# Step 4: Wait for key containers to be healthy
for i in $(seq 1 30); do
  status=$(docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
  # Check specific containers that matter
  echo "$status" | grep -c "healthy" 2>/dev/null && break
  sleep 2
done

# Step 5: Verify all containers are up
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Step 6: Verify API endpoints respond
curl -s http://localhost:8000/api/v1/health
curl -s http://localhost:8003/api/v1/health
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/
```

**Key observations (渔芯, 2026-07)**: After `open -a Docker`, do NOT run `docker context use desktop-linux` immediately — the engine socket may not exist yet. The wait-loop in Step 2 is mandatory. After Docker engine responds, containers appear with `(health: starting)` status — APIs may return `Connection refused` until they transition to `(healthy)`. Always verify with `curl` after `docker ps` shows healthy.

### Cold-start with wiped containers AND images (2026-08-30 实战)

`open -a Docker` only recovers the **daemon**. It does **not** resurrect containers or images that were removed while Docker was down. Two distinct post-recovery states:

| State after `open -a Docker` | Meaning | Fix |
|---|---|---|
| `docker ps -a` shows project containers (`(health: starting)` → `healthy`) | Containers persisted; pure cold-start | Wait + `docker context use desktop-linux` + verify with `curl` |
| `docker ps -a` **empty** AND `docker images` lacks the project's images (e.g. no `rkr-*`) | Containers removed AND images pruned | Full rebuild: `cd <project> && docker compose up --build -d` |

**Diagnose before assuming cold-start alone is enough:**
```bash
docker ps -a --format "{{.Names}}\t{{.Status}}"     # empty = containers gone
docker images --format "{{.Repository}}" | grep -i rkr   # no rkr-* = images pruned
```

**Key reassurance — rebuild is data-safe**: named data volumes (`pgdata` / `minio_data` / `es_data` / `redis_data`, usually under `~/rkr_staging/` or referenced in the project's `docker-compose.yml` `volumes:` block) survive independently of containers/images. `docker compose up --build -d` re-mounts them, so the DB/objects/indexes come back intact. Confirm volumes still exist first: `docker volume ls`. Only `docker system prune -a --volumes` (or a volume prune) destroys them.

**Real case**: 老莫 heartbeat 2026-08-30 found RKR `:8000` down (`curl` → `000`). Root cause chain: Docker Desktop not running → `open -a Docker` recovered daemon (v29.4.3) in ~10s → but `docker ps -a` was empty and `docker images` held only `geo-backend`/`geo-dashboard`/`zhiyu-ai-learning`/`pgvector`/`redis` (no `rkr-*`). Conclusion: full `docker compose up --build -d` rebuild required. Flagged for follow-up rather than run in-cron, because a cold build of the full RKR stack (FastAPI backend + React/Vite frontend + ES + celery pools) exceeds a single cron heartbeat's time budget — see `long-running-task` skill.

### Chronic daemon bounce — recovery is NOT one-shot (2026-09-04 实战, 10+ heartbeat rounds)

On this host Docker Desktop doesn't just "recover once" — the daemon bounces
repeatedly. Observed UP-cycle lengths: **14min → 7h46m** (R190 08:01 UP → R191
08:14 DOWN; R198 13:09 recovered → R199 13:18 bounced; UP again by ~13:40).
Operational stance after any recovery: **expect a re-bounce; don't mark the
incident closed.**

**Restart policy determines what survives a bounce:**

| restart policy | After daemon bounce | Example |
|---|---|---|
| `no` | `Exited (255)` — stays down until explicit `docker start` | entire rkr-* + research-* stack |
| `unless-stopped` / compose-managed | auto-returns on daemon re-up | lookforge-*, znt-* |

So after every daemon re-up, `docker ps -a` (not just `docker ps`) — any
`Exited (255)` containers need explicit start in dependency order
(infra: postgres/redis/minio/elasticsearch → wait → app/celery pools →
side stacks), then curl the health endpoints. See rkr-platform SKILL.md 方式二
for the RKR-specific sequence.

**False-DOWN diagnosis trap (profile `$HOME` hijack)**: under a hijacked
`$HOME` (`~/.hermes/profiles/<agent>/home`), the docker CLI looks for the
socket at the hijacked path and reports `no such file or directory` **even
when the daemon is UP** at the real home — heartbeat rounds R178/R191
mis-diagnosed daemon DOWN this way. Four-point check before declaring DOWN:

```bash
export HOME=/Users/hua                          # override hijack first
ls -la /Users/hua/.docker/run/docker.sock        # 1. socket exists?
curl --unix-socket /Users/hua/.docker/run/docker.sock --max-time 5 http://localhost/_ping  # 2. OK?
docker ps --format '{{.Names}}'                  # 3. CLI works now?
ps aux | grep com.docker.backend | grep -v grep  # 4. backend process alive?
```

All four DOWN = daemon really down (then `open -a Docker` + start exited
containers if in a work window); any disagreement = diagnosis error, not a
docker incident.

## Verification

After any Docker operation, verify the result:

- **Container started?** → `docker ps` (check status is "Up")
- **Logs clean?** → `docker logs --tail 20 NAME` (no errors)
- **Port accessible?** → `curl -s http://localhost:PORT` or `docker port NAME`
- **Image built?** → `docker images | grep TAG`
- **Compose stack healthy?** → `docker compose ps` (all services "running" or "healthy")
- **Disk freed?** → `docker system df` (compare before/after)
- **Multi-project port not colliding?** → `docker ps` should show the project's container on its dedicated host port, not on a port another stack already binds
- **Env vars actually changed?** → `docker exec NAME printenv | grep YOUR_VAR` (see pitfall below)

## ⚠️ Critical Pitfalls (most-encountered)

These three pitfalls caused **multi-hour debugging delays** for 渔芯 in 2026-06/07. Read every one before editing compose for a running service.

### Pitfall 1: `environment:` in compose overrides `env_file:`

**The trap.** When the same key appears in *both* `env_file: - .env` and the `environment:` block of `docker-compose.yml`, **the `environment:` value wins** — silently. Editing `.env` alone produces zero visible effect inside the container, and you'll spend an hour wondering why your fix "didn't take."

**How it manifests.** You edit `.env`, `docker compose restart`, see the new value in your editor, look at container logs and worker behavior — still using the old config. Sometimes there is NO error; the container just keeps behaving per the older setting.

**How to detect fast.** After editing `.env`:

```bash
# Compare what YOU think the container sees vs what it actually sees
grep '^OLLAMA_HOST' .env
docker exec CONTAINER printenv OLLAMA_HOST
# If the two disagree → compose.yml is overriding you
```

**How to fix.** Search the compose file for the variable and change it both places. Multi-edit-safe pattern:

```bash
grep -n 'YOUR_VAR' docker-compose.yml   # find every duplicate
```

Edit both. Then use `--force-recreate` (see Pitfall 2) to actually apply.

**Real 渔芯 case (2026-07-01).** RKR `.env` had `OLLAMA_HOST=192.168.65.254`, and `docker-compose.yml` hardcoded the same value three times across `processing-pool` / `processing-pool-2` / `staging-pool`. Changing only `.env` left the actual container config unchanged for ~10 minutes before the override was caught.

### Pitfall 2: `docker compose restart` does NOT re-read `.env` or image changes

**The trap.** `docker compose restart` reuses the existing container's stored env vars. If you changed `.env` or rebuilt an image, restart alone is a no-op for env changes — you'll keep seeing the old value in `docker exec printenv`.

**The escalation ladder:**

| Want | Command | What it actually does |
|---|---|---|
| Restart in place (config unchanged) | `docker compose restart SVC` | Reuses container, reuses env vars, reuses image |
| Apply new `.env` values | `docker compose up -d --force-recreate --no-deps SVC` | Stop + rm container, recreate from current compose, **read fresh `.env`** |
| Apply new image (rebuild) | `docker compose up -d --build SVC` | Rebuild image, recreate container |
| Fresh start, full reset | `docker compose down && docker compose up -d` | Stop + remove all containers, network, etc. **Volumes preserved** |

**`--no-deps` matters.** Without it, Compose may also try to recreate `postgres` / `redis` / etc., which fails healthchecks on the running services. Use `--no-deps SVC` when you only want to swap one worker.

**Quick recipe for safe worker-pool config swap** (the most common 渔芯 case):

```bash
# 1) Verify the new env in .env
grep '^YOUR_VAR' .env

# 2) Stop without auto-restart
docker compose stop SVC

# 3) Remove the container (volumes untouched)
docker compose rm -f SVC

# 4) Recreate from current compose + .env, no dependency churn
docker compose up -d --no-deps SVC

# 5) Verify env actually changed
docker exec SVC printenv YOUR_VAR
# Should now match your .env value

# 6) Verify logs are clean (no crashes on startup)
docker logs --tail 50 SVC
```

**Real 渔芯 case (2026-07-01).** First attempt was `docker compose restart processing-pool`; container came back with `printenv` still showing old `embo-02` (correct value in `.env` was `embo-01`). Took 5 extra minutes to diagnose.

### Pitfall 3: Celery worker pools that share a queue — when one stalls, all stall

**The trap.** RKR's `celery-beat` schedules tasks onto Redis queues consumed by `processing-pool` and `processing-pool-2`. If you `docker stop` or `docker rm` both pools and forget to recreate them, **beat keeps emitting tasks into the void** — Redis queue depth grows, no one is consuming, and on next restart the workers must chew through a giant backlog.

**How to detect.** After removing both pools, check the queue:

```bash
docker exec rkr-redis redis-cli -a PASSWORD LLEN celery
# If this number is growing while no workers run, you're accumulating debt
```

**How to fix.** Always recreate the worker pool immediately after removal — never leave beat running without a consumer. If the queue is large, expect 1–2 hours of catch-up after restart; this is normal.

**Why this matters.** Operators sometimes delete a worker to "free memory" without realizing it'll come back as a much-bigger problem (Redis queue clogging + downstream per-job CPU spikes when the new pool starts).

## Dockerfile Optimization Tips

When reviewing or creating a Dockerfile, suggest these improvements:

1. **Multi-stage builds** — separate build environment from runtime to reduce final image size
2. **Layer ordering** — put dependencies before source code so changes don't invalidate cached layers
3. **Combine RUN commands** — fewer layers, smaller images
4. **Use .dockerignore** — exclude `node_modules`, `.git`, `__pycache__`, etc.
5. **Pin base image versions** — `node:20-alpine` not `node:latest`
6. **Run as non-root** — add `USER` instruction for security
7. **Use slim/alpine bases** — `python:3.12-slim` not `python:3.12`

## Further Reading

- `references/multi-project-ports.md` — full port allocation rationale, cross-project integration patterns, and a worked example from the 八卦预测工具 project (validated 2026-06-28).