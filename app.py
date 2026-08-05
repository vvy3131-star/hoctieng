# -*- coding: utf-8 -*-
"""
================================================================================
 AI BUDDY - THẦY GIÁO GIA TRƯỜNG (TỐI ƯU TỐC ĐỘ & CHỦ ĐỘNG DẠY BÀI)
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
# 1. CẤU HÌNH TRANG & CSS
# ==============================================================================
st.set_page_config(
    page_title="AI Buddy - Thầy Giáo Gia Trưởng",
    page_icon="🐻",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_buddy_data.json")

# ==============================================================================
# 2. GIÁO TRÌNH & NGÔN NGỮ
# ==============================================================================
LANGUAGES = {
    "Tiếng Anh":          {"flag": "🇬🇧", "tts": "en-US", "stt": "vi-VN", "keywords": ["anh", "english", "tieng anh", "tiếng anh"]},
    "Tiếng Trung":        {"flag": "🇨🇳", "tts": "zh-CN", "stt": "vi-VN", "keywords": ["trung", "chinese", "tieng trung", "tiếng trung", "han", "hán"]},
    "Tiếng Nhật":         {"flag": "🇯🇵", "tts": "ja-JP", "stt": "vi-VN", "keywords": ["nhat", "nhật", "japanese", "tieng nhat", "tiếng nhật"]},
    "Tiếng Hàn":          {"flag": "🇰🇷", "tts": "ko-KR", "stt": "vi-VN", "keywords": ["han", "hàn", "korean", "tieng han", "tiếng hàn"]},
    "Tiếng Pháp":         {"flag": "🇫🇷", "tts": "fr-FR", "stt": "vi-VN", "keywords": ["phap", "pháp", "french", "tieng phap", "tiếng pháp"]},
    "Tiếng Đức":          {"flag": "🇩🇪", "tts": "de-DE", "stt": "vi-VN", "keywords": ["duc", "đức", "german", "tieng duc", "tiếng đức"]},
    "Tiếng Tây Ban Nha":  {"flag": "🇪🇸", "tts": "es-ES", "stt": "vi-VN", "keywords": ["tay ban nha", "tây ban nha", "spanish"]},
    "Tiếng Nga":          {"flag": "🇷🇺", "tts": "ru-RU", "stt": "vi-VN", "keywords": ["nga", "russian", "tieng nga", "tiếng nga"]},
}

LESSON_DB = {
    "Tiếng Anh": [
        {"title": "Level 1: Chào hỏi", "items": [
            {
                "phrase": "Hello", 
                "meaning": "Xin chào", 
                "guide": "Trọng âm nhấn vào âm tiết thứ hai /həˈloʊ/. Mở rộng khẩu hình âm 'OH', không đọc thành 'hê-lô'!"
            },
            {
                "phrase": "Thank you", 
                "meaning": "Cảm ơn", 
                "guide": "Âm /θ/ phải đặt đầu lưỡi giữa hai răng rồi thổi hơi ra. Không đọc thành 'Tăn kiu'!"
            }
        ]}
    ],
    "Tiếng Trung": [
        {"title": "Level 1: Chào hỏi cơ bản", "items": [
            {
                "phrase": "你好", 
                "meaning": "Xin chào (Nǐ hǎo)", 
                "guide": "Hai thanh 3 đi liền nhau! Phải biến điệu thanh đầu thành thanh 2: Đọc là 'Ní hảo', không đọc 'Nỉ hảo'!"
            },
            {
                "phrase": "谢谢", 
                "meaning": "Cảm ơn (Xiè xie)", 
                "guide": "Thanh 4 nhấn giọng dứt khoát 'Xiè', từ sau đọc thanh nhẹ lướt 'xie'."
            }
        ]}
    ],
    "Tiếng Nhật": [
        {"title": "Level 1: Chào hỏi", "items": [
            {
                "phrase": "こんにちは", 
                "meaning": "Xin chào (Konnichiwa)", 
                "guide": "Âm 'n' đứng giữa ngắt nhẹ một nhịp. Âm 'ha' ở cuối đọc thành 'wa'."
            }
        ]}
    ]
}

# ==============================================================================
# 3. LƯU TRỮ DỮ LIỆU
# ==============================================================================
DEFAULT_DATA = {
    "target_lang": "",
    "level": 1,
    "item_index": 0,
    "words_learned": [],
    "chat_log": [],
    "streak": 1,
    "last_study_date": str(datetime.date.today()),
    "onboard_stage": "ask_language",
    "voice_rate": 0.95,
    "last_speech_seq": []
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
        st.session_state.is_speaking = False

init_state()

# ==============================================================================
# 4. LOGIC XỬ LÝ AI - CHỦ ĐỘNG DẠY BÀI
# ==============================================================================
def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize_text(s):
    return strip_accents(s).lower().strip().replace("?", "").replace(".", "").replace(",", "").replace("!", "")

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

def set_target_language(lang_name):
    st.session_state.target_lang = lang_name
    st.session_state.onboard_stage = "in_lesson"
    curr = current_item()
    target_tts = LANGUAGES[lang_name]["tts"]
    
    # Chủ động vào thẳng bài học
    display_text = f"Vào học {lang_name} ngay! Không lằng nhằng!\n\n📘 BÀI HỌC 1:\nTừ vựng: '{curr['phrase']}' ({curr['meaning']})\n📌 CÁCH ĐỌC CHUẨN: {curr['guide']}\n\n👉 Nhìn kỹ hướng dẫn rồi đọc lại bằng tiếng Việt hoặc đọc theo từ mẫu cho tao nghe!"
    
    tts_seq = [
        {"lang": "vi-VN", "text": f"Vào học {lang_name} ngay! Bài 1. Từ vựng: "},
        {"lang": target_tts, "text": curr['phrase']},
        {"lang": "vi-VN", "text": f" nghĩa là {curr['meaning']}. Lưu ý cách đọc: {curr['guide']}. Đọc lại ngay!"}
    ]
    
    st.session_state.chat_log.append({"role": "assistant", "text": display_text})
    st.session_state.last_speech_seq = tts_seq
    st.session_state.is_speaking = True
    save_data()

def process_user_input(user_text):
    if not user_text.strip():
        return
    
    st.session_state.chat_log.append({"role": "user", "text": user_text})
    curr = current_item()
    target = curr["phrase"]
    target_tts = LANGUAGES[st.session_state.target_lang]["tts"]
    
    norm_user = normalize_text(user_text)
    norm_target = normalize_text(target)
    norm_meaning = normalize_text(curr["meaning"])

    # Nhận diện chính xác dù đọc bằng từ mẫu hay giải thích bằng tiếng Việt
    if norm_target in norm_user or norm_meaning in norm_user or norm_user == norm_target:
        st.session_state.item_index += 1
        plan = LESSON_DB.get(st.session_state.target_lang, LESSON_DB["Tiếng Anh"])
        if st.session_state.item_index >= len(plan[st.session_state.level - 1]["items"]):
            st.session_state.item_index = 0
            st.session_state.level += 1

        next_curr = current_item()
        display_text = f"😤 Tạm chấp nhận được! Qua bài tiếp theo ngay:\n\n📘 BÀI HỌC TỚI:\nTừ vựng: '{next_curr['phrase']}' ({next_curr['meaning']})\n📌 CÁCH ĐỌC CHUẨN: {next_curr['guide']}\n\n👉 Đọc tiếp ngay!"
        
        tts_seq = [
            {"lang": "vi-VN", "text": "Tạm chấp nhận được! Qua bài tiếp theo ngay. Từ vựng: "},
            {"lang": target_tts, "text": next_curr['phrase']},
            {"lang": "vi-VN", "text": f" nghĩa là {next_curr['meaning']}. Cách đọc: {next_curr['guide']}. Đọc tiếp ngay!"}
        ]
    else:
        # Chửi nghiêm khắc khi phát âm/nói sai
        display_text = f"🤬 Sai rồi! Nhìn bài giảng đây này!\nTừ đúng là '{target}' ({curr['meaning']}).\nMày vừa nói '{user_text}' là chưa chuẩn.\n📌 CÁCH ĐỌC CHUẨN: {curr['guide']}\n\n👉 Nghe lại rồi đọc lại ngay!"
        
        tts_seq = [
            {"lang": "vi-VN", "text": "Sai rồi! Nhìn bài giảng đây này! Từ đúng là "},
            {"lang": target_tts, "text": target},
            {"lang": "vi-VN", "text": f" nghĩa là {curr['meaning']}. Bạn nói chưa đúng. Lưu ý: {curr['guide']}. Đọc lại ngay!"}
        ]

    st.session_state.chat_log.append({"role": "assistant", "text": display_text})
    st.session_state.last_speech_seq = tts_seq
    st.session_state.is_speaking = True
    save_data()

# ==============================================================================
# 5. GIAO DIỆN & CSS
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Lexend', sans-serif; }
    .stApp { background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%); color: #F8FAFC; }
    
    .speech-bubble {
        position: relative; background: #1E293B; border: 2px solid #EF4444;
        border-radius: 16px; padding: 16px 20px; margin: 10px auto;
        max-width: 100%; text-align: left; font-size: 15px; line-height: 1.6; color: #F1F5F9;
        box-shadow: 0 8px 20px -5px rgba(239, 68, 68, 0.3);
    }
    .status-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid #475569;
        border-radius: 12px; padding: 10px 16px; display: flex;
        justify-content: space-around; margin-bottom: 10px; font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.chat_log:
    welcome_msg = "Chọn ngôn ngữ bên dưới ngay để bắt đầu bài học!"
    st.session_state.chat_log.append({"role": "assistant", "text": welcome_msg})
    st.session_state.last_speech_seq = [{"lang": "vi-VN", "text": welcome_msg}]

st.markdown(f"""
<div class="status-card">
    <span>🌐 Ngôn ngữ: <b>{st.session_state.target_lang or 'Chưa chọn'}</b></span>
    <span>📊 Cấp độ: <b>Level {st.session_state.level}</b></span>
