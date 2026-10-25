from langchain_community.document_loaders import PyPDFLoader

# 1. 加载 PDF（确保 test.pdf 就在你当前文件夹里）
print("正在尝试读取 PDF...")
loader = PyPDFLoader("test.pdf")
pages = loader.load()

# 2. 打印一共有几页
print(f"✅ 成功读取！共发现 {len(pages)} 页。")

# 3. 打印第一页的字数
if len(pages) > 0:
    first_page_text = pages[0].page_content
    print(f"第一页的字数是：{len(first_page_text)} 个字符。\n")
    
    print("========== 以下是第一页的前 300 个字 ==========")
    # 截取前300个字看看
    print(first_page_text[:300])
    print("===============================================")
else:
    print("❌ 警告：这个 PDF 一页都没读出来！")