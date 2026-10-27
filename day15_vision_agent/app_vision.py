import streamlit as st
import os
import base64
import requests
from dotenv import load_dotenv

# 1. 页面基础配置
load_dotenv()
st.set_page_config(page_title="AI 图像分析师", page_icon="👁️")
st.title("👁️ AI 图像分析师")
st.write("上传任意图片，向 AI 提问！")

api_key = os.getenv("SILICON_API_KEY")

# 2. 使用 Streamlit 的图片上传组件
uploaded_file = st.file_uploader("请上传一张图片 (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 在网页上把用户上传的图片展示出来
    st.image(uploaded_file, caption="已上传的图片", use_container_width=True)
    
    # 让用户输入针对图片的问题
    question = st.text_input("你想对这张图片问什么？", value="请详细描述一下这张图片里的内容。")
    
    if st.button("🚀 开始分析"):
        with st.spinner("AI 正在仔细端详这张图片..."):
            # 3. 读取上传的图片文件，并转为 Base64
            # 注意：这里直接用 uploaded_file.getvalue() 拿到图片的二进制数据
            image_bytes = uploaded_file.getvalue()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 4. 构造发给大模型的数据
            url = "https://api.siliconflow.cn/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "Qwen/Qwen3-VL-8B-Instruct", # 使用你刚才跑通的模型
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # 5. 发送请求并展示结果
            try:
                response = requests.post(url, headers=headers, json=data)
                result = response.json()
                
                if "choices" in result:
                    st.success("🤖 AI 的回答：")
                    st.write(result["choices"][0]["message"]["content"])
                else:
                    st.error(f"API 报错：{result}")
            except Exception as e:
                st.error(f"请求失败：{e}")