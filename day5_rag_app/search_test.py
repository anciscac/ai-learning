import os
import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="company_rules")

def get_embedding(text_content):
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"model": "embedding-2", "input": text_content}
    response = requests.post(url, headers=headers, json=data)
    
    # ---- 新增的排错代码 ----
    result = response.json()
    if "data" not in result:
        print("\n❌ 智谱 API 报错了！返回的真实信息：")
        print(result)
        # 顺便检查一下密钥读到没有
        print(f"当前使用的 Key 前 10 位：{str(api_key)[:10]}")
        import sys
        sys.exit(1)
    # ------------------------
        
    return result["data"][0]["embedding"]

question = "如果我晚上加班到11点，打车回家可以报销吗？"
print(f"用户提问：{question}")

question_vector = get_embedding(question)

results = collection.query(
    query_embeddings = [question_vector],
    n_results=2
)

print("/n数据库中找到最相关片段：")
for i,doc in enumerate(results['documents'][0]):
    print(f"[{i+1}]{doc}")