import streamlit as st
import random
import pandas as pd
import math
import wave
import struct
import io
import base64

# 設定頁面排版
st.set_page_config(page_title="九九乘法練習", layout="centered")

# --- 自訂 CSS：把按鈕字體變大 ---
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        height: 80px;
        border-radius: 15px;
    }
    div[data-testid="stButton"] button p {
        font-size: 35px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 終極音效解決方案 (產生 Base64 音效) ---
@st.cache_data
def get_correct_audio():
    sample_rate, duration = 44100, 0.2
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            val = int(32767 * 0.4 * math.sin(2.0 * math.pi * 880 * i / sample_rate))
            f.writeframesraw(struct.pack('<h', val))
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<audio autoplay src="data:audio/wav;base64,{b64}"></audio>'

@st.cache_data
def get_wrong_audio():
    sample_rate, duration = 44100, 0.3
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        period = sample_rate / 150.0
        for i in range(int(sample_rate * duration)):
            val = int(32767 * 0.2 * (1 if (i % period) < (period/2) else -1))
            f.writeframesraw(struct.pack('<h', val))
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<audio autoplay src="data:audio/wav;base64,{b64}"></audio>'

# --- 初始化狀態變數 ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "num1" not in st.session_state:
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "audio" not in st.session_state:
    st.session_state.audio = None
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

# --- 處理按鈕動作的函式 ---
def press_digit(digit):
    if len(st.session_state.current_input) < 3:
        st.session_state.current_input += str(digit)

def press_delete():
    st.session_state.current_input = st.session_state.current_input[:-1]

def submit_answer():
    if not st.session_state.current_input:
        st.session_state.feedback = "⚠️ 請輸入答案！"
        st.session_state.audio = None
        return

    n1 = st.session_state.num1
    n2 = st.session_state.num2
    user_ans = int(st.session_state.current_input)
    correct_ans = n1 * n2
    is_correct = (user_ans == correct_ans)

    # 記錄作答
    st.session_state.logs.append({
        "題目": f"{n1} × {n2}",
        "小孩填寫": user_ans,
        "正確答案": correct_ans,
        "結果": "⭕ 正確" if is_correct else "❌ 錯誤"
    })

    # 設定精簡版回饋
    if is_correct:
        st.session_state.feedback = "⭕ 答對了！"
        st.session_state.audio = "correct"
    else:
        st.session_state.feedback = f"❌ 錯了！<br><span style='font-size:18px'>上一題 {n1}×{n2} = {correct_ans}</span>"
        st.session_state.audio = "wrong"

    # 產生下一題
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
    st.session_state.current_input = ""


st.title("✖️ 九九乘法大挑戰")

# --- 1. 播放音效 ---
if st.session_state.audio == "correct":
    st.markdown(get_correct_audio(), unsafe_allow_html=True)
elif st.session_state.audio == "wrong":
    st.markdown(get_wrong_audio(), unsafe_allow_html=True)
# 播放完立刻清空狀態
st.session_state.audio = None

# --- 2. 顯示：題目(左) + 輸入框(中) + 回饋(右) ---
n1 = st.session_state.num1
n2 = st.session_state.num2

# 根據對錯決定右側文字顏色
feedback_color = "#28a745" if "⭕" in st.session_state.feedback else "#dc3545"
# 決定中間要顯示的文字 (沒輸入時顯示問號)
display_text = st.session_state.current_input if st.session_state.current_input else "?"

st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: center; background-color: white; padding: 15px 25px; border-radius: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 20px;'>
    
    <!-- 左側：題目 -->
    <div style='flex: 1; font-size: 55px; font-weight: bold; color: #333; text-align: left;'>
        {n1} × {n2} =
    </div>
    
    <!-- 中間：輸入顯示區 -->
    <div style='flex: 1; text-align: center;'>
        <div style='display: inline-block; font-size: 60px; font-weight: bold; background-color: #f0f2f6; border-radius: 15px; padding: 0 30px; min-width: 120px; height: 85px; line-height: 85px; color: #31333F;'>
            {display_text}
        </div>
    </div>
    
    <!-- 右側：對錯提示 -->
    <div style='flex: 1; font-size: 24px; color: {feedback_color}; text-align: right; font-weight: bold;'>
        {st.session_state.feedback}
    </div>
    
</div>
""", unsafe_allow_html=True)

# 顯示完回饋後清空
st.session_state.feedback = ""

# --- 3. 虛擬數字九宮格按鈕 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.button("1", on_click=press_digit, args=(1,), use_container_width=True)
    st.button("4", on_click=press_digit, args=(4,), use_container_width=True)
    st.button("7", on_click=press_digit, args=(7,), use_container_width=True)
    st.button("🔙", on_click=press_delete, use_container_width=True)

with col2:
    st.button("2", on_click=press_digit, args=(2,), use_container_width=True)
    st.button("5", on_click=press_digit, args=(5,), use_container_width=True)
    st.button("8", on_click=press_digit, args=(8,), use_container_width=True)
    st.button("0", on_click=press_digit, args=(0,), use_container_width=True)

with col3:
    st.button("3", on_click=press_digit, args=(3,), use_container_width=True)
    st.button("6", on_click=press_digit, args=(6,), use_container_width=True)
    st.button("9", on_click=press_digit, args=(9,), use_container_width=True)
    st.button("🚀", on_click=submit_answer, use_container_width=True, type="primary")

st.divider()

# --- 4. 家長查看區 ---
st.subheader("📊 本次練習記錄")

if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    total = len(df)
    correct_count = len(df[df["結果"] == "⭕ 正確"])
    accuracy = (correct_count / total) * 100
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("已完成", f"{total} 題")
    col_b.metric("答對", f"{correct_count} 題")
    col_c.metric("正確率", f"{accuracy:.1f} %")
    
    st.dataframe(df.iloc[::-1], use_container_width=True)
    
    if st.button("🔄 清空紀錄，重新開始", type="secondary"):
        st.session_state.logs = []
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(1, 9)
        st.session_state.current_input = ""
        st.session_state.feedback = ""
else:
    st.info("作答紀錄會即時顯示在這裡。")
