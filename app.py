# -*- coding: utf-8 -*-
"""
================================================================================
 AI BUDDY - Người bạn đồng hành học ngoại ngữ (DUY NHẤT 1 FILE app.py)
================================================================================
 CÁCH CHẠY:
     pip install streamlit requests
     streamlit run app.py
================================================================================
"""

import streamlit as st
import json
import os
import random
import re
import datetime
import unicodedata
import streamlit.components.v1 as components

# ==============================================================================
# 1. CẤU HÌNH TRANG & CSS DARK MODE MODERN
# ==============================================================================
st.set_page_config(
    page_title="AI Buddy - Học Ngoại Ngữ",
    page_icon="🐻",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_buddy_data.json")

# ==============================================================================
# 2. GIÁO TRÌNH & NGÔN NGỮ HỖ TRỢ
# ==============================================================================
LANGUAGES = {
    "Tiếng Anh":          {"flag": "🇬🇧", "tts": "en-US", "keywords": ["anh", "english", "tiếng anh"]},
    "Tiếng Trung":        {"flag": "🇨🇳", "tts": "zh-CN", "keywords": ["trung", "chinese", "tiếng trung"]},
    "Tiếng Nhật":         {"flag": "🇯🇵", "tts": "ja-JP", "keywords": ["nhật", "japanese", "tiếng nhật"]},
    "Tiếng Hàn":          {"flag": "🇰🇷", "tts": "ko-KR", "keywords": ["hàn", "korean", "tiếng hàn"]},
    "Tiếng Pháp":         {"flag": "🇫🇷", "tts": "fr-FR", "keywords": ["pháp", "french", "tiếng pháp"]},
    "Tiếng Đức":          {"flag": "🇩🇪", "tts": "de-DE", "keywords": ["đức", "german", "tiếng đức"]},
    "Tiếng Tây Ban Nha":  {"flag": "🇪🇸", "tts": "es-ES", "keywords": ["tây ban nha", "spanish"]},
    "Tiếng Nga":          {"flag": "🇷🇺", "tts": "ru-RU", "keywords": ["nga", "russian", "tiếng nga"]},
    "Tiếng Việt":         {"flag": "🇻🇳", "tts": "vi-VN", "keywords": ["việt", "vietnamese", "tiếng việt"]},
}

LESSON_DB = {
    "Tiếng Anh": [
        {"title": "Level 1: Chào hỏi", "items": [
            {"phrase": "Hello", "meaning": "Xin chào"},
            {"phrase": "Goodbye", "meaning": "Tạm biệt"},
            {"phrase": "Thank you", "meaning": "Cảm ơn"}
        ]},
        {"title": "Level 2: Giới thiệu bản thân", "items": [
            {"phrase": "My name is Alex", "meaning": "Tôi tên là Alex"},
            {"phrase": "Nice to meet you", "meaning": "Rất vui được gặp bạn"}
        ]},
        {"title": "Level 3: Gia đình", "items": [
            {"phrase": "This is my family", "meaning": "Đây là gia đình tôi"},
            {"phrase": "I love my parents", "meaning": "Tôi yêu bố mẹ tôi"}
        ]},
        {"title": "Level 4: Mua sắm", "items": [
            {"phrase": "How much is this?", "meaning": "Cái này bao nhiêu tiền?"},
            {"phrase": "I would like to buy this", "meaning": "Tôi muốn mua cái này"}
        ]}
    ],
    "Tiếng Trung": [
        {"title": "Level 1: Chào hỏi", "items": [
            {"phrase": "你好", "meaning": "Xin chào (Nǐ hǎo)"},
            {"phrase": "再见", "meaning": "Tạm biệt (Zài jiàn)"},
            {"phrase": "谢谢", "meaning": "Cảm ơn (Xiè xie)"}
        ]},
        {"title": "Level 2: Giới thiệu bản thân", "items": [
            {"phrase": "我叫...", "meaning": "Tôi tên là... (Wǒ jiào...)"}
        ]}
    ],
    "Tiếng Nhật": [
        {"title": "Level 1: Chào hỏi", "items": [
            {"phrase": "こんにちは", "meaning": "Xin chào (Konnichiwa)"},
            {"phrase": "さようなら", "meaning": "Tạm biệt (Sayōnara)"},
            {"phrase": "ありがとう", "meaning": "Cảm ơn (Arigatō)"}
        ]}
    ]
}

ROLEPLAY_SCENARIOS = ["Nhà hàng", "Du lịch", "Mua sắm", "Phỏng vấn", "Khách hàng"]

# ==============================================================================
# 3. LƯU TRỮ DỮ LIỆU JSON (BỘ NHỚ DÀI HẠN)
# ==============================================================================
DEFAULT_DATA = {
    "name": "",
    "target_lang": "",
    "level": 1,
    "item_index": 0,
    "words_learned": [],
    "chat_log": [],
    "streak": 1,
    "last_study_date": str(datetime.date.today()),
    "onboard_stage": "ask_language",
    "mode": "lesson", # lesson / roleplay
    "openai_api_key": "",
    "voice_rate": 1.0
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_DATA.copy()
            merged.update(data)
            return merged
        except Exception:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

def save_data():
    try:
        payload = {k: st.session_state[k] for k in DEFAULT_DATA.keys() if k in st.session_state}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def init_state():
    if "loaded" not in st.session_state:
        data = load_data()
        for k, v in data.items():
            st.session_state[k] = v
        st.session_state.loaded = True
        st.session_state.last_speech = ""
        st.session_state.is_speaking = False
        _update_streak()

def _update_streak():
    today = str(datetime.date.today())
    last = st.session_state.last_study_date
    if last != today:
        yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        if last == yesterday:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_study_date = today

init_state()

# ==============================================================================
# 4. LOGIC XỬ LÝ AI & BÀI HỌC
# ==============================================================================
def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize_text(s):
    return strip_accents(s).lower().strip().replace("?", "").replace(".", "").replace(",", "")

def detect_language(text):
    norm = normalize_text(text)
    for lang, meta in LANGUAGES.items():
        for kw in meta["keywords"]:
            if kw in norm:
                return lang
    return None

def current_item():
    lang = st.session_state.target_lang
    plan = LESSON_DB.get(lang, LESSON_DB["Tiếng Anh"])
    lvl_idx = max(0, st.session_state.level - 1)
    if lvl_idx >= len(plan):
        lvl_idx = len(plan) - 1
    items = plan[lvl_idx]["items"]
    item_idx = st.session_state.item_index
    if item_idx >= len(items):
        return items[-1]
    return items[item_idx]

def advance_lesson():
    lang = st.session_state.target_lang
    plan = LESSON_DB.get(lang, LESSON_DB["Tiếng Anh"])
    lvl_idx = st.session_state.level - 1
    items = plan[lvl_idx]["items"] if lvl_idx < len(plan) else []
    
    st.session_state.item_index += 1
    if st.session_state.item_index >= len(items):
        st.session_state.item_index = 0
        st.session_state.level += 1
        if st.session_state.level > len(plan):
            st.session_state.mode = "roleplay"
            return "Hết bài học cơ bản! Giờ chúng ta chuyển sang luyện hội thoại nhập vai nhé!"
        return f"🎉 Chúc mừng! Bạn đã lên Level {st.session_state.level}!"
    return "Tiếp tục bài học tiếp theo nào!"

def process_user_input(user_text):
    if not user_text.strip():
        return
    
    # Lưu tin nhắn người dùng
    st.session_state.chat_log.append({"role": "user", "text": user_text})
    stage = st.session_state.onboard_stage
    reply = ""

    # Giai đoạn 1: Hỏi chọn ngôn ngữ
    if stage == "ask_language":
        detected = detect_language(user_text)
        if detected:
            st.session_state.target_lang = detected
            st.session_state.onboard_stage = "in_lesson"
            
            # Kiểm tra xem có dữ liệu bài cũ không
            curr = current_item()
            reply = f"Được rồi! Hôm nay chúng ta bắt đầu học {detected}.\nBài đầu tiên: '{curr['phrase']}' ({curr['meaning']}). Hãy đọc lại theo mình!"
        else:
            reply = "Mình chưa hiểu rõ ngôn ngữ bạn muốn học. Bạn có thể nói lại ví dụ: 'Tôi muốn học Tiếng Anh' hoặc 'Tiếng Trung' được không?"

    # Giai đoạn 2: Trò chuyện / Học bài
    elif stage == "in_lesson":
        if st.session_state.mode == "lesson":
            curr = current_item()
            target = curr["phrase"]
            
            # So khớp phát âm đơn giản
            if normalize_text(user_text) == normalize_text(target):
                st.session_state.words_learned.append(target)
                adv_msg = advance_lesson()
                next_curr = current_item()
                reply = f"🎯 Rất tốt! Bạn phát âm chính xác 100%.\n{adv_msg}\nTừ tiếp theo: '{next_curr['phrase']}' ({next_curr['meaning']}). Đọc thử xem!"
            else:
                reply = f"😅 Chưa chính xác lắm. Từ đúng là '{target}' ({curr['meaning']}). Bạn hãy nghe kĩ và phát âm lại nhé!"
        else:
            # Chế độ Hội thoại Roleplay
            reply = f"[{st.session_state.target_lang} Roleplay] Cảm ơn bạn! Bạn nói rất tự nhiên. Hãy tiếp tục trò chuyện nhé!"

    # Lưu phản hồi AI & Lưu File
    st.session_state.chat_log.append({"role": "assistant", "text": reply})
    st.session_state.last_speech = reply
    st.session_state.is_speaking = True
    save_data()

# ==============================================================================
# 5. CẢO DIỆN & CSS (FULL SINGLE FILE)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lexend', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        color: #F8FAFC;
    }
    
    /* Bong bóng hội thoại */
    .speech-bubble {
        position: relative;
        background: #334155;
        border: 2px solid #38BDF8;
        border-radius: 20px;
        padding: 18px 24px;
        margin: 10px auto 20px auto;
        max-width: 90%;
        text-align: center;
        font-size: 18px;
        line-height: 1.5;
        color: #F1F5F9;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.25);
        animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .speech-bubble:after {
        content: '';
        position: absolute;
        bottom: -12px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 12px 12px 0;
        border-style: solid;
        border-color: #334155 transparent;
        display: block;
        width: 0;
    }

    /* Khung nhân vật AI */
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0;
    }
    .floating-bear {
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }

    /* Status Bar */
    .status-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 10px 16px;
        display: flex;
        justify-content: space-around;
        margin-bottom: 15px;
        font-size: 14px;
    }

    @keyframes popIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Lời chào tự động khi khởi chạy
