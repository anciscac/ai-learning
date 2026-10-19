import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key:
    print(f"成功读取密钥,前五位是:{api_key[:5]}********")
else:
    print("未找到密钥，请检查.env文件名字是否正确，或者内容是否有问题。")