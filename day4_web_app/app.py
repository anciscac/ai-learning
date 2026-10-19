import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# 1. 加载密钥
load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")

# 2. 网页设置
st.set_page_config(page_title="AI 客户挽回系统", page_icon="🤖")
st.title("🤖 AI 客户挽回生成系统")
st.write("上传包含用户反馈的 CSV 表格，系统将自动找出不满意客户，并利用 AI 生成专属回访话术。")

# 3. 文件上传
uploaded_file = st.file_uploader("请上传客户数据 (CSV)", type=["csv"])

if uploaded_file is not None:
    # 读取数据
    df = pd.read_csv(uploaded_file)
    st.success("✅ 数据读取成功！")
    
    # 用 Pandas 筛选
    try:
        # 这里假设你的表格有 '满意度' 和 '用户名' 这两列
        unhappy_users = df[df['满意度'] == '不满意']
        unhappy_names = unhappy_users['用户名'].tolist()
    except KeyError:
        st.error("❌ 表格缺少 '满意度' 或 '用户名' 列，请检查格式。")
        st.stop()
        
    st.info(f"发现不满意客户名单：**{unhappy_names}**")
    
    # 4. 交互按钮：点击才触发 AI
    if len(unhappy_names) > 0:
        if st.button("🚀 一键生成 AI 挽回话术"):
            with st.spinner("AI 正在深度思考，请稍候..."):
                # 构造 Prompt
                prompt_text = f"我们的产品有以下几个不满意的用户：{unhappy_names}。请帮我写一段简短的用户回访话术，安抚他们的情绪并了解具体问题。"
                
                # 呼叫智谱 API
                url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": prompt_text}]
                }
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    result = response.json()
                    
                    if "choices" in result:
                        ai_reply = result["choices"][0]["message"]["content"]
                        st.subheader("💡 专属挽回话术：")
                        st.write(ai_reply)
                    else:
                        st.error(f"API 报错：{result}")
                except Exception as e:
                    st.error(f"请求失败：{e}")
    else:
        st.warning("当前表格中没有“不满意”的客户，无需挽回。")