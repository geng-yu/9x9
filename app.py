import streamlit as st
import random
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="九九乘法練習", layout="centered")

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

# --- 初始化暫存變數 ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "num1" not in st.session_state:
    st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
# 新增：用來記錄上一題的對錯狀態，以便在畫面重整後播放音效與提示
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "audio" not in st.session_state:
    st.session_state.audio = None

st.title("✖️ 九九乘法大挑戰")

# --- 1. 顯示「上一題」的回饋與音效 ---
if st.session_state.feedback:
    if st.session_state.audio == "correct":
        st.success(st.session_state.feedback)
        components.html(get_audio_js("correct"), height=0)
    else:
        st.error(st.session_state.feedback)
        components.html(get_audio_js("wrong"), height=0)
    
    # 顯示完畢後清除狀態，避免一直重複播放
    st.session_state.feedback = None
    st.session_state.audio = None

# --- 2. 顯示「最新」的題目 ---
n1 = st.session_state.num1
n2 = st.session_state.num2
st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin: 20px 0;'>{n1} × {n2} = ？</h1>", unsafe_allow_html=True)

# --- 3. 答案輸入區 ---
with st.form("answer_form", clear_on_submit=True):
    user_input = st.number_input("請輸入答案：", min_value=0, max_value=100, step=1, value=None, placeholder="點此輸入答案")
    submitted = st.form_submit_button("送出答案 🚀", use_container_width=True)

# 當按下送出時的邏輯
if submitted:
    if user_input is None:
        st.warning("請先輸入數字再送出喔！")
    else:
        correct_ans = n1 * n2
        is_correct = (user_input == correct_ans)
        
        # 記錄作答
        st.session_state.logs.append({
            "題目": f"{n1} × {n2}",
            "小孩填寫": int(user_input),
            "正確答案": correct_ans,
            "結果": "⭕ 正確" if is_correct else "❌ 錯誤"
        })
        
        # 設定回饋與音效給下一次重整時顯示
        if is_correct:
            st.session_state.feedback = "🎉 太棒了，答對了！"
            st.session_state.audio = "correct"
        else:
            st.session_state.feedback = f"差一點！剛剛 {n1} × {n2} 的正確答案是：{correct_ans}"
            st.session_state.audio = "wrong"
        
        # 產生下一題的新數字
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(1, 9)
        
        # ★ 關鍵：強制立刻重整網頁，這樣畫面就會立刻換到下一題
        st.rerun()

st.divider()

# --- 4. 家長查看區：即時統計與做題明細 ---
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
    
    # 將最新的記錄顯示在最上面，方便查看
    st.dataframe(df.iloc[::-1], use_container_width=True)
    
    if st.button("🔄 清空紀錄，重新開始", type="secondary"):
        st.session_state.logs = []
        st.session_state.num1 = random.randint(2, 9)
        st.session_state.num2 = random.randint(1, 9)
        st.session_state.feedback = None
        st.rerun()
else:
    st.info("尚未開始作答，作答紀錄會即時顯示在這裡。")
