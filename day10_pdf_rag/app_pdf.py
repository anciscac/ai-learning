import streamlit as st
import os
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. 页面配置与加载密钥
st.set_page_config(page_title="PDF 智能阅读器", page_icon="📄")
st.title("📄 智能 PDF 知识库问答")

load_dotenv()
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
silicon_key = os.getenv("SILICON_API_KEY")

if not deepseek_key or not silicon_key:
    st.error("请检查 .env 文件是否包含 DEEPSEEK_API_KEY 和 SILICON_API_KEY")
    st.stop()

# 2. 初始化大模型和向量化模型
llm = ChatOpenAI(
    api_key=deepseek_key,
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0,
    streaming=True # 开启流式输出
)

embeddings = OpenAIEmbeddings(
    api_key=silicon_key,
    base_url="https://api.siliconflow.cn/v1",
    model="BAAI/bge-m3",
    check_embedding_ctx_length=False
)

# 3. 连接我们刚才建好的 PDF 数据库
# 注意：如果找不到库，这里会报错，所以确保 build_pdf_db.py 已经跑过
@st.cache_resource
def load_db():
    return Chroma(persist_directory="./chroma_pdf_db", embedding_function=embeddings)

db = load_db()
retriever = db.as_retriever(search_kwargs={"k": 3}) # 每次检索最相关的 3 个片段

# 4. 构建 RAG 提示词模板
template = """你是一个专业的 PDF 文档分析助手。
请严格根据以下【参考文档】回答用户的问题。如果你在文档中找不到答案，请直接说“文档中未提及”，绝不要自己编造。
【参考文档】：
{context}

【用户问题】：
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 5. 把检索器、提示词、模型串成 LangChain 链
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. 聊天界面初始化
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. 接收用户提问并触发 RAG
if prompt_text := st.chat_input("请输入关于这篇 PDF 的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.write(prompt_text)

    # ================= 新增监控代码 =================
    print("\n" + "="*40)
    print(f"用户提问：{prompt_text}")
    # 手动调用检索器，看看到底查出了什么
    docs = retriever.invoke(prompt_text)
    print(f"查到了 {len(docs)} 个片段。")
    for i, doc in enumerate(docs):
        print(f"【片段 {i+1}】: {doc.page_content[:100]}...") # 只打印前100个字
    print("="*40 + "\n")
    # ================================================

    # 渲染 AI 回复
    with st.chat_message("assistant"):
        with st.spinner("正在查阅 PDF 并思考中..."):
            response_stream = rag_chain.stream(prompt_text)
            full_response = st.write_stream(response_stream)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})