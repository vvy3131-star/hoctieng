# -*- coding: utf-8 -*-
"""
================================================================================
 AI BUDDY - THẦY GIÁO GIA TRƯỞNG & HƯỚNG DẪN PHÁT ÂM CHI TIẾT
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
    page_title="AI Buddy - Thầy Giáo Khó Tính",
    page_icon="🐻",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_buddy_data.json")

# ==============================================================================
# 2. GIÁO TRÌNH VỚI LƯU Ý PHÁT ÂM CHI TIẾT
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
            {
                "phrase": "Hello", 
                "meaning": "Xin chào", 
                "guide": "Trọng âm nhấn vào âm tiết thứ hai /həˈloʊ/. Mồm mở rộng khẩu hình âm 'OH', không đọc thành 'hê-lô' kiểu Việt Nam!"
            },
            {
                "phrase": "Thank you", 
                "meaning": "Cảm ơn", 
                "guide": "Âm /θ/ phải lè đầu lưỡi ra giữa hai răng rồi thổi hơi ra nhẹ nhàng. Không được đọc thành 'Săn kiu' hay 'Tăn kiu'!"
            },
            {
                "phrase": "Goodbye", 
                "meaning": "Tạm biệt", 
                "guide": "Âm 'd' ở giữa đọc lướt nhẹ, kết thúc bằng âm 'bAĐ' /ɡʊdˈbaɪ/. Đọc dứt khoát!"
            }
        ]},
        {"title": "Level 2: Giao tiếp thực tế", "items": [
            {
                "phrase": "Nice to meet you", 
                "meaning": "Rất vui được gặp bạn", 
                "guide": "Chú ý âm cuối /s/ của 'Nice' và âm /t/ nối sang 'you' đọc thành 'Nai-xơ tu mút iu' mượt mà!"
            }
        ]}
    ],
    "Tiếng Trung": [
        {"title": "Level 1: Chào hỏi cơ bản", "items": [
            {
                "phrase": "你好", 
                "meaning": "Xin chào (Nǐ hǎo)", 
                "guide": "Hai thanh 3 đi liền nhau! Phải biến điệu thanh đầu thành thanh 2: Đọc là 'Ní hảo', chứ không đọc là 'Nỉ hảo'!"
            },
            {
                "phrase": "谢谢", 
                "meaning": "Cảm ơn (Xiè xie)", 
                "guide": "Thanh 4 đi trước đọc hạ giọng mạnh và dứt khoát 'Xiè', từ sau đọc thanh nhẹ lướt 'xie'. Đừng có đọc bằng bằng!"
            },
            {
                "phrase": "再见", 
                "meaning": "Tạm biệt (Zài jiàn)", 
                "guide": "Cả 2 từ đều là thanh 4! Nhấn giọng từ trên cao xuống dứt khoát: 'Zài jiàn'! Không được đọc kéo dài như rên!"
            }
        ]}
    ],
    "Tiếng Nhật": [
        {"title": "Level 1: Chào hỏi", "items": [
            {
                "phrase": "こんにちは", 
                "meaning": "Xin chào ban ngày (Konnichiwa)", 
                "guide": "Âm 'n' đứng giữa phải ngắt nhẹ một nhịp. Âm 'ha' ở cuối đóng vai trò trợ từ đọc thành 'wa'. Đọc dứt khoát!"
            },
            {
                "phrase": "ありがとう", 
                "meaning": "Cảm ơn (Arigatou)", 
                "guide": "Âm 'r' trong tiếng Nhật uốn lưỡi nhẹ giống âm 'L' pha 'Đ'. 'u' ở cuối làm trường âm cho 'to', đọc kéo dài 'Arigatō'."
            }
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
    "voice_rate": 0.9,
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
# 4. LOGIC XỬ LÝ AI - TÍNH CÁCH GIA TRƯỜNG & HƯỚNG DẪN BẢN NGỮ
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
            return "Đã xong bài căn bản! Giờ bước vào hội thoại tự do, nói sai câu nào tao chỉnh câu đấy!"
        return f"Mới xong được Level {st.session_state.level-1} thôi, đừng có mà tưởng bở! Tiếp tục Level {st.session_state.level} ngay!"
    return "Xong từ này rồi. Học tiếp từ tiếp theo!"

def set_target_language(lang_name):
    st.session_state.target_lang = lang_name
    st.session_state.onboard_stage = "in_lesson"
    curr = current_item()
    target_tts = LANGUAGES[lang_name]["tts"]
    
    display_text = f"Đã chọn {lang_name}! Học hành cho đàng hoàng vào!\nTừ đầu tiên: '{curr['phrase']}' ({curr['meaning']}).\n📌 LƯU Ý PHÁT ÂM: {curr['guide']}\n👉 Đọc ngay cho tao nghe!"
    
    tts_seq = [
        {"lang": "vi-VN", "text": f"Đã chọn {lang_name}! Học hành cho đàng hoàng vào! Từ đầu tiên: "},
        {"lang": target_tts, "text": curr['phrase']},
        {"lang": "vi-VN", "text": f" nghĩa là {curr['meaning']}. Lưu ý phát âm: {curr['guide']}. Đọc ngay cho tao nghe!"}
    ]
    
    st.session_state.chat_log.append({"role": "assistant", "text": display_text})
    st.session_state.last_speech_seq = tts_seq
    st.session_state.is_speaking = True
    save_data()

def process_user_input(user_text):
    if not user_text.strip():
        return
    
    st.session_state.chat_log.append({"role": "user", "text": user_text})
    stage = st.session_state.onboard_stage
    display_text = ""
    tts_seq = []

    if stage == "ask_language":
        detected = detect_language(user_text)
        if detected:
            set_target_language(detected)
            return
        else:
            display_text = "Nói cái gì đấy?! Chọn đúng tên ngôn ngữ xem nào! Bấm nút bên dưới cho nhanh!"
            tts_seq = [{"lang": "vi-VN", "text": display_text}]

    elif stage == "in_lesson":
        target_tts = LANGUAGES[st.session_state.target_lang]["tts"]
        
        if st.session_state.mode == "lesson":
            curr = current_item()
            target = curr["phrase"]
            
            # So sánh chuẩn xác phát âm
            if normalize_text(user_text) == normalize_text(target):
                st.session_state.words_learned.append(target)
                adv_msg = advance_lesson()
                next_curr = current_item()
                
                display_text = f"😤 Hừ, tạm chấp nhận được! Cuối cùng cái đầu cũng chịu hoạt động rồi đấy.\n{adv_msg}\nTừ tiếp theo: '{next_curr['phrase']}' ({next_curr['meaning']}).\n📌 LƯU Ý: {next_curr['guide']}\nĐọc lại ngay!"
                
                tts_seq = [
                    {"lang": "vi-VN", "text": f"Hừ, tạm chấp nhận được! Cuối cùng cái đầu cũng chịu hoạt động rồi đấy. {adv_msg} Từ tiếp theo: "},
                    {"lang": target_tts, "text": next_curr['phrase']},
                    {"lang": "vi-VN", "text": f" nghĩa là {next_curr['meaning']}. Lưu ý: {next_curr['guide']}. Đọc lại ngay!"}
                ]
            else:
                # CHỬI GIA TRƯỜNG KHI NÓI SAI
                display_text = f"🤬 Đọc cái kiểu gì đấy?! Ngu quá, nhìn đây này!\nTừ đúng phải là '{target}' ({curr['meaning']}).\nMày vừa đọc thành '{user_text}' là sai hoàn toàn!\n📌 NHÌN LẠI CÁCH ĐỌC: {curr['guide']}\nNghe lại rồi đọc lại ngay cho tao!"
                
                tts_seq = [
                    {"lang": "vi-VN", "text": f"Đọc cái kiểu gì đấy?! Ngu quá, nhìn đây này! Từ người ta là "},
                    {"lang": target_tts, "text": target},
                    {"lang": "vi-VN", "text": f" nghĩa là {curr['meaning']}. Mày vừa đọc sai rồi. Nghe kĩ lưu ý này: {curr['guide']}. Nghe lại rồi đọc lại ngay!"}
                ]
        else:
            display_text = f"Nói chưa được tự nhiên đâu! Nói lại câu khác xem nào!"
            tts_seq = [{"lang": "vi-VN", "text": display_text}]

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
        border-radius: 20px; padding: 16px 20px; margin: 10px auto 15px auto;
        max-width: 95%; text-align: left; font-size: 16px; line-height: 1.6; color: #F1F5F9;
        box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.3);
    }
    .speech-bubble:after {
        content: ''; position: absolute; bottom: -12px; left: 50%;
        transform: translateX(-50%); border-width: 12px 12px 0;
        border-style: solid; border-color: #1E293B transparent; display: block; width: 0;
    }
    .status-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid #475569;
        border-radius: 12px; padding: 10px 16px; display: flex;
        justify-content: space-around; margin-bottom: 15px; font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Lịch sử ban đầu
if not st.session_state.chat_log:
    welcome_msg = "Mày muốn học cái tiếng gì?! Bấm chọn bên dưới nhanh lên rồi tao dạy!"
    st.session_state.chat_log.append({"role": "assistant", "text": welcome_msg})
    st.session_state.last_speech_seq = [{"lang": "vi-VN", "text": welcome_msg}]

st.markdown(f"""
<div class="status-card">
    <span>🔥 Streak: <b>{st.session_state.streak} ngày</b></span>
    <span>🌐 Ngôn ngữ: <b>{st.session_state.target_lang or 'Chưa chọn'}</b></span>
    <span>📊 Cấp độ: <b>Level {st.session_state.level}</b></span>