</div>
""", unsafe_allow_html=True)

assistant_msgs = [m["text"] for m in st.session_state.chat_log if m.get("role") == "assistant"]
latest_ai_msg = assistant_msgs[-1] if assistant_msgs else ""
st.markdown(f'<div class="speech-bubble">{latest_ai_msg.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. NHÂN VẬT SVG
# ==============================================================================
is_talking = st.session_state.is_speaking
mouth_svg = (
    "<ellipse cx='100' cy='118' rx='10' ry='12' fill='#EF4444'>"
    "<animate attributeName='ry' values='4;12;4' dur='0.15s' repeatCount='indefinite'/>"
    "</ellipse>"
    if is_talking
    else "<path d='M85 120 Q100 110 115 120' stroke='#EF4444' stroke-width='4' stroke-linecap='round' fill='none'/>"
)

svg_bear_html = f"""
<!DOCTYPE html><html><head><style>
    body {{ margin: 0; padding: 0; background: transparent; display: flex; justify-content: center; align-items: center; overflow: hidden; }}
</style></head><body>
    <svg width="150" height="150" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="25" fill="#475569"/> <circle cx="50" cy="50" r="14" fill="#94A3B8"/>
        <circle cx="150" cy="50" r="25" fill="#475569"/> <circle cx="150" cy="50" r="14" fill="#94A3B8"/>
        <circle cx="100" cy="100" r="70" fill="#64748B"/>
        <path d="M60 68 L85 78" stroke="#0F172A" stroke-width="5" stroke-linecap="round"/>
        <path d="M140 68 L115 78" stroke="#0F172A" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="75" cy="88" rx="6" ry="8" fill="#0F172A"/>
        <ellipse cx="125" cy="88" rx="6" ry="8" fill="#0F172A"/>
        <ellipse cx="100" cy="108" rx="16" ry="10" fill="#E2E8F0"/>
        <polygon points="100,102 94,108 106,108" fill="#0F172A"/>
        {mouth_svg}
    </svg>
