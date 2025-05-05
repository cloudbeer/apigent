# apigent

## 运行项目

```shell
uv sync
```

```shell
source .venv/bin/activate
```

```shell
fastapi run main.py

# or dev
fastapi dev main.py
```

## 环境变量配置

开发环境下，请按照以下步骤配置环境变量：

1. 在项目根目录下复制 `.env.example` 文件并重命名为 `.env`
   ```shell
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的实际配置信息

### 环境变量说明

```
# 应用运行端口
PORT=8081

# 数据库连接字符串
# 格式：postgresql://用户名:密码@主机地址:端口/数据库名?sslmode=disable
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=disable

# OpenAI API密钥（必填）
OPENAI_API_KEY=your_openai_api_key

# OpenAI API基础URL（可选，用于自定义API端点）
OPENAI_API_BASE_URL=your_api_base_url

# 嵌入模型名称
EMBEDDING_MODEL=model_name

# 文本生成模型名称
TEXT_GENERATION_MODEL=model_name

# 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
LOG_LEVEL=ERROR
```

**注意**：请勿将包含敏感信息的 `.env` 文件提交到版本控制系统中。该文件已在 `.gitignore` 中配置为忽略。