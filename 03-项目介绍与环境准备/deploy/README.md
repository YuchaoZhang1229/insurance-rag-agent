
## 一键部署
修改 `./milvus/user.yaml` 中 `dashscope_apikey` 的值
```shell
docker compose up -d
```

## 连接 postgres
- 数据库名：insurance
- 用户名：insurance
- 密码：insurance123

## 连接 Milvus
Milvus有一个web控制台，端口是3000，在浏览器输入地址：http://localhost:3000 即可访问

首次访问，需要注册一个管理员的用户名和密码，密码必须8位以上，且必须有大写、小写、数字、下划线中的3个类型。admin/admin_123

