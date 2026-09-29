import streamlit as st
import random
import pandas as pd
import streamlit.components.v1 as components

# 設定頁面排版
st.set_page_config(page_title="九九乘法練習", layout="centered")

# --- 自訂 CSS：把按鈕字體與顯示框變大，適合 iPad 點擊 ---
st.markdown("""
    <style>
    /* 顯示輸入數字的螢幕 */
    .input-screen {
        font-size: 60px;
        font-weight: bold;
        text-align: center;
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        color: #31333F;
        min-height: 90px;
    }
    /* 把所有按鈕變大 */
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

# --- 音效產生器 ---
def get_audio_js(sound_type):
    if sound_type == "correct":
        return """
        <script>
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function beep(freq, delay, dur) {
            setTimeout(() => {
                let osc = ctx.createOscillator();
                let gain = ctx.createGain();
                osc.connect(gain); gain.connect(ctx.destination);
                osc.frequency.value = freq;
                osc.start();
                gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
            }, delay);
        }
        beep(587.33, 0, 0.2);   
        beep(880.00, 150, 0.4); 
        </script>
        """
    else:
        return """
        <script>
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        let osc = ctx.createOscillator();
        let gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = "sawtooth";
        osc.frequency.value = 150;
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
        </script>
        """

# --- 初始化狀態變數 ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "num1" not in st.session_state:
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "audio" not in st.session_state:
    st.session_state.audio = None
# 新增：用來記錄畫面上目前輸入的數字
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

# --- 處理按鈕動作的函式 ---
def press_digit(digit):
    # 限制最多只能輸入 3 位數（因為 9x9 最大也才 81）
    if len(st.session_state.current_input) < 3:
        st.session_state.current_input += str(digit)

def press_delete():
    st.session_state.current_input = st.session_state.current_input[:-1]

def submit_answer():
    # 沒輸入數字直接按送出的防呆
    if not st.session_state.current_input:
        st.session_state.feedback = "⚠️ 請先點擊數字按鈕輸入答案喔！"
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

    # 設定回饋與音效
    if is_correct:
        st.session_state.feedback = "🎉 太棒了，答對了！"
        st.session_state.audio = "correct"
    else:
        st.session_state.feedback = f"差一點！剛剛 {n1} × {n2} 的答案是：{correct_ans}"
        st.session_state.audio = "wrong"

    # 產生下一題
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
    
    # 清空輸入框，準備下一題
    st.session_state.current_input = ""


st.title("✖️ 九九乘法大挑戰")

# --- 1. 顯示「上一題」的回饋與音效 ---
if st.session_state.feedback:
    if st.session_state.audio == "correct":
        st.success(st.session_state.feedback)
        components.html(get_audio_js("correct"), height=0)
    elif st.session_state.audio == "wrong":
        st.error(st.session_state.feedback)
        components.html(get_audio_js("wrong"), height=0)
    else:
        st.warning(st.session_state.feedback) # 用於防呆提示
    
    st.session_state.feedback = None
    st.session_state.audio = None

# --- 2. 顯示「最新」的題目 ---
n1 = st.session_state.num1
n2 = st.session_state.num2
st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin: 10px 0;'>{n1} × {n2} = ？</h1>", unsafe_allow_html=True)

# --- 3. 虛擬輸入框 (顯示目前按下的數字) ---
display_text = st.session_state.current_input if st.session_state.current_input else "?"
st.markdown(f"<div class='input-screen'>{display_text}</div>", unsafe_allow_html=True)

# --- 4. 虛擬數字九宮格按鈕 (類似手機撥號盤排列) ---
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

# --- 5. 家長查看區 ---
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
        st.session_state.feedback = None
        st.rerun()
else:
    st.info("作答紀錄會即時顯示在這裡。")
