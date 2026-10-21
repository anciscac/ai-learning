import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

st.title("💬 带记忆的 AI 助手")

# 1. 初始化记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 渲染历史聊天
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 3. 接收输入
if prompt := st.chat_input("请输入你的问题..."):
    
    # 保存并显示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # 请求 AI
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "glm-4-flash", "messages": st.session_state.messages}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    # 排错检查
    if "choices" not in result:
        st.error(f"API 报错：{result}")
    else:
        ai_reply = result["choices"][0]["message"]["content"]
        
        # 保存并显示 AI 回复
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)

