import chromadb

# 连接数据库
client = chromadb.PersistentClient(path="./chroma_db")

# 列出数据库里所有的集合名字
collections = client.list_collections()
print("当前数据库里的集合有：", collections)