</body></html>
"""
components.html(svg_bear_html, height=160)

# ==============================================================================
# 7. TỐI ƯU ÂM THANH & MICRO (NÓI TIẾNG VIỆT & PHẢN HỒI SIÊU TỐC)
# ==============================================================================
stt_lang = "vi-VN" # Mặc định cho phép nói tiếng Việt thoải mái
tts_sequence_json = json.dumps(st.session_state.last_speech_seq)

if st.session_state.is_speaking:
    st.session_state.is_speaking = False

components.html(f"""
    <div style="display:flex; gap:10px; font-family:sans-serif;">
        <button id="speakBtn" style="flex:1; padding:12px; background:#DC2626; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🔊 Nghe lại giảng
        </button>
        <button id="micBtn" style="flex:1; padding:12px; background:#0284C7; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🎤 Bật Micro Trả Lời
        </button>
    </div>
    <p id="status" style="color:#94A3B8; font-size:12px; text-align:center; margin-top:6px; margin-bottom:0;"></p>

    <script>
        const speakBtn = document.getElementById('speakBtn');
        const micBtn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        
        const sequence = {tts_sequence_json};
        const sttLang = "{stt_lang}";
        const voiceRate = {st.session_state.voice_rate};
        let currentVoiceIdx = 0;

        function speakNextSegment() {{
            if (currentVoiceIdx >= sequence.length) {{
                status.innerText = "";
                return;
            }}
            
            const part = sequence[currentVoiceIdx];
            if (!part.text.trim()) {{
                currentVoiceIdx++;
                speakNextSegment();
                return;
            }}

            const msg = new SpeechSynthesisUtterance(part.text);
            msg.lang = part.lang;
            msg.rate = voiceRate;
            
            const voices = window.speechSynthesis.getVoices();
            let voice = voices.find(v => v.lang.includes(part.lang) && (v.name.includes("Natural") || v.name.includes("Google")));
            if (!voice) voice = voices.find(v => v.lang.includes(part.lang));
            if (voice) msg.voice = voice;

            msg.onstart = () => {{ status.innerText = "🔊 Đang giảng bài..."; }};
            msg.onend = () => {{ 
                currentVoiceIdx++;
                speakNextSegment();
            }};
            msg.onerror = () => {{
                currentVoiceIdx++;
                speakNextSegment();
            }};
            
            window.speechSynthesis.speak(msg);
        }}

        function startSpeaking() {{
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            currentVoiceIdx = 0;
            speakNextSegment();
        }}

        speakBtn.onclick = startSpeaking;
        setTimeout(startSpeaking, 100);

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = sttLang;
            recognition.interimResults = false;
            
            micBtn.onclick = () => {{
                try {{
                    window.speechSynthesis.cancel();
                    recognition.start();
                    status.innerText = "🎤 Đang nghe...";
                    micBtn.style.background = "#DC2626";
                }} catch (e) {{
                    recognition.stop();
                }}
            }};
            
            recognition.onresult = (event) => {{
                const text = event.results[0][0].transcript;
                status.innerText = "Đã nghe: " + text;
                micBtn.style.background = "#0284C7";
                
                const doc = window.parent.document;
                const inputField = doc.querySelector('input[type="text"]');
                
                if (inputField) {{
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(inputField, text);
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));

                    // Xử lý nộp ngay lập tức (100ms)
                    setTimeout(() => {{
                        const submitBtn = doc.querySelector('button[kind="formSubmit"]');
                        if (submitBtn) submitBtn.click();
                    }}, 100);
                }}
            }};
            
            recognition.onerror = () => {{
                status.innerText = "Chưa nghe thấy gì cả!";
                micBtn.style.background = "#0284C7";
            }};
        }}
    </script>
""", height=80)

# ==============================================================================
# 8. BẢNG CHỌN NGÔN NGỮ & BÀI HỌC
# ==============================================================================
if st.session_state.onboard_stage == "ask_language":
    st.write("👉 **Bấm chọn ngôn ngữ để vào học ngay:**")
    cols = st.columns(3)
    idx = 0
    for lang_name, meta in LANGUAGES.items():
        with cols[idx % 3]:
            if st.button(f"{meta['flag']} {lang_name}", use_container_width=True):
                set_target_language(lang_name)
                st.rerun()
        idx += 1

with st.container():
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Trả lời bài học...", placeholder="Nói hoặc gõ bằng tiếng Việt / từ vựng...", key="user_text_input")
        submit_button = st.form_submit_button("Nộp bài 🚀", use_container_width=True)

    if submit_button and user_input:
        process_user_input(user_input)
        st.rerun()
