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

# --- 自訂 CSS：鎖死左右滑動、置中卡片、大按鈕 ---
st.markdown("""
<style>
/* 1. 全局鎖死水平捲軸，iPad 無法左右滑動 */
html, body, #root, .main,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
.block-container {
    overflow-x: hidden !important;
    max-width: 100% !important;
    touch-action: pan-y !important;
    box-sizing: border-box !important;
}

/* 2. 限制寬度在 iPad 最佳視覺範圍 */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 620px !important;
    margin: 0 auto !important;
}

/* 3. 題卡本體 */
.question-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #ffffff;
    padding: 12px 18px;
    border-radius: 16px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    margin-bottom: 16px;
    width: 100%;
    box-sizing: border-box;
}

/* 左側：題目 */
.q-left {
    flex: 1.1;
    font-size: 42px;
    font-weight: 800;
    color: #222222;
    text-align: left;
    white-space: nowrap;
}

/* 中間：輸入框 */
.q-mid {
    flex: 0.9;
    text-align: center;
}
.q-mid-box {
    display: inline-block;
    font-size: 44px;
    font-weight: 800;
    background-color: #f1f3f7;
    border-radius: 12px;
    width: 90px;
    height: 64px;
    line-height: 64px;
    color: #2b3445;
    text-align: center;
}

/* 右側：提示 */
.q-right {
    flex: 1;
    font-size: 18px;
    font-weight: bold;
    text-align: right;
    line-height: 1.3;
}

/* 4. 虛擬大按鈕 */
div[data-testid="stButton"] button {
    height: 72px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}
div[data-testid="stButton"] button p {
    font-size: 30px !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

# --- 音效產生器 ---
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

# --- 處理按鈕動作 ---
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

    # 設定回饋
    if is_correct:
        st.session_state.feedback = "⭕ 答對了！"
        st.session_state.audio = "correct"
    else:
        st.session_state.feedback = f"❌ 答錯了！<br><span style='font-size:15px; color:#555;'>正解: {correct_ans}</span>"
        st.session_state.audio = "wrong"

    # 換下一題
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
    st.session_state.current_input = ""

st.title("✖️ 九九乘法大挑戰")

# --- 1. 播放音效 ---
if st.session_state.audio == "correct":
    st.markdown(get_correct_audio(), unsafe_allow_html=True)
elif st.session_state.audio == "wrong":
    st.markdown(get_wrong_audio(), unsafe_allow_html=True)
st.session_state.audio = None

# --- 2. 題卡顯示 ---
n1 = st.session_state.num1
n2 = st.session_state.num2
feedback_color = "#28a745" if "⭕" in st.session_state.feedback else "#dc3545"
display_text = st.session_state.current_input if st.session_state.current_input else "?"
feedback_html = st.session_state.feedback if st.session_state.feedback else "&nbsp;"

card_html = (
    f'<div class="question-card">'
    f'<div class="q-left">{n1} × {n2} =</div>'
    f'<div class="q-mid"><div class="q-mid-box">{display_text}</div></div>'
    f'<div class="q-right" style="color: {feedback_color};">{feedback_html}</div>'
    f'</div>'
)
st.markdown(card_html, unsafe_allow_html=True)
st.session_state.feedback = ""

# --- 3. 虛擬九宮格按鈕 ---
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

# --- 4. 家長查看區（僅統計題數與顯示錯題） ---
st.subheader("📊 練習與錯題記錄")

if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    total = len(df)
    wrong_df = df[df["結果"] == "❌ 錯誤"]
    wrong_count = len(wrong_df)
    
    col_a, col_b = st.columns(2)
    col_a.metric("已測驗題數", f"{total} 題")
    col_b.metric("答錯題數", f"{wrong_count} 題")
    
    if wrong_count > 0:
        st.write("❌ **答錯題目明細：**")
        st.dataframe(
            wrong_df[["題目", "小孩填寫", "正確答案"]].iloc[::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 目前全部答對，沒有任何錯題！")
    
    if st.button("🔄 清空紀錄，重新開始", type="secondary"):
        st.session_state.logs = []
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(1, 9)
        st.session_state.current_input = ""
        st.session_state.feedback = ""
else:
    st.info("作答紀錄會即時顯示在這裡。")
