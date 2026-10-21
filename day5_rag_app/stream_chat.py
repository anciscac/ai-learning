import streamlit as st
import os
import chromadb
import requests
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")
st.title("📚 企业智能客服 (流式极速版)")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="company_rules")

def get_embedding(text_content):
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "embedding-2", "input": text_content}
    response = requests.post(url, headers=headers, json=data)
    return response.json()["data"][0]["embedding"]

# 初始化记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("请输入关于公司规定的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.spinner("正在查阅公司相关规章制度..."):
        question_vector = get_embedding(prompt)
        result = collection.query(query_embeddings=[question_vector], n_results=2)
        context = "\n".join(result['documents'][0])
        
        final_prompt = f"请严格根据以下【参考文档】回答用户的问题。如果文档里没有，请说不知道。\n【参考文档】: \n{context}\n\n【用户问题】:{prompt}"
        api_messages = st.session_state.messages[:-1]
        api_messages.append({"role": "user", "content": final_prompt})

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 注意这里：加了 "stream": True
    data = {
        "model": "glm-4-flash", 
        "messages": api_messages,
        "stream": True 
    }
    
    response = requests.post(url, headers=headers, json=data, stream=True)

    # 定义一个生成器函数，用来把服务器每次吐出来的字符提取出来
    def generate_chunks():
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    if json_str != "[DONE]":
                        try:
                            chunk = json.loads(json_str)
                            # 提取增量文本
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            yield delta
                        except Exception:
                            pass

    # 在网页上画出一个 AI 消息框，把生成器丢进去
    with st.chat_message("assistant"):
        # st.write_stream 会自动处理打字机效果，并返回完整的最终文本
        full_response = st.write_stream(generate_chunks())
        
    # 把完整回复存进记忆
    st.session_state.messages.append({"role": "assistant", "content": full_response})