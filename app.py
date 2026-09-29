import streamlit as st
import random
import pandas as pd
import streamlit.components.v1 as components

# 設定頁面大標題與排版
st.set_page_config(page_title="九九乘法練習", layout="centered")

# --- 音效產生器 (使用 Web Audio API，不需要外部音訊檔案，iPad 支援度高) ---
def play_audio(sound_type):
    if sound_type == "correct":
        # 答對：清脆的雙音階 (叮咚)
        js = """
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
        beep(587.33, 0, 0.2);   // D5
        beep(880.00, 150, 0.4); // A5
        </script>
        """
    else:
        # 答錯：低沈警告音 (嘟)
        js = """
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
    components.html(js, height=0)

# --- 初始化暫存變數 ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "num1" not in st.session_state:
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)

# 產生新題目
def next_question():
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)

# --- 介面開始 ---
st.title("✖️ 九九乘法大挑戰")

# 上方題目卡片
n1 = st.session_state.num1
n2 = st.session_state.num2
st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin: 20px 0;'>{n1} × {n2} = ？</h1>", unsafe_allow_html=True)

# 輸入區表單（按送出或 Enter 觸發，避免每打一個數字就重整）
with st.form("answer_form", clear_on_submit=True):
    user_input = st.number_input("請輸入答案：", min_value=0, max_value=100, step=1, value=None, placeholder="點此輸入答案")
    submitted = st.form_submit_button("送出答案 🚀", use_container_width=True)

if submitted:
    if user_input is None:
        st.warning("請先輸入數字再送出喔！")
    else:
        correct_ans = n1 * n2
        is_correct = (user_input == correct_ans)
        
        # 記錄做題結果
        st.session_state.logs.append({
            "題目": f"{n1} × {n2}",
            "小孩填寫": int(user_input),
            "正確答案": correct_ans,
            "結果": "⭕ 正確" if is_correct else "❌ 錯誤"
        })
        
        # 播放音效
        if is_correct:
            play_audio("correct")
            st.success("🎉 太棒了，答對了！")
        else:
            play_audio("wrong")
            st.error(f"差一點！正確答案是：{correct_ans}")
        
        # 換下一題
        next_question()

st.divider()

# --- 家長查看區：即時統計與做題明細 ---
st.subheader("📊 本次練習記錄")

if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    total = len(df)
    correct_count = len(df[df["結果"] == "⭕ 正確"])
    accuracy = (correct_count / total) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("已完成題數", f"{total} 題")
    col2.metric("答對題數", f"{correct_count} 題")
    col3.metric("正確率", f"{accuracy:.1f} %")
    
    # 顯示所有作答明細，錯的題目一目瞭然
    st.dataframe(df, use_container_width=True)
    
    if st.button("🔄 清空紀錄，重新開始", type="secondary"):
        st.session_state.logs = []
        next_question()
        st.rerun()
else:
    st.info("尚未開始作答，作答紀錄會即時顯示在這裡。")
