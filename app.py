import json
import os
import streamlit as st
from openai import OpenAI

# 1. CẤU HÌNH TRANG & CÀI ĐẶT CHUNG
st.set_page_config(
    page_title="AI Language Teacher",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Đường dẫn lưu dữ liệu tiến trình học
DB_FILE = "user_progress.json"


# Hàm tải tiến trình người dùng
def load_progress():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "current_language": None,
        "level": 1,
        "topic": "Xin chào & Khởi đầu",
        "streak": 1,
        "history": [],
    }


# Hàm lưu tiến trình người dùng
def save_progress(progress):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=4)


# Khởi tạo Session State
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "ai_text" not in st.session_state:
    st.session_state.ai_text = (
        "Xin chào! Mình là giáo viên AI của bạn. Bạn muốn học ngôn ngữ nào hôm nay? "
        "(Hãy nhập phía dưới: Tiếng Anh, Tiếng Trung, Tiếng Nhật, Tiếng Hàn, Tiếng Pháp, Tiếng Đức...)"
    )
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "tts_trigger" not in st.session_state:
    st.session_state.tts_trigger = True

# 2. GIAO DIỆN TỐI GIẢN (CSS CUSTOM)
st.markdown(
    """
    <style>
    /* Ẩn toàn bộ menu, header, footer của Streamlit */
    #MainMenu, header, footer {visibility: hidden;}
    .stApp {background-color: #121212; color: #ffffff;}
    
    /* Khung chứa nhân vật hoạt hình */
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, #2a2a3a 0%, #1a1a26 70%);
        border-radius: 50%;
        box-shadow: 0 0 30px rgba(0, 255, 200, 0.2);
        position: relative;
    }
    
    /* Vẽ nhân vật Robot Hoạt hình bằng CSS tinh gọn */
    .robot {
        width: 100px;
        height: 100px;
        background: #00ffcc;
        border-radius: 40px 40px 30px 30px;
        position: relative;
        animation: float 3s ease-in-out infinite;
    }
    .robot::before, .robot::after {
        content: '';
        position: absolute;
        background: #121212;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        top: 35px;
        animation: blink 4s infinite;
    }
    .robot::before { left: 24px; }
    .robot::after { right: 24px; }
    
    .robot-mouth {
        width: 30px;
        height: 8px;
        background: #121212;
        position: absolute;
        bottom: 25px;
        left: 35px;
        border-radius: 0 0 15px 15px;
    }}
    
    /* Hiệu ứng chuyển động nhẹ và nháy mắt */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }
    
    /* Bong bóng hội thoại phía trên */
    .speech-bubble {
        background-color: #222530;
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 15px 25px;
        margin: 10px auto 30px auto;
        max-width: 500px;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 500;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. NHẬN DIỆN VÀ XỬ LÝ LỜI THOẠI CHÍNH (Xử lý OpenAI API)
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    api_key = st.text_input(
        "Nhập OpenAI API Key để kích hoạt giáo viên:", type="password"
    )

# Ô nhập dữ liệu trò chuyện siêu tối giản ngay dưới bóng thoại
user_saying = st.text_input("Trò chuyện với AI tại đây:", key="user_input_text")

if user_saying:
    st.session_state.user_text = user_saying

if st.session_state.user_text and api_key:
    try:
        client = OpenAI(api_key=api_key)
        p = st.session_state.progress

        system_prompt = f"""
        Bạn là một giáo viên dạy ngoại ngữ hoạt hình vui tính, kiên nhẫn.
        Tiến trình hiện tại của học sinh:
        - Ngôn ngữ đang học: {p['current_language'] if p['current_language'] else 'Chưa chọn (Đang đợi học sinh nói tên ngôn ngữ muốn học)'}
        - Cấp độ hiện tại: Level {p['level']} ({p['topic']})
        
        NHIỆM VỤ CỦA BẠN:
        1. Nếu học sinh chưa chọn ngôn ngữ, hãy nhận diện ngôn ngữ họ muốn học từ câu trả lời của họ (Ví dụ: "Tiếng Anh", "Tiếng Trung"...), cập nhật hệ thống và bắt đầu bài học Level 1 (Chào hỏi) bằng ngôn ngữ đó kèm giải thích tiếng Việt ngắn gọn.
        2. Nếu đã có ngôn ngữ, hãy đóng vai người bản xứ dạy học. Luôn nói câu ngoại ngữ trước, viết phiên âm (nếu có), giải thích nghĩa bằng tiếng Việt ngắn gọn.
        3. Chấm điểm hoặc nhận xét phản hồi của học sinh xem chính xác chưa, sửa lỗi sai nếu phát hiện ra lỗi qua văn bản họ đọc lại.
        4. Giữ câu thoại ngắn gọn, tối giản, phù hợp hiển thị trong bong bóng nhỏ.
        """

        messages = [{"role": "system", "content": system_prompt}]
        for chat in p["history"][-6:]:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["ai"]})

        messages.append({"role": "user", "content": st.session_state.user_text})

        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, temperature=0.7
        )

        ai_reply = response.choices.message.content
        st.session_state.ai_text = ai_reply

        if not p["current_language"]:
            for lang in [
                "Anh",
                "Trung",
                "Nhật",
                "Hàn",
                "Pháp",
                "Đức",
                "Tây Ban Nha",
                "Nga",
            ]:
                if lang.lower() in st.session_state.user_text.lower():
                    p["current_language"] = f"Tiếng {lang}"
                    p["level"] = 1
                    p["topic"] = "Xin chào & Tạm biệt"
                    break

        p["history"].append(
            {"user": st.session_state.user_text, "ai": ai_reply}
        )
        save_progress(p)
        st.session_state.tts_trigger = True

    except Exception as e:
        st.session_state.ai_text = (
            f"Có lỗi kết nối AI: {str(e)}. Bạn hãy kiểm tra lại API Key nhé."
        )

    st.session_state.user_text = ""


# 4. HIỂN THỊ GIAO DIỆN CHÍNH (CHỈ CÓ NHÂN VẬT & BONG BÓNG)
st.write("")
st.markdown(
    f'<div class="speech-bubble">{st.session_state.ai_text}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="avatar-container"><div class="robot"><div class="robot-mouth"></div></div></div>',
    unsafe_allow_html=True,
)

st.write("")

# Lựa chọn giọng nói (Nam / Nữ) nằm gọn gàng bên dưới nhân vật
voice_option = st.selectbox(
    "Chọn giọng nói giáo viên AI:",
    ["Nữ (Female Voice)", "Nam (Male Voice)"],
    label_visibility="collapsed",
)
voice_gender = "female" if "Nữ" in voice_option else "male"


# 5. CÔNG CỤ PHÁT ÂM (TTS) & NÚT MICRO SIÊU TO QUA TRÌNH DUYỆT (Dùng Chuỗi Thường Loại Bỏ F-string)
sound_lang = "vi-VN"
if "English" in st.session_state.ai_text or "Hello" in st.session_state.ai_text:
    sound_lang = "en-US"
elif "你好" in st.session_state.ai_text:
    sound_lang = "zh-CN"

# Chuẩn bị dữ liệu an toàn để đưa vào JS, không lo xung đột ngoặc nhọn
ai_say_json = json.dumps(st.session_state.ai_text)
should_speak = "true" if st.session_state.tts_trigger else "false"
st.session_state.tts_trigger = False

# Thành phần Web component HTML/JS an toàn tuyệt đối
html_code = """
<div style="text-align: center; margin-top: 10px;">
    <button id="mic-btn" style="
        width: 110px; 
        height: 110px; 
        border-radius: 50%; 
        border: none; 
        background: linear-gradient(135deg, #ff007f, #7f00ff); 
        color: white; 
        font-size: 42px; 
        cursor: pointer;
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.5);
        transition: all 0.2s ease;
    ">🎤</button>
    <p id="status-text" style="color: #00ffcc; font-size: 15px; margin-top: 15px; font-family: sans-serif; font-weight: bold; letter-spacing: 1px;">
        BẤM VÀO ĐÂY ĐỂ NÓI CHUYỆN
    </p>
</div>

<script>
// Nhận diện biến từ môi trường Python truyền xuống ngầm qua thẻ data
const aiText = {AI_TEXT_PLACEHOLDER};
const shouldSpeak = {SHOULD_SPEAK_PLACEHOLDER};
const soundLang = "{LANG_PLACEHOLDER}";
const voiceGender = "{GENDER_PLACEHOLDER}";

if (shouldSpeak) {
    var msg = new SpeechSynthesisUtterance(aiText);
    msg.lang = soundLang;
    var voices = window.speechSynthesis.getVoices();
    for(var i = 0; i < voices.length; i++) {
        if(voices[i].lang.includes(soundLang.split("-")[0])) {
            if(voiceGender === 'female' && voices[i].name.toLowerCase().includes('female')) {
                msg.voice = voices[i]; break;
            } else if (voiceGender === 'male' && voices[i].name.toLowerCase().includes('male')) {
                msg.voice = voices[i]; break;
            }
        }
    }
    window.speechSynthesis.speak(msg);
}

// Xử lý bộ nhận diện giọng nói tích hợp trình duyệt
const micBtn = document.getElementById('mic-btn');
const statusText = document.getElementById('status-text');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    statusText.innerText = "Trình duyệt không hỗ trợ Mic. Hãy dùng Google Chrome.";
} else {
    const recognition = new SpeechRecognition();
    recognition.lang = 'vi-VN'; 
    recognition.interimResults = false;
    
    let isRecording = false;
    micBtn.addEventListener('click', () => {
