## 会话管理功能
用户可以同时拥有多个会话

| 功能 | 请求方式 | 请求路径 |
| :--- | :--- | :--- |
| 创建会话 | POST | `/api/v1/chat-threads` |
| 查询会话列表 | GET | `/api/v1/chat-threads` |
| 重命名会话 | PATCH | `/api/v1/chat-threads/{thread_id}` |
| 删除会话 | DELETE | `/api/v1/chat-threads/{thread_id}` |

会话数据分为两部分
- 会话元数据：所属用户、会话的名称、创建时间、更新时间等信息，存储在 `chat_threads` 表中
- 会话历史消息：属于消息数据，将来用 LangChain 来管理

目前暂时不实现登录功能，前端在每次请求中固定携带 `x-user-id` 请求头，用它模拟当前登录用户，这里默认使用用户 ID `1`，后续接入真实认证时再替换

## 接口设计

[会话管理模块](https://my.feishu.cn/wiki/GvHtwszVKiSj2TkJs6lcgrRYn2b)

在 `app/modules` 下新建 `chat_thread` 包，并创建本章需要的文件：

```
app/modules/chat_thread/
├── __init__.py
├── models.py
├── repository.py
├── router.py
├── schemas.py
└── service.py
```

### 创建会话

<img alt="创建会话.png" src="创建会话.png" width="1000"/>

### 查询会话列表

<img alt="查询会话列表.png" src="查询会话列表.png" width="1000"/>


### 重命名会话

<img alt="img_2.png" src="重命名会话.png" width="1000"/>

### 删除会话

<img alt="删除会话.png" src="删除会话.png" width="1000"/>