</div>
""", unsafe_allow_html=True)

assistant_msgs = [m["text"] for m in st.session_state.chat_log if m.get("role") == "assistant"]
latest_ai_msg = assistant_msgs[-1] if assistant_msgs else ""
st.markdown(f'<div class="speech-bubble">{latest_ai_msg.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. NHÂN VẬT AI HOẠT HÌNH SVG (BIỂU CẢM NGẦU / TỔNG TÀI GIA TRƯỜNG)
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
    .floating-bear {{ animation: float 3s ease-in-out infinite; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
</style></head><body>
    <svg class="floating-bear" width="180" height="180" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Tai -->
        <circle cx="50" cy="50" r="25" fill="#475569"/> <circle cx="50" cy="50" r="14" fill="#94A3B8"/>
        <circle cx="150" cy="50" r="25" fill="#475569"/> <circle cx="150" cy="50" r="14" fill="#94A3B8"/>
        <!-- Đầu -->
        <circle cx="100" cy="100" r="70" fill="#64748B"/>
        <!-- Lông mày gia trưởng nghiêm nghị -->
        <path d="M60 68 L85 78" stroke="#0F172A" stroke-width="5" stroke-linecap="round"/>
        <path d="M140 68 L115 78" stroke="#0F172A" stroke-width="5" stroke-linecap="round"/>
        <!-- Mắt sắc lẹm -->
        <ellipse cx="75" cy="88" rx="6" ry="8" fill="#0F172A"/>
        <ellipse cx="125" cy="88" rx="6" ry="8" fill="#0F172A"/>
        <!-- Mũi -->
        <ellipse cx="100" cy="108" rx="16" ry="10" fill="#E2E8F0"/>
        <polygon points="100,102 94,108 106,108" fill="#0F172A"/>
        {mouth_svg}
    </svg>
</body></html>
"""
components.html(svg_bear_html, height=190)

