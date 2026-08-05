import streamlit as st
import json
import sqlite3
import base64
import os
from datetime import datetime
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH BAN ĐẦU & KHỞI TẠO CƠ SỞ DỮ LIỆU
# ==========================================
st.set_page_config(page_title="AI Language Tutor", layout="wide", initial_sidebar_state="collapsed")

DB_FILE = "tutor_progress.db"

def init_db():
    """Khởi tạo SQLite lưu trữ tiến trình học tập của người dùng."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY,
            current_lang TEXT,
            level INTEGER,
            current_lesson TEXT,
            learned_words TEXT,
            streak_days INTEGER,
            last_learned TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    ''')
    
    # Khởi tạo dữ liệu mặc định nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM progress")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO progress (id, current_lang, level, current_lesson, learned_words, streak_days, last_learned)
            VALUES (1, NULL, 1, 'Chưa bắt đầu', '[]', 0, NULL)
        ''')
    conn.commit()
    conn.close()

init_db()

def get_progress():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT current_lang, level, current_lesson, learned_words, streak_days, last_learned FROM progress WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return {
        "current_lang": row[0],
        "level": row[1],
        "current_lesson": row[2],
        "learned_words": json.loads(row[3]),
        "streak_days": row[4],
        "last_learned": row[5]
    }

def update_progress(current_lang, level, current_lesson, learned_words, streak_days):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE progress 
        SET current_lang = ?, level = ?, current_lesson = ?, learned_words = ?, streak_days = ?, last_learned = ?
        WHERE id = 1
    ''', (current_lang, level, current_lesson, json.dumps(learned_words), streak_days, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def save_chat(role, content):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)", 
                   (role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(limit=10):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1] # Đảo chuỗi để đúng thứ tự thời gian

def clear_chat_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

# Khởi tạo trạng thái Session State trong Streamlit
progress_data = get_progress()
if "ai_response" not in st.session_state:
    st.session_state.user_voice_text = ""
    # Nếu đã học trước đó, AI nhắc lại bài cũ. Nếu chưa, AI chào hỏi ban đầu.
    if progress_data["current_lang"]:
        st.session_state.ai_response = f"Chào mừng bạn quay lại! Hôm trước chúng ta đã học đến: Level {progress_data['level']} - {progress_data['current_lesson']}. Hôm nay chúng ta sẽ tiếp tục học {progress_data['current_lang']} nhé!"
    else:
        st.session_state.ai_response = "Xin chào! Mình sẽ đồng hành cùng bạn học ngoại ngữ. Bạn muốn học ngôn ngữ nào trong các ngôn ngữ sau: Anh, Trung, Nhật, Hàn, Pháp, Đức, Tây Ban Nha, Nga, Việt?"

# ==========================================
# 2. GIAO DIỆN PHÍA TRƯỚC (UI) & CSS ANIMATION
# ==========================================

# Thiết kế giao diện tối giản, tối màu (Dark Mode) và nhân vật chuyển động nhấp nháy mắt, nhún nhảy nhẹ
st.markdown("""
<style>
    /* Reset & Dark background */
    .stApp {
        background-color: #121214;
        color: #E2E8F0;
    }
    
    /* Container chính chứa nhân vật */
    .avatar-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem;
        position: relative;
    }

    /* Bong bóng hội thoại kiểu hiện đại */
    .speech-bubble {
        position: relative;
        background: #1F2937;
        border: 2px solid #3B82F6;
        border-radius: 20px;
        padding: 20px;
        max-width: 600px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        line-height: 1.6;
        animation: fadeIn 0.5s ease-in-out;
    }
    .speech-bubble:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        width: 0;
        height: 0;
        border: 15px solid transparent;
        border-top-color: #1F2937;
        border-bottom: 0;
        margin-left: -15px;
        margin-bottom: -15px;
    }

    /* Tạo hình nhân vật Robot bằng SVG nhúng CSS kèm Animation thở + nháy mắt */
    .ai-character {
        width: 220px;
        height: 220px;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><ellipse cx='50' cy='65' rx='30' ry='25' fill='%233B82F6'/><circle cx='50' cy='35' r='20' fill='%232563EB'/><g id='eyes'><circle cx='43' cy='33' r='3' fill='%2300F5FF'/><circle cx='57' cy='33' r='3' fill='%2300F5FF'/></g><rect cx='45' cy='45' width='10' height='3' rx='1' fill='%231D4ED8'/><path d='M 42 18 Q 50 8 50 5' stroke='%232563EB' stroke-width='2' fill='none'/><circle cx='50' cy='5' r='2' fill='%2300F5FF'/></svg>");
        background-size: contain;
        background-repeat: no-repeat;
        animation: float 4s ease-in-out infinite, blink 5s infinite;
    }

    /* Hiệu ứng thở nhẹ */
    @keyframes float {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-10px) scale(1.02); }
        100% { transform: translateY(0px) scale(1); }
    }

    /* Hiệu ứng chớp mắt tự nhiên */
    @keyframes blink {
        0%, 90%, 100% { opacity: 1; }
        93%, 97% { opacity: 0.2; transform: scaleY(0.1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Ẩn header mặc định của Streamlit để tăng độ tối giản */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Hiển thị khu vực nhân vật trung tâm
st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
st.markdown(f'<div class="speech-bubble">{st.session_state.ai_response}</div>', unsafe_allow_html=True)
st.markdown('<div class="ai-character"></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Tách thanh điều khiển đầu vào xuống dưới chân màn hình
col_space1, col_input, col_space2 = st.columns([1, 2, 1])

with col_input:
    # Form cấu hình API Key và cấu hình Giọng nói mở rộng
    with st.expander("⚙️ Cấu hình API OpenAI & Giọng nói"):
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        voice_gender = st.selectbox("Giọng nói AI (TTS)", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], index=4)
        speed = st.slider("Tốc độ nói", min_value=0.5, max_value=1.5, value=1.0, step=0.1)

    # Ô nhập văn bản chính của người dùng
    user_input = st.text_input("Trò chuyện hoặc trả lời Giáo viên AI tại đây:", key="user_text_input", placeholder="Nhập câu trả lời hoặc yêu cầu của bạn...")

    # Khu vực Giả lập Micro (Nhận diện giọng nói STT) do giới hạn môi trường chạy Server
    st.markdown("<p style='text-align:center; font-size:0.9rem; color:#6B7280;'>Mô phỏng Ghi âm bằng Micro (Speech-to-Text):</p>", unsafe_allow_html=True)
    col_mic, col_clear = st.columns(2)
    with col_mic:
        st.caption("Bấm nút giả lập micro để nhập nhanh phát âm mẫu:")
        if st.button("🎤 Bấm để Nói (Giả lập phát âm đúng)", use_container_width=True):
            st.session_state.user_voice_text = "Nǐ hǎo"
            st.info("Đã nhận diện từ Micro: 'Nǐ hǎo'")
    with col_clear:
        st.caption("Xóa tiến trình để học lại từ đầu:")
        if st.button("🗑️ Xóa toàn bộ lịch sử & Học lại", use_container_width=True):
            clear_chat_history()
            update_progress(None, 1, "Chưa bắt đầu", [], 0)
            st.session_state.ai_response = "Hệ thống đã reset. Bạn muốn học ngôn ngữ nào?"
            st.rerun()

# ==========================================
# 3. XỬ LÝ LOGIC TRÍ TUỆ NHÂN TẠO (OPENAI API)
# ==========================================

def call_ai_teacher(prompt_input, current_state, history_logs, api_key):
    """Gửi yêu cầu tới OpenAI gánh vác vai trò Giáo viên bản xứ và chấm điểm."""
    if not api_key:
        return "Vui lòng cấu hình OpenAI API Key trong mục bánh răng cài đặt phía dưới để trò chuyện cùng mình nhé!", None

    client = OpenAI(api_key=api_key)
    
    # Định hình Hệ thống Prompt đóng vai giáo viên chấm điểm gắt gao theo đúng yêu cầu bài học
    system_prompt = f"""
    Bạn là một Giáo viên dạy ngoại ngữ bằng AI tài năng, thân thiện nhưng rất nghiêm khắc trong phát âm.
    Nhiệm vụ của bạn là dẫn dắt người học qua các cấp độ tăng dần:
    - Level 1: Xin chào, Tạm biệt, Cảm ơn.
    - Level 2: Giới thiệu bản thân.
    - Level 3: Gia đình.
    - Level 4: Mua sắm.
