import streamlit as st
from config_loader import load_append_config, load_inner_web_scale
from task_runner import run_task
from auth import register, login, is_logged_in, logout
from deepseek_api import evaluate_conversation, generate_conversation_title
import asyncio
import re
import requests
import streamlit.components.v1 as components
from database import User, Task, Conversation
from datetime import datetime
from chat_page import main_page

# 设置页面配置
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="css/X.png",
    layout="wide",
    initial_sidebar_state="collapsed"
) 

# 添加自定义 CSS 样式
def local_css(file_name):
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("css/main_styles.css")

# 添加自定义 CSS 来设置任务按钮宽度为最大
st.markdown("""
<style>
.task-button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'task_running' not in st.session_state:
    st.session_state.task_running = False
if 'agent_result' not in st.session_state:
    st.session_state.agent_result = None
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'show_confirm' not in st.session_state:
    st.session_state.show_confirm = False
    st.session_state.task_to_delete = None
    st.session_state.task_name_to_delete = None
if 'first_question' not in st.session_state:
    st.session_state.first_question = True
    st.session_state.chat_type = None
    st.session_state.handing = False

# 检查用户是否已登录
if is_logged_in():
    main_page() 

else:
    auth_type = None # 用于存储用户选择的验证方式
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image("css/Xbot.png", caption="", use_container_width=False, width=500) 
    with col3: 
        auth_type = st.radio(
            "验证方式：", 
            ["🔐 登录", "📝 注册"], 
            horizontal=False,
            label_visibility="collapsed",  # 可选：隐藏标签以自定义样式
            # 使用container参数包裹以进一步控制样式（需Streamlit支持）
        )

    if auth_type == "📝 注册":
        register()  # 直接调用自带表单的函数
    else:
        login()     # 直接调用自带表单的函数
    st.markdown("</div>", unsafe_allow_html=True)
    