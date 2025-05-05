# Amazon Q 实现的 Chat Session 和 Chat History 路由

根据项目需求，我实现了两个新的路由文件：

## 1. chat_session.py

这个路由文件处理聊天会话的 CRUD 操作，包括：

- `GET /` - 获取聊天会话列表，支持分页
- `GET /{session_id}` - 获取单个聊天会话详情
- `POST /` - 创建新的聊天会话
- `PUT /{session_id}` - 更新聊天会话信息
- `DELETE /{session_id}` - 删除聊天会话及其历史记录（通过数据库级联删除）

## 2. chat_history.py

这个路由文件处理聊天历史记录的 CRUD 操作，包括：

- `GET /` - 获取指定会话的聊天历史记录，支持分页
- `GET /{history_id}` - 获取单条聊天历史记录详情
- `POST /` - 创建新的聊天历史记录
- `PUT /{history_id}` - 更新聊天历史记录
- `DELETE /{history_id}` - 删除单条聊天历史记录

## 实现细节

- 参考了现有的 tool.py 路由实现方式
- 使用了项目中的 db 工具类进行数据库操作
- 添加了必要的参数验证和错误处理
- 在创建聊天历史记录时，会自动更新对应会话的更新时间
- 处理了 JSON 参数的序列化和反序列化

## 注意事项

- 需要在主应用中注册这两个路由
- 确保数据库中已创建了相应的表（根据 sql/chat-history.sql）
