# -*- coding: utf-8 -*-
"""
================================================================================
 AI BUDDY - Người bạn đồng hành học ngoại ngữ (HOÀN CHỈNH - ĐÃ SỬA LỖI)
================================================================================
 CÁCH CHẠY:
     pip install streamlit requests
     streamlit run app.py
================================================================================
"""

import streamlit as st
import json
import os
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
    "Tiếng Anh":          {"flag": "🇬🇧", "tts": "en-US", "stt": "en-US", "keywords": ["anh", "english", "tieng anh", "tiếng anh"]},
    "Tiếng Trung":        {"flag": "🇨🇳", "tts": "zh-CN", "stt": "zh-CN", "keywords": ["trung", "chinese", "tieng trung", "tiếng trung", "han", "hán"]},
    "Tiếng Nhật":         {"flag": "🇯🇵", "tts": "ja-JP", "stt": "ja-JP", "keywords": ["nhat", "nhật", "japanese", "tieng nhat", "tiếng nhật"]},
    "Tiếng Hàn":          {"flag": "🇰🇷", "tts": "ko-KR", "stt": "ko-KR", "keywords": ["han", "hàn", "korean", "tieng han", "tiếng hàn"]},
    "Tiếng Pháp":         {"flag": "🇫🇷", "tts": "fr-FR", "stt": "fr-FR", "keywords": ["phap", "pháp", "french", "tieng phap", "tiếng pháp"]},
    "Tiếng Đức":          {"flag": "🇩🇪", "tts": "de-DE", "stt": "de-DE", "keywords": ["duc", "đức", "german", "tieng duc", "tiếng đức"]},
    "Tiếng Tây Ban Nha":  {"flag": "🇪🇸", "tts": "es-ES", "stt": "es-ES", "keywords": ["tay ban nha", "tây ban nha", "spanish"]},
    "Tiếng Nga":          {"flag": "🇷🇺", "tts": "ru-RU", "stt": "ru-RU", "keywords": ["nga", "russian", "tieng nga", "tiếng nga"]},
    "Tiếng Việt":         {"flag": "🇻🇳", "tts": "vi-VN", "stt": "vi-VN", "keywords": ["viet", "việt", "vietnamese", "tieng viet", "tiếng việt"]},
}

