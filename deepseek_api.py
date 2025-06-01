# Please install OpenAI SDK first: `pip3 install openai`
from openai import OpenAI
from dotenv import load_dotenv
import os
from config_loader import get_config_value,load_append_config
import streamlit as st 

# 加载 .env 文件
load_dotenv()

def call_deepseek_api(messages,limit_temperature=0.1,limit_max_tokens=1000):
    print("正在调用 DeepSeek API...")
    # 从环境变量中获取 API Key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未在 .env 文件中设置")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                *messages
            ],
            stream=False,
            temperature=limit_temperature,  # 调整随机参数，范围 0-2，值越大越随机————默认不随机0.1
            max_tokens=limit_max_tokens    # 调整最大生成的 token 数量
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek API 调用出错: {e}")
        return None
    
def get_api_response(messages): 
    """"直接使用api的回复"""
    response = call_deepseek_api(messages,limit_temperature=0.9,limit_max_tokens=1000)
    return response

def get_perfect_command(messages): 
    """生成一条合适的browser-use命令"""
    
    th1, th2 = st.columns([1, 14])
    with th1:
        think1 = st.empty()
        think1.image("css/thinking.png", use_container_width=False,width = 40)
    with th2:
        think2 = st.empty()
        think2.markdown("<h4><b>✅ 优化提问中...</b></h4>", unsafe_allow_html=True)

    # 读取配置并拼接
    append_rules = load_append_config() 
    print(0)
    last_user_message = next((msg for msg in reversed(messages) if msg["role"] == "user"), None)
    if not last_user_message:
        return None
    print(messages)
    # print(append_rules)
    fixed_cmd = {
        "role": "system", 
        "content": f"优化我的提问：“{last_user_message['content']}”,强调问题中的关键字复述"
    }
    updated_messages = messages + [fixed_cmd]
    response = call_deepseek_api(updated_messages,limit_temperature=0.4,limit_max_tokens=100) 
    
    think1.empty()  # 清除“思考中...”提示
    think2.empty()  # 清除“思考中...”提示

    # 从响应中提取浏览器命令并拼接append_rules
    
    th1, th2 = st.columns([1, 14])
    with th1:
        think1 = st.empty()
        think1.image("css/thinking.png", use_container_width=False,width = 40)
    with th2:
        think2 = st.empty()
        think2.write(f"<h4><b>✅ 优化完成，浏览器命令已生成：{response}</b></h4>", unsafe_allow_html=True)
    browser_command = response
    final_command = f"{browser_command}\n注意："
    i=0
    for rule in append_rules:
        final_command += f"{i+1}.{rule}\n"
        i+=1
    return final_command 

def evaluate_conversation(chat_type,messages): 
    """评估对话处理方式"""
    res_mode = get_config_value("agent_mode")
    if chat_type == "message" or res_mode == 0:
        print("直接调用API")
        res_msg = get_api_response(messages)
        return (0, res_msg)
    elif chat_type == "web" or res_mode == 1:
        print("生成browser-use命令")
        res_cmd = get_perfect_command(messages)
        return (1, res_cmd)
    else:
        print("API决策中")
        
        thi1, thi2 = st.columns([1, 14])
        with thi1:
            thinking1 = st.empty()
            thinking1.image("css/thinking.png", use_container_width=False,width = 50)
        with thi2:
            thinking2 = st.empty()
            thinking2.markdown("<h4><b>🧠 API决策中 . . .</b></h4>", unsafe_allow_html=True)
        # 提取上一条用户提问内容
        last_user_message = next((msg for msg in reversed(messages) if msg["role"] == "user"), None)
        if not last_user_message:
            return (0, None)
        
        evaluation_prompt = {
            "role": "user", 
            "content": f"“{last_user_message['content']}”，是不是在网站上的操作？是就回复“1”，否则回复“0”（回复单个数字即可）"
        }
        
        # 添加评估指令到消息末尾
        # updated_messages = messages + [evaluation_prompt]
        updated_messages = [evaluation_prompt]
        print("原对话:",updated_messages)
        
        # 调用API
        response = call_deepseek_api(updated_messages,limit_temperature=0.1,limit_max_tokens=10)
        thinking1.empty()  # 清除“思考中...”提示
        thinking2.empty()  # 清除“思考中...”提示
        print("API响应:",response)
        
        # 解析响应
        if not response:
            return (0, None)
            
        first_line = response.split('\n')[0].strip()
        if first_line == '0':  
            th1, th2 = st.columns([1, 14])
            with th1:
                think1 = st.empty()
                think1.image("css/thinking.png", use_container_width=False,width = 40)
            with th2:
                think2 = st.empty()
                think2.markdown("<h4><b>✅ 已确定使用文字应答。</b></h4>", unsafe_allow_html=True)
            res_msg = get_api_response(messages)
            
            think1.empty()  # 清除“思考中...”提示
            think2.empty()  # 清除“思考中...”提示
            return (0, res_msg)
        elif first_line == '1':
            th1, th2 = st.columns([1, 14])
            with th1:
                think1 = st.empty()
                think1.image("css/thinking.png", use_container_width=False,width = 40)
            with th2:
                think2 = st.empty()
                think2.markdown("<h4><b>✅ 准备启动“网页帮做”模式。</b></h4>", unsafe_allow_html=True)
            res_cmd = get_perfect_command(messages)
            
            think1.empty()  # 清除“思考中...”提示
            think2.empty()  # 清除“思考中...”提示
            return (1, res_cmd)
        else:# 如果API返回了其他内容，重新调用API
            i=0
            judge_num = get_config_value("re_judge")
            while i<judge_num:
                i+=1
                re_evaluation_prompt = {
                        "role": "system", 
                        "content": f"（直接回答数字）针对上一条用户提问以及上下文：“{last_user_message['content']}”，评估其是否可以直接作为一个简单的browser-use命令？可以的话或者当用户明确要求访问网站就回复“1”，否则回复“0”（直接回答数字！！！！）（直接回答数字！！！！）"
                    } 
                re_updated_messages = messages + [re_evaluation_prompt] 
                temp = i/4
                response = call_deepseek_api(re_updated_messages,limit_temperature=temp,limit_max_tokens=10) 
                re_first_line = response.split('\n')[0].strip() 
                if re_first_line == '0':
                    res_msg = get_api_response(messages)
                    return (0, res_msg)
                elif re_first_line == '1':
                    res_cmd = get_perfect_command(messages)
                    return (1, res_cmd)
            return (0, "服务器繁忙，请稍后再试")
            

def generate_conversation_title(messages: list) -> str:
    """生成简短对话标题（不超过14字符）"""
    title_prompt = {
        "role": "system",
        "content": "请根据对话内容生成中文标题，必须极度简短，标点符号省略，最长不得超过14个字符，只返回标题内容不要任何格式"
    }
    
    try:
        response = call_deepseek_api(messages + [title_prompt])
        # 提取首行有效内容并截断
        clean_title = response.split('\n')[0].strip()[:14]
        return clean_title if clean_title else "未命名对话"
    except Exception as e:
        print(f"标题生成异常: {str(e)}")
        return "未命名对话"

# main测试函数
def main():
    messages = [
        {"role": "user", "content": "你好，DeepSeek!"},
        {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"},
        {"role": "user", "content": "你能告诉我今天的天气吗？"}
    ]
    
    status, msg = evaluate_conversation(messages)
    print(f"评估结果: {status}")
    if status == 0:
        print(f"完整响应: {msg}")



if __name__ == "__main__":
    main()
