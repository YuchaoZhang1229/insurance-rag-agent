## Docker Compose
Docker Compose就可以帮助我们实现**多个相互关联的Docker容器的快速部署**

### 7.1 基础语法

| docker run 参数 | docker compose 指令 | 说明 |
| :--- | :--- | :--- |
| `--name` | `container_name` | 容器名称 |
| `-p` | `ports` | 端口映射 |
| `-e` | `environment` | 环境变量 |
| `-v` | `volumes` | 数据卷配置 |
| `--network` | `networks` | 网络 |

举例来说，用 `docker run` 部署 Nginx 的命令如下：

```shell
docker run -d \
 --name chatbot-frontend\
 -v /root/robot/frontend/public:/usr/share/nginx/html \
 -v /root/robot/frontend/nginx.conf:/etc/nginx/nginx.conf \
 --network my_network \
 -p 80:80 \
nginx:latest
```

如果用 `docker-compose.yml` 文件来定义，就是这样：

```yaml
services:
  frontend:
    image: "nginx:latest"
    container_name: chatbot-frontend
    ports:
      - "80:80"
    volumes:
      - "/root/robot/frontend/public:/usr/share/nginx/html"
      - "/root/robot/frontend/nginx.conf:/etc/nginx/nginx.conf"
    networks:
      - my_network
networks:
  my_network:
    name: my_network
```
### 7.2 基础命令
编写好 `docker-compose.yml` 文件，就可以部署项目了。语法如下：
```shell
docker compose [OPTIONS] [COMMAND]
```
其中，OPTIONS和COMMAND都是可选参数，比较常见的有：

| 类型       | 参数或指令 | 说明 |
|:---------| :--- | :--- |
| Options  | `-f` | 指定compose文件的路径和名称 |
|          | `-p` | 指定project名称。project就是当前compose文件中设置的多个service的集合，是逻辑概念 |
| Commands | `up` | 创建并启动所有service容器 |
|          | `down` | 停止并移除所有容器、网络 |
|          | `ps` | 列出所有启动的容器 |
|          | `logs` | 查看指定容器的日志 |
|          | `stop` | 停止容器 |
|   | `start` | 启动容器 |
|  | `restart` | 重启容器 |
|  | `top` | 查看运行的进程 |
|  | `exec` | 在指定的运行中容器中执行命令 |

### 7.3 教学演示
```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: chatbot-mysql
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: robot
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: chatbot-backend
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    depends_on:
      mysql:
        condition: service_healthy

  frontend:
    image: nginx:latest
    container_name: chatbot-frontend
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/public:/usr/share/nginx/html:ro
    depends_on:
      - backend

volumes:
  mysql_data:
```

```shell
docker compose up -d
```