LESSON_DB = {
    "Tiếng Anh": [
        {"title": "Level 1: Chào hỏi", "items": [
            {"phrase": "Hello", "meaning": "Xin chào"},
            {"phrase": "Goodbye", "meaning": "Tạm biệt"},
            {"phrase": "Thank you", "meaning": "Cảm ơn"}
        ]},
        {"title": "Level 2: Giới thiệu", "items": [
            {"phrase": "My name is Alex", "meaning": "Tôi tên là Alex"},
            {"phrase": "Nice to meet you", "meaning": "Rất vui được gặp bạn"}
        ]}
    ],
    "Tiếng Trung": [
        {"title": "Level 1: Chào hỏi", "items": [
            {"phrase": "你好", "meaning": "Xin chào (Nǐ hǎo)"},
            {"phrase": "再见", "meaning": "Tạm biệt (Zài jiàn)"},
            {"phrase": "谢谢", "meaning": "Cảm ơn (Xiè xie)"}
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

# ==============================================================================
# 3. LƯU TRỮ DỮ LIỆU JSON
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
    "mode": "lesson",
    "voice_rate": 0.95
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
        st.session_state.tts_lang_code = "vi-VN"
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
    return strip_accents(s).lower().strip().replace("?", "").replace(".", "").replace(",", "").replace("!", "")

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
            return "Bạn đã hoàn thành các bài cơ bản! Chúng ta hãy cùng luyện hội thoại tự do nhé!"
        return f"🎉 Tuyệt vời! Bạn đã vượt qua và bước sang Level {st.session_state.level}!"
    return "Hãy cùng luyện tập từ tiếp theo nào!"

def set_target_language(lang_name):
    st.session_state.target_lang = lang_name
    st.session_state.onboard_stage = "in_lesson"
    curr = current_item()
    reply = f"Được rồi! Chúng ta sẽ học {lang_name}.\nBài đầu tiên: '{curr['phrase']}' nghĩa là ({curr['meaning']}). Hãy đọc thử lại từ này nhé!"
    
    st.session_state.chat_log.append({"role": "assistant", "text": reply})
    st.session_state.last_speech = reply
    st.session_state.tts_lang_code = "vi-VN"
    st.session_state.is_speaking = True
    save_data()

def process_user_input(user_text):
    if not user_text.strip():
        return
    
    st.session_state.chat_log.append({"role": "user", "text": user_text})
    stage = st.session_state.onboard_stage
    reply = ""
    tts_code = "vi-VN"

    if stage == "ask_language":
        detected = detect_language(user_text)
        if detected:
            set_target_language(detected)
            return
        else:
            reply = "Mình chưa nhận diện được ngôn ngữ bạn chọn. Bạn hãy bấm vào nút chọn ngôn ngữ bên dưới hoặc nhập lại nhé!"
            tts_code = "vi-VN"

    elif stage == "in_lesson":
        if st.session_state.mode == "lesson":
            curr = current_item()
            target = curr["phrase"]
            
            # So khớp chuỗi phát âm
            if normalize_text(user_text) == normalize_text(target):
                st.session_state.words_learned.append(target)
                adv_msg = advance_lesson()
                next_curr = current_item()
                reply = f"🎯 Rất chuẩn xác!\n{adv_msg}\nTừ tiếp theo là: '{next_curr['phrase']}' ({next_curr['meaning']}). Đọc thử nhé!"
                tts_code = "vi-VN"
            else:
                reply = f"😅 Chưa chính xác lắm. Từ đúng là '{target}' ({curr['meaning']}). Bạn hãy nghe và đọc lại nhé!"
                tts_code = "vi-VN"
        else:
            reply = f"Cảm ơn bạn! Bạn phát âm rất tự nhiên. Hãy tiếp tục trò chuyện nhé!"
            tts_code = LANGUAGES.get(st.session_state.target_lang, {}).get("tts", "vi-VN")

    st.session_state.chat_log.append({"role": "assistant", "text": reply})
    st.session_state.last_speech = reply
    st.session_state.tts_lang_code = tts_code
    st.session_state.is_speaking = True
    save_data()

# ==============================================================================
# 5. GIAO DIỆN & CSS
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
    
    .speech-bubble {
        position: relative;
        background: #334155;
        border: 2px solid #38BDF8;
        border-radius: 20px;
        padding: 16px 20px;
        margin: 10px auto 15px auto;
        max-width: 95%;
        text-align: center;
        font-size: 17px;
        line-height: 1.5;
        color: #F1F5F9;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.25);
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
</style>
""", unsafe_allow_html=True)

# Khởi tạo tin nhắn chào hỏi ban đầu nếu lịch sử trống
if not st.session_state.chat_log:
    welcome_msg = "Xin chào! Mình là AI Buddy. Bạn muốn cùng mình học ngôn ngữ nào dưới đây?"
    st.session_state.chat_log.append({"role": "assistant", "text": welcome_msg})
    st.session_state.last_speech = welcome_msg
    st.session_state.tts_lang_code = "vi-VN"

# Header Status Bar
st.markdown(f"""
<div class="status-card">
    <span>🔥 Streak: <b>{st.session_state.streak} ngày</b></span>
    <span>🌐 Ngôn ngữ: <b>{st.session_state.target_lang or 'Chưa chọn'}</b></span>
    <span>📊 Cấp độ: <b>Level {st.session_state.level}</b></span>
</div>
""", unsafe_allow_html=True)

# Lấy tin nhắn AI mới nhất an toàn
assistant_msgs = [m["text"] for m in st.session_state.chat_log if m.get("role") == "assistant"]
latest_ai_msg = assistant_msgs[-1] if assistant_msgs else "Xin chào! Bạn muốn học ngôn ngữ nào?"

st.markdown(f'<div class="speech-bubble">{latest_ai_msg.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. NHÂN VẬT AI HOẠT HÌNH SVG (SỬA LỖI HIỂN THỊ TRÊN MỌI TRÌNH DUYỆT)
# ==============================================================================
is_talking = st.session_state.is_speaking

mouth_svg = (
    "<ellipse cx='100' cy='118' rx='8' ry='10' fill='#EF4444'>"
    "<animate attributeName='ry' values='3;10;3' dur='0.2s' repeatCount='indefinite'/>"
    "</ellipse>"
    if is_talking
    else "<path d='M92 116 Q100 122 108 116' stroke='#4C1D95' stroke-width='3' stroke-linecap='round' fill='none'/>"
)

svg_bear_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }}
    .floating-bear {{
        animation: float 3s ease-in-out infinite;
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
</style>
</head>
<body>
    <svg class="floating-bear" width="180" height="180" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="25" fill="#8B5CF6"/>
        <circle cx="50" cy="50" r="14" fill="#DDD6FE"/>
        <circle cx="150" cy="50" r="25" fill="#8B5CF6"/>
        <circle cx="150" cy="50" r="14" fill="#DDD6FE"/>
        <circle cx="100" cy="100" r="70" fill="#A78BFA"/>
        <ellipse cx="75" cy="85" rx="7" ry="10" fill="#0F172A">
            <animate attributeName="ry" values="10; 10; 1; 10" keyTimes="0; 0.9; 0.95; 1" dur="4s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="125" cy="85" rx="7" ry="10" fill="#0F172A">
            <animate attributeName="ry" values="10; 10; 1; 10" keyTimes="0; 0.9; 0.95; 1" dur="4s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="100" cy="110" rx="20" ry="14" fill="#ECE9FE"/>
        <polygon points="100,102 93,110 107,110" fill="#4C1D95"/>
        {mouth_svg}
        <circle cx="60" cy="105" r="8" fill="#F472B6" opacity="0.6"/>
        <circle cx="140" cy="105" r="8" fill="#F472B6" opacity="0.6"/>
    </svg>
</body>
</html>
"""
components.html(svg_bear_html, height=190)

# ==============================================================================
# 7. ĐIỀU KHIỂN ÂM THANH (TTS LỒNG TIẾNG VÀ MICRO CHUẨN)
# ==============================================================================
# Xác định ngôn ngữ STT (Micro): Khi hỏi ngôn ngữ thì dùng tiếng Việt, khi luyện bài dùng ngôn ngữ mục tiêu
if st.session_state.onboard_stage == "ask_language":
    stt_lang = "vi-VN"
else:
    stt_lang = LANGUAGES.get(st.session_state.target_lang, {}).get("stt", "en-US")

tts_lang = st.session_state.tts_lang_code
speech_text = st.session_state.last_speech or latest_ai_msg

if st.session_state.is_speaking:
    st.session_state.is_speaking = False

components.html(f"""
    <div style="display:flex; gap:10px; font-family:sans-serif;">
        <button id="speakBtn" style="flex:1; padding:12px; background:#8B5CF6; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🔊 Nghe AI nói
        </button>
        <button id="micBtn" style="flex:1; padding:12px; background:#0284C7; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🎤 Bật Micro & Nói ({stt_lang})
        </button>
    </div>
    <p id="status" style="color:#94A3B8; font-size:12px; text-align:center; margin-top:6px; margin-bottom:0;"></p>

    <script>
        const speakBtn = document.getElementById('speakBtn');
        const micBtn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        
        const textToSpeak = {json.dumps(speech_text)};
        const ttsLang = {json.dumps(tts_lang)};
        const sttLang = {json.dumps(stt_lang)};

        // Hàm chọn giọng nói chất lượng nhất (Lồng tiếng chuẩn)
        function speak() {{
            if (!('speechSynthesis' in window)) {{
                status.innerText = "Trình duyệt không hỗ trợ phát âm.";
                return;
            }}
            
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(textToSpeak);
            msg.rate = {st.session_state.voice_rate};
            
            // Tìm giọng đọc ưu tiên (Natural / Premium / Google / Microsoft)
            const voices = window.speechSynthesis.getVoices();
            let selectedVoice = voices.find(v => v.lang.includes(ttsLang) && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Online")));
            if (!selectedVoice) {{
                selectedVoice = voices.find(v => v.lang.startsWith(ttsLang.split('-')[0]));
            }}
            if (selectedVoice) {{
                msg.voice = selectedVoice;
            }}
            msg.lang = ttsLang;

            msg.onstart = () => {{ status.innerText = "🔊 AI đang nói..."; }};
            msg.onend = () => {{ status.innerText = ""; }};
            
            window.speechSynthesis.speak(msg);
        }}

        speakBtn.onclick = speak;

        // Tự động kích hoạt phát âm khi chọn bài mới
        setTimeout(speak, 200);

        // Xử lý Micro thu âm
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = sttLang;
            recognition.interimResults = false;
            
            micBtn.onclick = () => {{
                try {{
                    recognition.start();
                    status.innerText = "Đang lắng nghe...";
                    micBtn.style.background = "#EF4444";
                }} catch (e) {{
                    recognition.stop();
                }}
            }};
            
            recognition.onresult = (event) => {{
                const text = event.results[0][0].transcript;
                status.innerText = "Đã nghe: " + text;
                micBtn.style.background = "#0284C7";
                
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                if(inputs.length > 0){{
                    inputs[0].value = text;
                }}
            }};
            
            recognition.onerror = () => {{
                status.innerText = "Lỗi nhận diện âm thanh. Vui lòng thử lại.";
                micBtn.style.background = "#0284C7";
            }};
        }} else {{
            status.innerText = "Trình duyệt không hỗ trợ thu âm Micro.";
        }}
    </script>
""", height=90)

# ==============================================================================
# 8. KHU VỰC CHỌN NGÔN NGỮ BẰNG NÚT BẤM VÀ KHUNG NHẬP LIỆU
# ==============================================================================
if st.session_state.onboard_stage == "ask_language":
    st.write("👉 **Chọn nhanh ngôn ngữ bạn muốn học:**")
    cols = st.columns(3)
    idx = 0
    for lang_name, meta in LANGUAGES.items():
        if lang_name != "Tiếng Việt":
            with cols[idx % 3]:
                if st.button(f"{meta['flag']} {lang_name}", use_container_width=True):
                    set_target_language(lang_name)
                    st.rerun()
            idx += 1

with st.container():
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Nhập tin nhắn hoặc nội dung phát âm...", placeholder="Gõ câu trả lời hoặc dùng Micro...", key="user_text_input")
        submit_button = st.form_submit_button("Gửi 🚀", use_container_width=True)

    if submit_button and user_input:
        process_user_input(user_input)
        st.rerun()

# ==============================================================================
# 9. CÀI ĐẶT NÂNG CAO
# ==============================================================================
with st.expander("⚙️ Cài đặt giọng nói & Bộ nhớ"):
    rate = st.slider("Tốc độ đọc của AI", 0.5, 1.5, st.session_state.voice_rate, 0.05)
    if st.button("Đổi ngôn ngữ muốn học"):
        st.session_state.onboard_stage = "ask_language"
        st.session_state.target_lang = ""
        save_data()
        st.rerun()
    if st.button("Lưu cài đặt"):
        st.session_state.voice_rate = rate
        save_data()
        st.success("Đã lưu thành công!")
