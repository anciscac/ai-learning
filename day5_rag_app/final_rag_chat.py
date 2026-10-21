import streamlit as st
import os
import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")
st.title("企业智能客服(rag）")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="company_rules")

def get_embedding(text_content):
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}","Content-Type":"application/json"
    }
    data = {
        "model":"embedding-2","input":text_content
    }
    response = requests.post(url,headers=headers,json=data)
    result = response.json()
    if"data" not in result:
        st.error(f"Embedding API报错： {result}")
        st.stop()
    return result["data"][0]["embedding"]

if "messages" not in st.session_state:
    st.session_state.messages = [] 

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
         st.write(msg["content"])
if prompt := st.chat_input("请输入关于公司规定的问题。。。"):
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner("正在查阅公司相关规章制度"):
        question_vector = get_embedding(prompt)
        result = collection.query(query_embeddings=[question_vector],n_results=2)
        context = "\n".join(result['documents'][0])
        final_prompt = f"请严格根据以下【参考文档】回答用户的问题。如果文档里没有，请说不知道。\n【参考文档】: \n{context}\n\n【用户问题】:{prompt}"
        api_messages = st.session_state.messages[:-1]
        api_messages.append({"role":"user","content":final_prompt})

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "glm-4-flash", "messages": api_messages}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "choices" not in  result:
        st.error(f"聊天API报错: {result}")
    else:
        ai_reply = result["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role":"assistant","content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)
