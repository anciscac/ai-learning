import os
import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

with open("company_rules.txt","r",encoding="utf-8") as f:
    text = f.read()

chunks = [para.strip() for para in text.split("\n") if para.strip()]
print(f"成功将文本切分为{len(chunks)}个片段")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="company_rules")

def get_embedding(text_content):
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model":"embedding-2",
        "input": text_content
    }
    response = requests.post(url,headers=headers,json=data)
    result = response.json()
    if "data" not in result:
        print("\n智谱服务器拒绝了请求，返回的真实原因是：")
        print(result)
        import sys
        sys.exit(1)
    return result["data"][0]["embedding"]

print("正在向数据库存入数据，请稍侯。。。")
for i,chunk in enumerate(chunks):
    vector = get_embedding(chunk)
    collection.add(
        documents = [chunk],
        embeddings = [vector],
        ids = [f"id_{i}"]
    )
print("数据库构建完成！所有公司规定已转换为向量存入本地")
