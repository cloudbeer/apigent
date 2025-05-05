-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建工具组表
CREATE TABLE IF NOT EXISTS apigent_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建工具表
CREATE TABLE IF NOT EXISTS apigent_tool (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    url VARCHAR(1024) NOT NULL,
    http_method VARCHAR(20) NOT NULL,
    http_context JSONB DEFAULT '{}'::jsonb, -- 存储 HTTP 请求的额外数据，如认证信息、headers、默认参数等
    category_id INTEGER REFERENCES apigent_category(id),
    embedding vector(1536), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE apigent_tool_embedding (
    id BIGSERIAL PRIMARY KEY,                          -- 向量ID
    tool_id BIGINT REFERENCES apigent_tool(id) ON DELETE CASCADE, -- 关联的工具ID
    text_variant TEXT NOT NULL,                     -- 表述文本
    is_original BOOLEAN DEFAULT FALSE,              -- 是否为原始表述
    category_id INTEGER REFERENCES apigent_category(id),
    embedding vector(1536),                          -- 向量(维度根据您的模型调整)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- 为向量创建IVFFlat索引(适合中等规模数据)
CREATE INDEX ON apigent_tool_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 创建工具ID索引以加速连接查询
CREATE INDEX ON apigent_tool_embedding (tool_id);

-- 创建是否原始表述的索引，便于按类型查询
CREATE INDEX ON apigent_tool_embedding (is_original);

-- 创建字段表
CREATE TABLE IF NOT EXISTS apigent_field (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT REFERENCES apigent_tool(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data_type VARCHAR(50) NOT NULL,
    format VARCHAR(50), -- OpenAPI 格式，如 date-time, email, uuid 等
    is_required BOOLEAN DEFAULT false,
    is_array BOOLEAN DEFAULT false,
    array_items_type VARCHAR(50), -- 数组元素类型
    array_items_format VARCHAR(50), -- 数组元素格式
    default_value TEXT,
    enum_values JSONB, -- 枚举值列表
    minimum NUMERIC, -- 数值最小值
    maximum NUMERIC, -- 数值最大值
    exclusive_minimum BOOLEAN DEFAULT false, -- 是否包含最小值
    exclusive_maximum BOOLEAN DEFAULT false, -- 是否包含最大值
    min_length INTEGER, -- 字符串最小长度
    max_length INTEGER, -- 字符串最大长度
    pattern TEXT, -- 正则表达式模式
    min_items INTEGER, -- 数组最小元素数
    max_items INTEGER, -- 数组最大元素数
    unique_items BOOLEAN DEFAULT false, -- 数组元素是否唯一
    multiple_of NUMERIC, -- 数值倍数
    nullable BOOLEAN DEFAULT false, -- 是否可为 null
    deprecated BOOLEAN DEFAULT false, -- 是否已废弃
    allow_empty_value BOOLEAN DEFAULT false, -- 是否允许空值
    style VARCHAR(50), -- 参数样式：matrix, label, form, simple, spaceDelimited, pipeDelimited, deepObject
    explode BOOLEAN DEFAULT false, -- 是否展开数组/对象
    allow_reserved BOOLEAN DEFAULT false, -- 是否允许保留字符
    schema_ref TEXT, -- 引用其他 schema
    example TEXT, -- 示例值
    reference_tool_id BIGINT REFERENCES apigent_tool(id), -- 引用的工具ID
    reference_path TEXT, -- 引用工具返回值的 JSON 路径
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以优化查询性能
CREATE INDEX ON apigent_field (tool_id);
CREATE INDEX ON apigent_field (name);
CREATE INDEX ON apigent_field (data_type);
