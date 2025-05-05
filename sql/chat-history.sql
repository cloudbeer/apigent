-- 创建聊天会话表
CREATE TABLE IF NOT EXISTS apigent_chat_session (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,     -- 会话ID
    title VARCHAR(255) NOT NULL,                 -- 会话标题
    case_summary TEXT,                           -- 会话总结
    status INTEGER NOT NULL DEFAULT 0,           -- 会话状态
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建聊天历史记录表
CREATE TABLE IF NOT EXISTS apigent_chat_history (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES apigent_chat_session(session_id) ON DELETE CASCADE,  -- 会话ID，外键关联
    request_content JSONB NOT NULL,              -- 用户请求内容
    response_content JSONB,                      -- AI响应内容
    tool_name VARCHAR(255),                      -- 使用的工具名称
    parameters JSONB,                            -- 工具参数，使用JSONB类型存储
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以优化查询性能

CREATE INDEX ON apigent_chat_history (session_id);
CREATE INDEX ON apigent_chat_history (tool_name);
