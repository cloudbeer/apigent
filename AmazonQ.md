# APIGent 项目分析报告

## 项目概述

**项目名称**: APIGent  
**版本**: 0.1.0  
**描述**: NL to API Agent - 自然语言到API代理服务  
**Python版本要求**: >=3.12  

APIGent 是一个基于 FastAPI 的智能API代理服务，通过自然语言处理和向量检索技术，帮助用户通过自然语言描述来调用相应的API工具。

## 核心技术栈

### 后端框架
- **FastAPI**: 现代、高性能的Python Web框架，支持自动API文档生成
- **Python 3.12+**: 使用最新的Python版本特性

### 数据库技术
- **PostgreSQL**: 主数据库，存储工具、分类、字段等元数据
- **pgvector**: PostgreSQL向量扩展，支持向量相似度搜索
- **psycopg[binary,pool]**: PostgreSQL数据库连接器，支持连接池

### AI/ML 集成
- **OpenAI API**: 集成GPT模型进行自然语言处理和对话
- **向量嵌入**: 使用OpenAI的embedding模型进行文本向量化
- **jieba**: 中文分词库，用于中文文本处理

### 前端技术
- **Jinja2**: 模板引擎，用于服务端渲染HTML页面
- **静态文件服务**: 通过FastAPI StaticFiles提供静态资源

### 其他依赖
- **python-dotenv**: 环境变量管理
- **babel**: 国际化支持
- **pygments**: 代码高亮

## 项目架构

### 目录结构
```
apigent/
├── app/                    # 应用核心代码
│   ├── models/            # 数据模型定义
│   ├── routers/           # API路由处理
│   ├── utils/             # 工具函数
│   └── translations/      # 国际化翻译文件
├── pages/                 # HTML模板页面
├── static/                # 静态资源文件
├── sql/                   # 数据库脚本
├── bin/                   # 可执行脚本
└── main.py               # 应用入口文件
```

### 核心模块分析

#### 1. 路由模块 (app/routers/)
- **chat.py**: 聊天完成API，处理自然语言对话
- **chat_session.py**: 聊天会话管理
- **chat_history.py**: 聊天历史记录管理
- **tool.py**: API工具管理
- **category.py**: 工具分类管理
- **field.py**: 字段管理
- **pages.py**: 页面路由

#### 2. 数据模型 (app/models/)
- **chat.py**: 聊天相关数据模型
- **tool.py**: 工具数据模型
- **category.py**: 分类数据模型
- **field.py**: 字段数据模型
- **tool_embedding.py**: 工具向量嵌入模型

#### 3. 工具函数 (app/utils/)
- **ai.py**: AI相关功能，OpenAI API集成
- **pg.py**: PostgreSQL数据库操作
- **retrieve.py**: 向量检索功能
- **preproccess.py**: 数据预处理
- **i18n.py**: 国际化支持
- **code_to_image.py**: 代码转图片功能

### 数据库设计

#### 数据库扩展
- **pgvector**: PostgreSQL向量扩展，支持向量相似度搜索和高维向量存储

#### 核心表结构详解

##### 1. 工具分类表 (apigent_category)
存储API工具的分类信息，用于组织和管理不同类型的工具。

