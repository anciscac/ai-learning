import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
load_dotenv()
api_key = os.getenv("SILICON_API_KEY")

print("1.正在读取并切片pdf。。。")
loader = PyPDFLoader("test.pdf")
pages = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50,
    length_function = len,
    separators = ["\n\n","。","!","?",",","\n"]
)
chunks = text_splitter.split_documents(pages)
print(f"切片完成，共{len(chunks)}块")

embeddings = OpenAIEmbeddings(
    api_key = api_key,
    base_url = "https://api.siliconflow.cn/v1",
    model = "BAAI/bge-m3",
    check_embedding_ctx_length = False
)
# 4. 存入 Chroma 数据库
print("2. 正在将数据存入向量数据库...")

# 先创建对象
db = Chroma(
    embedding_function=embeddings,
    # 使用绝对路径，这样它绝对不会跑到别的文件夹去
    persist_directory=r"D:\dev\ai-learning\day10_pdf_rag\chroma_pdf_db"
)

# 再把文档加进去
db.add_documents(chunks)

print("🎉 数据库构建完成！")