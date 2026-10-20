import streamlit as st
import os
import chromadb
import requests
from dotenv import load_dotenv

# 1. 页面基础设置
st.set_page_config(page_title="企业智能知识库", page_icon="📚")
st.title("📚 企业智能知识库助手")
st.write("欢迎！请输入你关心的公司规章制度问题，AI 将基于本地文档为你解答。")

# 2. 加载密钥和数据库
load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

# 连接本地向量数据库
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="company_rules")

# 3. 复用之前的向量化函数（把文字变成向量）
def get_embedding(text_content):
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "embedding-2", "input": text_content}
    response = requests.post(url, headers=headers, json=data)
    return response.json()["data"][0]["embedding"]

# 4. 网页上的输入框和按钮
question = st.text_input("请输入你的问题：", placeholder="例如：年假有几天？出差住宿标准是多少？")

if st.button("🚀 提问 AI"):
    if not question:
        st.warning("请先输入问题！")
    else:
        with st.spinner("正在查阅公司文档并思考中..."):
            # 步骤A：把问题变成向量
            question_vector = get_embedding(question)
            
            # 步骤B：去数据库里找最相关的 2 个片段
            results = collection.query(query_embeddings=[question_vector], n_results=2)
            context = "\n".join(results['documents'][0]) # 把找到的规定拼成一段文字
            
            # 步骤C：构造发给大模型的 Prompt
            prompt = f"""
            你是一个专业的企业 HR 助手。
            请严格根据以下【参考文档】来回答用户的【问题】。
            如果参考文档里没有答案，请直接说“根据现有规定，我无法回答该问题”，绝不要自己编造。
            
            【参考文档】：
            {context}
            
            【问题】：
            {question}
            """
            
            # 步骤D：调用大模型（GLM-4-Flash）
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "glm-4-flash",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                result = response.json()
                
                if "choices" in result:
                    ai_answer = result["choices"][0]["message"]["content"]
                    # 在网页上展示答案
                    st.success("🤖 AI 回答：")
                    st.write(ai_answer)
                    
                    # 把“依据”折叠起来，证明不是瞎编的
                    with st.expander("查看依据的文档片段"):
                        st.info(context)
                else:
                    st.error(f"AI 接口报错：{result}")
            except Exception as e:
                st.error(f"请求失败：{e}")