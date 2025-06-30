import os
from openai import OpenAI
import logging
from dotenv import load_dotenv
import json
from openai.types.chat import ChatCompletionMessage, ChatCompletion
import time
from typing import AsyncGenerator

# 加载环境变量
load_dotenv(override=True)

logger = logging.getLogger(__name__)

base_url = os.getenv("OPENAI_API_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")
text_generation_model = os.getenv("TEXT_GENERATION_MODEL")


client = OpenAI(base_url=base_url, api_key=api_key)


# 向量化工具函数
def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=embedding_model, input=text  # 不需要编码，OpenAI 客户端会处理
    )
    res = response.data[0].embedding
    logger.info(f"embedding length: {len(res)}")
    
    # 处理维度不匹配问题，确保返回1536维向量
    target_dim = 1536
    current_dim = len(res)
    
    if current_dim == target_dim:
        return res
    elif current_dim < target_dim:
        # 如果维度不足，通过重复或填充0来扩展
        padding = [0.0] * (target_dim - current_dim)
        return res + padding
    else:
        # 如果维度过多，截断到目标维度
        return res[:target_dim]


def gen_text_variant(text: str, system_prompt: str | None = None) -> list[str]:
    if system_prompt is None:
        system_prompt = """作为IT工具变体生成器，你需要为指定的IT工具或服务生成不同形式的用户查询表达，以帮助训练AI向量检索系统，实现精确的意图识别。
你收到的输入内容为某个特定的IT工具或服务，例如："WAF封禁"、"开通数据库"、"发送邮件"、"查询网页"等。
对于输入内容，请严格按照以下要求生成变体表达：
- 每个变体独立一行，禁止单独输出序号或编号。
- 严格保持与输入内容完全一致的语言进行输出，例如输入为中文则输出也为中文，输入为英文则输出也为英文。
- 总变体数不超过35条，至少30%的变体应不超过10个词。
- 每次生成的变体，必须覆盖以下所有表达类型：
    - 极简表达（3-5个词）
    - 日常口语化表述
    - 使用精确技术术语的专业表达
    - 新手困惑式但意图清晰的表达
    - 包含具体示例（如特定IP、数据库名、邮箱地址）的表达
    - 包含URL或资源标识符的详细描述
    - 紧急情况下简短急促的表达
    - 针对特定平台或界面的操作询问（如"在控制台如何..."）
    - 包含具体技术参数或配置信息的表达
    - 使用同义技术术语或行业别名的表达
    - 包含常见误解但意图明确的表达
    - 明确询问具体操作步骤或流程的表达
    - 针对特定业务场景或用例的具体表达
    - 包含时间或条件限制的请求表达
    - 使用同义动词明确表达核心意图（例如封禁意图使用"阻止"、"屏蔽"、"拦截"、"过滤"等）

请务必遵循上述规范，并避免模糊、含糊的表达，以确保AI训练数据的质量和可用性。
        
"""

    response = client.chat.completions.create(
        model=text_generation_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        stream=False,
    )

    content = response.choices[0].message.content
    # 如果content为空，则返回text
    temp_list = content.split("\n")
    if temp_list == [""]:
        result = [text]
    else:
        result = [text] + temp_list
    # 去除空字符串
    result = [item for item in result if item.strip() != ""]
    return result


def parse_tool_schemas(
    messages: list[ChatCompletionMessage], tools: list[dict]
) -> dict:
    """
    使用 OpenAI 模型解析工具调用

    Args:
        messages: 对话历史
        tools: 工具列表

    Returns:
        dict: 包含 OpenAI 响应和额外字段的字典
    """
    print(f"retrieved tools: {tools}")
    response: ChatCompletion | None = None

    if len(tools) <= 0:
        response = client.chat.completions.create(
            model=text_generation_model,
            messages=messages,
        )
    else:
        # print(f"messages: {messages}")
        response = client.chat.completions.create(
            model=text_generation_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        # 构建包含额外字段的响应
    enhanced_response = {
        "openai_response": response.to_dict(),
        "timestamp": int(time.time()),
        "model": text_generation_model,
        "tools_used": [{"name": tool["function"]["name"], "key": tool["function"]["key"]} for tool in tools],
    }

    return enhanced_response


async def parse_tool_schemas_stream(
    messages: list[ChatCompletionMessage], tools: list[dict]
) -> AsyncGenerator[dict, None]:
    """
    使用 OpenAI 模型解析工具调用 - 流式版本

    Args:
        messages: 对话历史
        tools: 工具列表

    Yields:
        dict: OpenAI 流式响应的每个chunk
    """
    print(f"retrieved tools: {tools}")

    try:
        if len(tools) <= 0:
            stream = client.chat.completions.create(
                model=text_generation_model,
                messages=messages,
                stream=True,
            )
        else:
            print(f"messages: {messages}")
            stream = client.chat.completions.create(
                model=text_generation_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
            )

        # 逐个yield流式响应的chunk
        for chunk in stream:
            # 将chunk转换为字典格式
            chunk_dict = chunk.to_dict()
            yield chunk_dict
            
    except Exception as e:
        logger.error(f"Error in streaming parse_tool_schemas: {str(e)}")
        # 发送错误信息
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "api_error",
                "code": "stream_error"
            }
        }
        yield error_chunk
