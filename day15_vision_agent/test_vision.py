import os
import base64
import requests
from dotenv import load_dotenv

# 1. 加载密钥
load_dotenv()
api_key = os.getenv("SILICON_API_KEY")

# 2. 定义将图片转为 Base64 的函数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        # 读取图片的二进制数据，并转换成 base64 字符串
        return base64.b64encode(image_file.read()).decode('utf-8')

# 3. 准备请求数据
image_path = "test.jpg"
print(f"正在读取并编码图片：{image_path}...")
base64_image = encode_image(image_path)

# 这就是硅基流动视觉模型的接口地址
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 这里使用了 OpenAI 兼容的视觉消息格式
data = {
    "model": "Qwen/Qwen3-VL-8B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请详细描述一下这张图片里有什么。"},
                {
                    "type": "image_url",
                    "image_url": {
                        # 核心：告诉模型这是一个 base64 格式的 jpeg 图片
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 500
}

# 4. 发送请求
print("正在呼叫视觉大模型，请稍候...")
response = requests.post(url, headers=headers, json=data)
result = response.json()

# 5. 打印结果
if "choices" in result:
    print("\n🤖 AI 看到了：")
    print(result["choices"][0]["message"]["content"])
else:
    print("\n❌ 报错了，服务器返回：")
    print(result)