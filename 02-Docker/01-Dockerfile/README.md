## Dockerfile
用 Dockerfile 来描述每层内容，Docker 会根据 Dockerfile 生成镜像

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| **FROM** | 指定基础镜像 | `FROM centos:7` |
| **ENV** | 设置环境变量，可在后面指令使用 | `ENV key value` |
| **COPY** | 拷贝本地文件到镜像的指定目录 | `COPY ./hm.tar /tmp` |
| **RUN** | 执行Linux的shell命令，一般是安装过程的命令 | `RUN tar -xvf /tmp/hm.tar && pip install uv && uv sync` |
| **EXPOSE** | 指定容器运行时监听的端口，是给镜像使用者看的 | `EXPOSE 8000` |
| **ENTRYPOINT** | 镜像中应用的启动命令，容器运行时调用 | `ENTRYPOINT uv run xxx` |

例如，要基于 python:3.12-slim 镜像来构建一个 Python 应用，其 Dockerfile 内容如下：
```dockerfile
# 使用 python:3.12-slim 作为基础镜像
From python:3.12-slim
# 设置应用目录
WORKDIR /app 
# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# 拷贝依赖管理文件
COPY pyproject.toml ./
# 安装依赖
RUN uv sync --no-dev
# 拷贝源码
COPY src/ ./src/
# 暴露端口
EXPOSE 8000
# 运行命令
ENTRYPOINT ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dockerfile文件编写好了之后，就可以使用如下命令来构建镜像了。
```shell
docker build -t [镜像名]:[标签] .
```
- `-t [repository]:[tag]`：是给镜像起名，不指定tag时，默认为latest
- `.`：是指定Dockerfile所在目录，如果就在当前目录，则指定为"."

```shell
docker build -t backend .
docker run -d --name backend -p 8000:8000 --env-file .env.prod backend
docker inspect backend --format '{{range .Config.Env}}{{println .}}{{end}}' # 查看容器环境变量
```