```sql
CREATE TABLE apigent_category (
    id SERIAL PRIMARY KEY,                    -- 分类ID，主键
    name VARCHAR(255) NOT NULL UNIQUE,        -- 分类名称，唯一
    description TEXT,                         -- 分类描述
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 自增主键
- `name`: 分类名称，必须唯一
- `description`: 分类的详细描述
- `created_at/updated_at`: 创建和更新时间戳

##### 2. API工具表 (apigent_tool)
存储API工具的基本信息，包括URL、HTTP方法、向量嵌入等。

```sql
CREATE TABLE apigent_tool (
    id BIGSERIAL PRIMARY KEY,                 -- 工具ID，主键
    name VARCHAR(255) NOT NULL UNIQUE,        -- 工具名称，唯一
    description TEXT,                         -- 工具描述
    url VARCHAR(1024) NOT NULL,               -- API端点URL
    http_method VARCHAR(20) NOT NULL,         -- HTTP方法(GET/POST/PUT/DELETE等)
    http_context JSONB DEFAULT '{}'::jsonb,   -- HTTP请求额外数据(认证、headers、默认参数等)
    category_id INTEGER REFERENCES apigent_category(id), -- 关联分类ID
    embedding vector(1536),                   -- 1536维向量嵌入
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 64位自增主键
- `name`: 工具名称，系统内唯一标识
- `description`: 工具功能描述
- `url`: API的完整URL地址
- `http_method`: HTTP请求方法
- `http_context`: JSONB格式存储额外的HTTP配置信息
- `category_id`: 外键关联到分类表
- `embedding`: 1536维向量，用于语义搜索

##### 3. 工具向量嵌入表 (apigent_tool_embedding)
存储工具的多种文本表述及其对应的向量嵌入，支持更灵活的语义搜索。

```sql
CREATE TABLE apigent_tool_embedding (
    id BIGSERIAL PRIMARY KEY,                 -- 向量记录ID
    tool_id BIGINT REFERENCES apigent_tool(id) ON DELETE CASCADE, -- 关联工具ID
    text_variant TEXT NOT NULL,               -- 文本表述变体
    is_original BOOLEAN DEFAULT FALSE,        -- 是否为原始表述
    category_id INTEGER REFERENCES apigent_category(id), -- 关联分类ID
    embedding vector(1536),                   -- 1536维向量嵌入
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 向量记录的唯一标识
- `tool_id`: 关联的工具ID，级联删除
- `text_variant`: 工具的不同文本表述（如同义词、不同描述方式）
- `is_original`: 标识是否为工具的原始描述
- `category_id`: 分类关联
- `embedding`: 对应文本的向量表示

**索引优化:**
```sql
-- 向量相似度搜索索引（IVFFlat算法）
CREATE INDEX ON apigent_tool_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- 工具ID索引，加速连接查询
CREATE INDEX ON apigent_tool_embedding (tool_id);
-- 原始表述索引，便于分类查询
CREATE INDEX ON apigent_tool_embedding (is_original);
```

##### 4. 字段定义表 (apigent_field)
存储API工具的参数字段定义，支持完整的OpenAPI规范。

```sql
CREATE TABLE apigent_field (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT REFERENCES apigent_tool(id) ON DELETE CASCADE, -- 关联工具ID
    name VARCHAR(255) NOT NULL,               -- 字段名称
    description TEXT,                         -- 字段描述
    data_type VARCHAR(50) NOT NULL,           -- 数据类型(string/integer/boolean等)
    format VARCHAR(50),                       -- OpenAPI格式(date-time/email/uuid等)
    is_required BOOLEAN DEFAULT false,        -- 是否必填
    is_array BOOLEAN DEFAULT false,           -- 是否为数组类型
    array_items_type VARCHAR(50),             -- 数组元素类型
    array_items_format VARCHAR(50),           -- 数组元素格式
    default_value TEXT,                       -- 默认值
    enum_values JSONB,                        -- 枚举值列表
    -- 数值约束
    minimum NUMERIC,                          -- 最小值
    maximum NUMERIC,                          -- 最大值
    exclusive_minimum BOOLEAN DEFAULT false,  -- 是否排除最小值
    exclusive_maximum BOOLEAN DEFAULT false,  -- 是否排除最大值
    multiple_of NUMERIC,                      -- 倍数约束
    -- 字符串约束
    min_length INTEGER,                       -- 最小长度
    max_length INTEGER,                       -- 最大长度
    pattern TEXT,                             -- 正则表达式模式
    -- 数组约束
    min_items INTEGER,                        -- 最小元素数
    max_items INTEGER,                        -- 最大元素数
    unique_items BOOLEAN DEFAULT false,       -- 元素是否唯一
    -- 其他属性
    nullable BOOLEAN DEFAULT false,           -- 是否可为null
    deprecated BOOLEAN DEFAULT false,         -- 是否已废弃
    allow_empty_value BOOLEAN DEFAULT false,  -- 是否允许空值
    -- OpenAPI参数样式
    style VARCHAR(50),                        -- 参数样式
    explode BOOLEAN DEFAULT false,            -- 是否展开数组/对象
    allow_reserved BOOLEAN DEFAULT false,     -- 是否允许保留字符
    -- 引用和示例
    schema_ref TEXT,                          -- 引用其他schema
    example TEXT,                             -- 示例值
    reference_tool_id BIGINT REFERENCES apigent_tool(id), -- 引用工具ID
    reference_path TEXT,                      -- 引用路径
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段分类说明:**
- **基础信息**: name, description, data_type, format
- **必填性**: is_required, nullable, allow_empty_value
- **数组支持**: is_array, array_items_type, array_items_format
- **数值约束**: minimum, maximum, exclusive_minimum, exclusive_maximum, multiple_of
- **字符串约束**: min_length, max_length, pattern
- **数组约束**: min_items, max_items, unique_items
- **OpenAPI规范**: style, explode, allow_reserved
- **引用机制**: schema_ref, reference_tool_id, reference_path

##### 5. 聊天会话表 (apigent_chat_session)
管理用户的聊天会话信息。

```sql
CREATE TABLE apigent_chat_session (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE, -- 会话唯一标识
    title VARCHAR(255) NOT NULL,             -- 会话标题
    case_summary TEXT,                       -- 会话总结
    status INTEGER NOT NULL DEFAULT 0,       -- 会话状态(0:活跃, 1:已结束等)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `session_id`: 会话的唯一字符串标识符
- `title`: 会话的显示标题
- `case_summary`: 会话内容的摘要总结
- `status`: 会话状态标识

##### 6. 聊天历史记录表 (apigent_chat_history)
存储详细的聊天交互记录和工具调用信息。

```sql
CREATE TABLE apigent_chat_history (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES apigent_chat_session(session_id) ON DELETE CASCADE,
    request_content JSONB NOT NULL,          -- 用户请求内容(JSON格式)
    response_content JSONB,                  -- AI响应内容(JSON格式)
    tool_name VARCHAR(255),                  -- 调用的工具名称
    parameters JSONB,                        -- 工具调用参数(JSON格式)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `session_id`: 关联会话ID，支持级联删除
- `request_content`: 用户的完整请求内容，JSONB格式存储
- `response_content`: AI的响应内容，包括文本和工具调用信息
- `tool_name`: 如果调用了工具，记录工具名称
- `parameters`: 工具调用时使用的参数

#### 数据库索引策略

##### 性能优化索引
```sql
-- 字段表索引
CREATE INDEX ON apigent_field (tool_id);     -- 按工具查询字段
CREATE INDEX ON apigent_field (name);        -- 按字段名查询
CREATE INDEX ON apigent_field (data_type);   -- 按数据类型查询

-- 聊天相关索引
CREATE INDEX ON apigent_chat_session (session_id);  -- 会话ID查询
CREATE INDEX ON apigent_chat_history (session_id);  -- 历史记录会话查询
CREATE INDEX ON apigent_chat_history (tool_name);   -- 按工具名查询历史
```

##### 向量搜索索引
```sql
-- IVFFlat向量索引，适合中等规模数据的相似度搜索
CREATE INDEX ON apigent_tool_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### 向量检索特性
- **维度**: 1536维向量（对应OpenAI text-embedding-ada-002模型）
- **相似度算法**: 余弦相似度 (vector_cosine_ops)
- **索引算法**: IVFFlat，适合中等规模数据集
- **索引参数**: lists=100，将向量空间分为100个聚类
- **搜索性能**: 支持高效的近似最近邻搜索


#### 数据库初始化
1. **基础结构**: 执行 `sql/meta.sql` 创建工具管理相关表
2. **聊天功能**: 执行 `sql/chat-history.sql` 创建聊天会话和历史表
3. **扩展要求**: 需要安装 pgvector 扩展支持向量操作

## 核心功能

### 1. 自然语言到API转换
- 用户输入自然语言描述
- 系统通过向量检索找到最匹配的API工具
- 自动生成API调用参数
- 执行API调用并返回结果

### 2. 聊天对话系统
- 支持多轮对话
- 会话状态管理
- 历史记录存储和查询
- 工具调用结果异步获取

### 3. API工具管理
- 工具注册和管理
- 分类组织
- 向量嵌入自动生成
- 多种文本表述支持

### 4. Web界面
- 工具管理界面
- 聊天交互界面
- 历史记录查看
- 多语言支持

## API接口设计

### 主要端点
- `POST /api/chat/completions`: 聊天完成API
- `GET /api/chat-histories/result/`: 获取工具调用结果
- `/api/tools/`: 工具管理相关接口
- `/api/categories/`: 分类管理接口
- `/health`: 健康检查接口

### 请求/响应格式
- 遵循OpenAI ChatCompletion API格式
- 支持工具调用(tool_calls)
- JSON格式数据交换

## 环境配置

### 必需环境变量
- `DATABASE_URL`: PostgreSQL连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_API_BASE_URL`: OpenAI API基础URL（可选）
- `EMBEDDING_MODEL`: 嵌入模型名称
- `TEXT_GENERATION_MODEL`: 文本生成模型名称

### 可选配置
- `PORT`: 应用运行端口（默认8000）
- `LOG_LEVEL`: 日志级别（默认ERROR）

## 部署和运行

### 开发环境
```bash
# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate

# 开发模式运行
fastapi dev main.py

# 生产模式运行
fastapi run main.py
```

### 数据库初始化
- 执行 `sql/meta.sql` 创建基础表结构
- 执行 `sql/chat-history.sql` 创建聊天历史表

### 国际化资源文件处理
项目支持多语言国际化功能，翻译文件存储在 `app/translations/` 目录下。在运行项目前，需要编译翻译资源文件：

```bash
# 编译翻译文件
./compile_translations.sh
```



**说明:**
- 翻译源文件格式为 `.po` 文件
- 编译后生成 `.mo` 二进制文件供应用使用
- 支持的语言包括中文、英文等
- 修改翻译内容后需要重新编译才能生效
- 你可能需要安装 gettext 

---

*分析时间: 2025-06-17*  
*分析工具: Amazon Q*
