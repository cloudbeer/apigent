#!/usr/bin/env python3
"""
测试流式聊天API的示例脚本
"""

import requests
import json
import uuid

def test_stream_chat():
    """测试流式聊天API"""
    
    # API端点
    url = "http://localhost:8000/api/chat/completions/stream"
    
    # 生成会话ID
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Session-Id": session_id
    }
    
    # 请求体
    data = {
        "messages": [
            {
                "role": "user",
                "content": "你好，请帮我查询天气信息"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": True
    }
    
    print(f"发送流式请求到: {url}")
    print(f"会话ID: {session_id}")
    print("=" * 50)
    
    try:
        # 发送流式请求
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        if response.status_code == 200:
            print("开始接收流式响应:")
            print("-" * 30)
            
            # 逐行读取流式响应
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # 处理SSE格式的数据
                    if line.startswith("data: "):
                        data_content = line[6:]  # 去掉 "data: " 前缀
                        
                        if data_content == "[DONE]":
                            print("\n流式响应结束")
                            break
                        
                        try:
                            # 解析JSON数据
                            chunk_data = json.loads(data_content)
                            
                            # 检查是否有错误
                            if "error" in chunk_data:
                                print(f"错误: {chunk_data['error']}")
                                break
                            
                            # 提取并显示内容
                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                choice = chunk_data["choices"][0]
                                if "delta" in choice:
                                    delta = choice["delta"]
                                    if "content" in delta and delta["content"]:
                                        print(delta["content"], end="", flush=True)
                                    
                                    # 处理工具调用
                                    if "tool_calls" in delta:
                                        print(f"\n[工具调用]: {delta['tool_calls']}")
                                
                                # 检查完成原因
                                if "finish_reason" in choice and choice["finish_reason"]:
                                    print(f"\n[完成原因]: {choice['finish_reason']}")
                        
                        except json.JSONDecodeError as e:
                            print(f"JSON解析错误: {e}")
                            print(f"原始数据: {data_content}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except KeyboardInterrupt:
        print("\n用户中断请求")


def test_normal_chat():
    """测试普通聊天API作为对比"""
    
    # API端点
    url = "http://localhost:8000/api/chat/completions"
    
    # 生成会话ID
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Session-Id": session_id
    }
    
    # 请求体
    data = {
        "messages": [
            {
                "role": "user",
                "content": "你好，请帮我查询天气信息"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    print(f"发送普通请求到: {url}")
    print(f"会话ID: {session_id}")
    print("=" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("普通响应结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")


if __name__ == "__main__":
    print("APIGent 流式聊天API测试")
    print("=" * 50)
    
    choice = input("选择测试类型 (1: 流式, 2: 普通, 3: 两者): ")
    
    if choice == "1":
        test_stream_chat()
    elif choice == "2":
        test_normal_chat()
    elif choice == "3":
        print("测试普通API:")
        test_normal_chat()
        print("\n" + "=" * 50)
        print("测试流式API:")
        test_stream_chat()
    else:
        print("无效选择，默认测试流式API")
        test_stream_chat()
