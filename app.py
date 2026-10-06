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

# --- 自訂 CSS：手機/iPad/電腦全平台自適應 ---
st.markdown("""
<style>
/* 1. 全局鎖死水平捲軸，防止手機/iPad 誤觸左右滑動 */
html, body, #root, .main,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
.block-container {
    overflow-x: hidden !important;
    max-width: 100% !important;
    touch-action: pan-y !important;
    box-sizing: border-box !important;
}

/* 2. 頁面邊距自適應（手機留邊更小、iPad/電腦維持合適寬度） */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    max-width: 580px !important;
    margin: 0 auto !important;
}

/* 3. 關鍵修正：強制 Streamlit 欄位在手機上維持橫向並排，不自動折成垂直單欄 */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 8px !important;
}

[data-testid="stHorizontalBlock"] > div,
[data-testid="stHorizontalBlock"] [data-testid="column"],
[data-testid="stHorizontalBlock"] [data-testid="stColumn"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    width: 100% !important;
}

/* 4. 題卡本體：彈性大小自適應 */
.question-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #ffffff;
    padding: 10px 14px;
    border-radius: 16px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    margin-bottom: 16px;
    width: 100%;
    box-sizing: border-box;
    gap: 6px;
}

/* 左側：題目（手機自動適度微縮，不換行） */
.q-left {
    flex: 1.1;
    font-size: clamp(26px, 7.5vw, 42px);
    font-weight: 800;
    color: #222222;
    text-align: left;
    white-space: nowrap;
}

/* 中間：答案輸入框 */
.q-mid {
    flex: 0.9;
    text-align: center;
}
.q-mid-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(26px, 8vw, 44px);
    font-weight: 800;
    background-color: #f1f3f7;
    border-radius: 12px;
    width: clamp(64px, 18vw, 90px);
    height: clamp(52px, 14vw, 64px);
    color: #2b3445;
    text-align: center;
}

/* 右側：提示/回饋 */
.q-right {
    flex: 1;
    font-size: clamp(14px, 4vw, 18px);
    font-weight: bold;
    text-align: right;
    line-height: 1.25;
    word-break: break-word;
}

/* 5. 虛擬大按鈕：高度與字級隨螢幕彈性調整 */
div[data-testid="stButton"] {
    margin-bottom: 8px !important;
}
div[data-testid="stButton"] button {
    height: clamp(58px, 13vw, 72px) !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 0 !important;
    width: 100% !important;
}
div[data-testid="stButton"] button p {
    font-size: clamp(22px, 6vw, 30px) !important;
    font-weight: bold !important;
    margin: 0 !important;
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
        st.session_state.feedback = f"❌ 答錯了！<br><span style='font-size:14px; color:#555;'>正解: {correct_ans}</span>"
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
