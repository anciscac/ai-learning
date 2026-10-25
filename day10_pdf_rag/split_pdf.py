from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
print("正在加载pdf。。。")
loader = PyPDFLoader("test.pdf")
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    length_function=len,
    separators=["\n\n","\n","。","!","?",","]
)
print("正在智能切片。。。")
chunks = text_splitter.split_documents(pages)

print(f"切片完成！原本{len(pages)}页的PDF，被切成了{len(chunks)}个小块儿。\n")

for i in range(min(3,len(chunks))):
    print(f"----第{i+1}个切片----")
    print(f"该切片的长度：{len(chunks[i].page_content)}")
    print("\n")