if not st.session_state.chat_log:
    if st.session_state.name or st.session_state.target_lang:
        welcome_msg = f"Chào mừng bạn quay lại! Hôm trước chúng ta đã học đến Level {st.session_state.level} ({st.session_state.target_lang}). Hôm nay chúng ta tiếp tục nhé!"
    else:
        welcome_msg = "Xin chào! Mình sẽ đồng hành cùng bạn học ngoại ngữ.\nBạn muốn học ngôn ngữ nào?"
    st.session_state.chat_log.append({"role": "assistant", "text": welcome_msg})
    st.session_state.last_speech = welcome_msg

# Header Status Bar
st.markdown(f"""
<div class="status-card">
    <span>🔥 Streak: <b>{st.session_state.streak} ngày</b></span>
    <span>🌐 Ngôn ngữ: <b>{st.session_state.target_lang or 'Chưa chọn'}</b></span>
    <span>📊 Cấp độ: <b>Level {st.session_state.level}</b></span>
</div>
""", unsafe_allow_html=True)

# Hiển thị bong bóng hội thoại AI gần nhất
latest_ai_msg = [m["text"] for m in st.session_state.chat_log if m["role"] == "assistant"][-1]
st.markdown(f'<div class="speech-bubble">{latest_ai_msg.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. NHÂN VẬT AI HOẠT HÌNH SVG (ĐỨNG GIỮA MÀN HÌNH)
# ==============================================================================
is_talking = st.session_state.is_speaking
st.session_state.is_speaking = False # Reset sau render

svg_bear = f"""
<div class="avatar-container">
    <svg class="floating-bear" width="220" height="220" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Tai -->
        <circle cx="50" cy="50" r="25" fill="#8B5CF6"/>
        <circle cx="50" cy="50" r="14" fill="#DDD6FE"/>
        <circle cx="150" cy="50" r="25" fill="#8B5CF6"/>
        <circle cx="150" cy="50" r="14" fill="#DDD6FE"/>
        
        <!-- Đầu -->
        <circle cx="100" cy="100" r="70" fill="#A78BFA"/>
        
        <!-- Mắt (Có hiệu ứng chớp) -->
        <ellipse cx="75" cy="85" rx="7" ry="10" fill="#0F172A">
            <animate attributeName="ry" values="10; 10; 1; 10" keyTimes="0; 0.9; 0.95; 1" dur="4s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="125" cy="85" rx="7" ry="10" fill="#0F172A">
            <animate attributeName="ry" values="10; 10; 1; 10" keyTimes="0; 0.9; 0.95; 1" dur="4s" repeatCount="indefinite" />
        </ellipse>
        
        <!-- Mũi & Mõm -->
        <ellipse cx="100" cy="110" rx="20" ry="14" fill="#ECE9FE"/>
        <polygon points="100,102 93,110 107,110" fill="#4C1D95"/>
        
        <!-- Miệng (Chuyển động khi nói) -->
        {"<ellipse cx='100' cy='118' rx='8' ry='10' fill='#EF4444'><animate attributeName='ry' values='3;10;3' dur='0.3s' repeatCount='indefinite'/></ellipse>" if is_talking else "<path d='M92 116 Q100 122 108 116' stroke='#4C1D95' stroke-width='3' stroke-linecap='round' fill='none'/>"}
        
        <!-- Má hồng -->
        <circle cx="60" cy="105" r="8" fill="#F472B6" opacity="0.6"/>
        <circle cx="140" cy="105" r="8" fill="#F472B6" opacity="0.6"/>
    </svg>
</div>
"""
st.markdown(svg_bear, unsafe_allow_html=True)

# ==============================================================================
# 7. PHÁT ÂM TTS & MICROPHONE RECOGNITION (HTML5 COMPONENTS)
# ==============================================================================
tts_lang = LANGUAGES.get(st.session_state.target_lang, {}).get("tts", "vi-VN")

# Tự động phát âm câu nói mới nhất của AI
js_speech = f"""
<script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance({json.dumps(st.session_state.last_speech)});
        msg.lang = '{tts_lang}';
        msg.rate = {st.session_state.voice_rate};
        window.speechSynthesis.speak(msg);
    }}
</script>
"""
components.html(js_speech, height=0)

# Khung nhập liệu & Thu âm Micro
st.write("")
col1, col2 = st.columns([5, 1])

with st.container():
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Nhập tin nhắn hoặc phát âm...", placeholder="Nói hoặc nhập câu trả lời tại đây...", key="user_text_input")
        submit_button = st.form_submit_button("Gửi 🚀", use_container_width=True)

    if submit_button and user_input:
        process_user_input(user_input)
        st.rerun()

# Thu âm bằng Web Speech API
st.markdown("### 🎙️ Nhấp để nói:")
st.components.v1.html("""
    <button id="micBtn" style="width:100%; padding:12px; background:#0284C7; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
        🎤 Bật Micro & Nói
    </button>
    <p id="status" style="color:#94A3B8; font-size:12px; text-align:center; margin-top:5px;"></p>
    <script>
        const btn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.interimResults = false;
            
            btn.onclick = () => {
                recognition.start();
                status.innerText = "Đang nghe...";
                btn.style.background = "#EF4444";
            };
            
            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                status.innerText = "Đã nghe: " + text;
                btn.style.background = "#0284C7";
                
                // Gửi văn bản thu âm vào Input của Streamlit
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                if(inputs.length > 0){
                    inputs[0].value = text;
                }
            };
            
            recognition.onerror = () => {
                status.innerText = "Lỗi nhận diện âm thanh.";
                btn.style.background = "#0284C7";
            };
        } else {
            status.innerText = "Trình duyệt không hỗ trợ Web Speech API.";
        }
    </script>
""", height=90)

# ==============================================================================
# 8. CÀI ĐẶT ẨN & API KEY (MỞ RỘNG)
# ==============================================================================
with st.expander("⚙️ Cài đặt nâng cao (API Key & Giọng nói)"):
    api_key = st.text_input("OpenAI API Key (Tuỳ chọn)", value=st.session_state.openai_api_key, type="password")
    rate = st.slider("Tốc độ phát âm AI", 0.5, 1.5, st.session_state.voice_rate, 0.1)
    
    if st.button("Lưu cài đặt"):
        st.session_state.openai_api_key = api_key
        st.session_state.voice_rate = rate
        save_data()
        st.success("Đã lưu!")
