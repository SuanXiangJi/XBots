import streamlit.components.v1 as components
import streamlit as st

def save_to_local_storage(key, value):
    """
    将数据保存到浏览器的 localStorage 中。

    参数:
        key (str): 要保存的键。
        value (str): 要保存的值。
    """
    # 确保 key 和 value 是字符串类型
    if key is None:
        key = ""
    if value is None:
        value = ""

    # 转义单引号以避免 JavaScript 错误
    key = key.replace("'", "\\'")
    value = value.replace("'", "\\'")

    # 定义 JavaScript 代码
    my_js = f"""
    <script>
    // 保存数据到 localStorage
    function saveToLocalStorage(key, value) {{
        localStorage.setItem(key, value); 
    }}

    // 调用保存数据的函数
    saveToLocalStorage('{key}', '{value}');
    </script>
    """

    # 将 JavaScript 代码包装为 HTML 并渲染
    components.html(my_js, height=0)

def read_from_local_storage(key):
    """
    从浏览器的 localStorage 中读取数据，并将结果存储到 st.session_state 中。

    参数:
        key (str): 要读取的键。
    """
    # 确保 key 是字符串类型
    if key is None:
        key = ""

    # 转义单引号以避免 JavaScript 错误
    key = key.replace("'", "\\'")

    # 定义 JavaScript 代码
    my_js = f"""
    <script>
    // 从 localStorage 中读取数据
    function readFromLocalStorage(key) {{
        const value = localStorage.getItem(key);
        if (value) {{
            // 将数据存储到 Streamlit 的 session_state 中
            document.getElementById('value').value = value;
        }} else {{
            document.getElementById('value').value = 'null';
        }}
    }}

    // 调用读取数据的函数
    readFromLocalStorage('{key}');
    </script>
    <input type="hidden" id="value" name="value" value="">
    """

    # 将 JavaScript 代码包装为 HTML 并渲染
    components.html(my_js, height=0)
    print("read_from_local_storage")
    print(st.session_state)

    # 检查是否有从 JavaScript 发送的消息
    if "value" in st.session_state:
        return st.session_state["value"]
    return None 