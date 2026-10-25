from langchain_community.document_loaders import PyPDFLoader
pdf_path = "test.pdf"
print("正在加载并解析pdf，请稍后。。。")
loader = PyPDFLoader(pdf_path)
pages = loader.load()
print(f"解析成功！这份PDF共有{len(pages)}页。\n")
print("---第一页的文本片段---")
print(pages[9].page_content[:500])