# ==============================================================================
# 7. ĐIỀU KHIỂN ÂM THANH JAVASCRIPT (SONG NGỮ & AUTO SUBMIT)
# ==============================================================================
if st.session_state.onboard_stage == "ask_language":
    stt_lang = "vi-VN"
else:
    stt_lang = LANGUAGES.get(st.session_state.target_lang, {}).get("stt", "en-US")

tts_sequence_json = json.dumps(st.session_state.last_speech_seq)

if st.session_state.is_speaking:
    st.session_state.is_speaking = False

components.html(f"""
    <div style="display:flex; gap:10px; font-family:sans-serif;">
        <button id="speakBtn" style="flex:1; padding:12px; background:#DC2626; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🔊 Bắt thầy đọc lại
        </button>
        <button id="micBtn" style="flex:1; padding:12px; background:#0284C7; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
            🎤 Đọc phát âm ({stt_lang})
        </button>
    </div>
    <p id="status" style="color:#94A3B8; font-size:12px; text-align:center; margin-top:6px; margin-bottom:0;"></p>

    <script>
        const speakBtn = document.getElementById('speakBtn');
        const micBtn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        
        const sequence = {tts_sequence_json};
        const sttLang = {json.dumps(stt_lang)};
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
            let voice = voices.find(v => v.lang.includes(part.lang) && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Online")));
            if (!voice) voice = voices.find(v => v.lang.includes(part.lang));
            if (!voice) voice = voices.find(v => v.lang.startsWith(part.lang.split('-')[0]));
            if (voice) msg.voice = voice;

            msg.onstart = () => {{ status.innerText = "🔊 Đang giảng..."; }};
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
        
        window.speechSynthesis.onvoiceschanged = () => {{
            if(currentVoiceIdx === 0) startSpeaking();
        }};
        setTimeout(startSpeaking, 300);

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = sttLang;
            recognition.interimResults = false;
            
            micBtn.onclick = () => {{
                try {{
                    recognition.start();
                    status.innerText = "🎤 Đang nghe... Nói xong tự nộp!";
                    micBtn.style.background = "#DC2626";
                }} catch (e) {{
                    recognition.stop();
                }}
            }};
            
            recognition.onresult = (event) => {{
                const text = event.results[0][0].transcript;
                status.innerText = "Nói: " + text + " -> Đang kiểm tra...";
                micBtn.style.background = "#0284C7";
                
                const doc = window.parent.document;
                const inputField = doc.querySelector('input[type="text"]');
                
                if (inputField) {{
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(inputField, text);
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));

                    setTimeout(() => {{
                        const submitBtn = doc.querySelector('button[kind="formSubmit"]');
                        if (submitBtn) {{
                            submitBtn.click();
                        }}
                    }}, 400);
                }}
            }};
            
            recognition.onerror = () => {{
                status.innerText = "Chưa nghe thấy gì cả! Nói to lên!";
                micBtn.style.background = "#0284C7";
            }};
        }}
    </script>
""", height=90)

# ==============================================================================
# 8. KHU VỰC CHỌN NGÔN NGỮ & NHẬP LIỆU
# ==============================================================================
if st.session_state.onboard_stage == "ask_language":
    st.write("👉 **Chọn ngôn ngữ để thầy nắn phát âm:**")
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
        user_input = st.text_input("Nhập câu trả lời hoặc dùng Micro...", placeholder="Đọc từ vựng vào Micro...", key="user_text_input")
        submit_button = st.form_submit_button("Nộp bài 🚀", use_container_width=True)

    if submit_button and user_input:
        process_user_input(user_input)
        st.rerun()

# ==============================================================================
# 9. CÀI ĐẶT
# ==============================================================================
with st.expander("⚙️ Cài đặt hệ thống"):
    rate = st.slider("Tốc độ nói của thầy", 0.5, 1.5, st.session_state.voice_rate, 0.05)
    if st.button("Đổi ngôn ngữ"):
        st.session_state.onboard_stage = "ask_language"
        st.session_state.target_lang = ""
        save_data()
        st.rerun()
    if st.button("Lưu cài đặt"):
        st.session_state.voice_rate = rate
        save_data()
        st.success("Đã lưu!")
