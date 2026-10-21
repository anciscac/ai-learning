import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")
st.title("🤖 全能 AI 助理 (带计算器工具)")

# 1. 定义工具说明书（和终端版一样）
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个数字的加法",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"}
                },
                "required": ["a", "b"]
            }
        }
    }
]

# 2. 定义真实工具函数
def add_numbers(a, b):
    return a + b

# 3. 初始化记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 渲染历史聊天
for msg in st.session_state.messages:
    # 只渲染正常的对话，跳过 tool 的内部交互信息
    if msg["role"] in ["user", "assistant"] and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 5. 接收输入
if prompt := st.chat_input("试着让我算个数，比如：帮我算 123 加 456 等于几？"):
    # 保存并渲染用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    # 准备请求数据
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 第一次请求：带上工具
    data = {
        "model": "glm-4-flash", 
        "messages": st.session_state.messages, 
        "tools": tools
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    # 获取 AI 的回复（可能是文字，也可能是调用工具的申请）
    response_message = result["choices"][0]["message"]
    
    # 6. 判断是否需要调用工具
    if response_message.get("tool_calls"):
        with st.chat_message("assistant"):
            st.info("🔧 AI 正在调用计算器工具...")
            
        # 提取参数并本地执行
        tool_call = response_message["tool_calls"][0]
        args = json.loads(tool_call["function"]["arguments"])
        calc_result = add_numbers(args["a"], args["b"])
        
        # 将 AI 的调用申请和工具执行结果加入记忆
        st.session_state.messages.append(response_message)
        st.session_state.messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": str(calc_result)
        })
        
        # 第二次请求：把结果告诉 AI，让它总结
        data_final = {"model": "glm-4-flash", "messages": st.session_state.messages}
        final_response = requests.post(url, headers=headers, json=data_final)
        final_answer = final_response.json()["choices"][0]["message"]["content"]
        
        # 保存并渲染最终回复
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        with st.chat_message("assistant"):
            st.write(final_answer)
            
    else:
        # 如果没调用工具，直接显示回复
        ai_reply = response_message["content"]
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)