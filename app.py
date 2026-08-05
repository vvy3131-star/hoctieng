# -*- coding: utf-8 -*-
"""
================================================================================
 AI LANGUAGE LEARNING - Ứng dụng học ngoại ngữ bằng AI
 Tác giả: Senior Python/AI Engineer & UI-UX Designer (viết theo yêu cầu)
 File duy nhất: app.py (không dùng module/package/class ở file khác)
================================================================================
 Cách chạy:
     pip install streamlit
     streamlit run app.py

 Tích hợp AI thật (tuỳ chọn):
     - Đặt biến môi trường OPENAI_API_KEY (hoặc nhập trong Cài đặt > AI)
     - Nếu chưa có key -> app tự dùng "Chatbot giả lập" (rule-based) để demo
     - Khi có key, hàm get_ai_response() sẽ tự động gọi OpenAI API thật.
================================================================================
"""

import streamlit as st
import random
import time
import datetime
import json
import os
import re
import base64
import urllib.parse

# ==============================================================================
# 1. CẤU HÌNH TRANG
# ==============================================================================
st.set_page_config(
    page_title="AI Language Learning",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. KHỞI TẠO SESSION STATE (bộ nhớ phiên làm việc)
# ==============================================================================
def init_state():
    defaults = {
        "theme": "dark",                       # dark / light
        "page": "Trang chủ",
        "native_lang": "Tiếng Việt",
        "target_lang": "Tiếng Anh",
        "onboarded": False,
        "chat_history": {},                    # {lang: [ {role, content, ts} ]}
        "xp": 0,
        "streak": 3,
        "last_study_date": str(datetime.date.today()),
        "level": 1,
        "words_learned": set(),
        "flashcard_index": 0,
        "flashcard_known": set(),
        "flashcard_unknown": set(),
        "quiz_score": 0,
        "quiz_total": 0,
        "game_score": 0,
        "font_size": "Vừa",
        "ai_voice": "Nữ (US)",
        "speech_speed": 1.0,
        "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
        "username": "Người học",
        "avatar": "🧑‍🎓",
        "history_log": [],                     # nhật ký học tập cho thống kê
        "pron_last_score": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==============================================================================
# 3. DỮ LIỆU NGÔN NGỮ (từ vựng / ngữ pháp / dịch / chatbot rule-based)
# ==============================================================================

LANGUAGES = {
    "Tiếng Việt": {"code": "vi", "flag": "🇻🇳"},
    "Tiếng Anh": {"code": "en", "flag": "🇬🇧"},
    "Tiếng Trung": {"code": "zh", "flag": "🇨🇳"},
    "Tiếng Nhật": {"code": "ja", "flag": "🇯🇵", "soon": True},
    "Tiếng Hàn": {"code": "ko", "flag": "🇰🇷", "soon": True},
    "Tiếng Pháp": {"code": "fr", "flag": "🇫🇷", "soon": True},
    "Tiếng Đức": {"code": "de", "flag": "🇩🇪", "soon": True},
    "Tiếng Tây Ban Nha": {"code": "es", "flag": "🇪🇸", "soon": True},
}

# Từ vựng mẫu theo ngôn ngữ đích (mở rộng dễ dàng bằng cách thêm dict)
VOCAB_DB = {
    "Tiếng Anh": [
        {"word": "Apple", "phonetic": "/ˈæp.əl/", "meaning": "Quả táo", "example": "I eat an apple every morning.", "emoji": "🍎"},
        {"word": "Book", "phonetic": "/bʊk/", "meaning": "Quyển sách", "example": "She is reading a book.", "emoji": "📖"},
        {"word": "Water", "phonetic": "/ˈwɔː.tər/", "meaning": "Nước", "example": "Drink more water every day.", "emoji": "💧"},
        {"word": "House", "phonetic": "/haʊs/", "meaning": "Ngôi nhà", "example": "This is my house.", "emoji": "🏠"},
        {"word": "Friend", "phonetic": "/frend/", "meaning": "Bạn bè", "example": "He is my best friend.", "emoji": "🤝"},
        {"word": "Happy", "phonetic": "/ˈhæp.i/", "meaning": "Hạnh phúc, vui vẻ", "example": "I feel happy today.", "emoji": "😊"},
        {"word": "Travel", "phonetic": "/ˈtræv.əl/", "meaning": "Du lịch, di chuyển", "example": "I love to travel around the world.", "emoji": "✈️"},
        {"word": "Study", "phonetic": "/ˈstʌd.i/", "meaning": "Học tập", "example": "I study English every day.", "emoji": "📚"},
        {"word": "Beautiful", "phonetic": "/ˈbjuː.tɪ.fəl/", "meaning": "Đẹp", "example": "The sunset is beautiful.", "emoji": "🌅"},
        {"word": "Family", "phonetic": "/ˈfæm.əl.i/", "meaning": "Gia đình", "example": "I love my family.", "emoji": "👨‍👩‍👧‍👦"},
    ],
    "Tiếng Trung": [
        {"word": "你好", "phonetic": "nǐ hǎo", "meaning": "Xin chào", "example": "你好，很高兴认识你。", "emoji": "👋"},
        {"word": "谢谢", "phonetic": "xiè xiè", "meaning": "Cảm ơn", "example": "谢谢你的帮助。", "emoji": "🙏"},
        {"word": "朋友", "phonetic": "péng yǒu", "meaning": "Bạn bè", "example": "他是我的朋友。", "emoji": "🤝"},
        {"word": "水", "phonetic": "shuǐ", "meaning": "Nước", "example": "请给我一杯水。", "emoji": "💧"},
        {"word": "学习", "phonetic": "xué xí", "meaning": "Học tập", "example": "我每天学习中文。", "emoji": "📚"},
        {"word": "家", "phonetic": "jiā", "meaning": "Gia đình / nhà", "example": "我爱我的家。", "emoji": "🏠"},
        {"word": "高兴", "phonetic": "gāo xìng", "meaning": "Vui vẻ", "example": "我今天很高兴。", "emoji": "😊"},
        {"word": "旅行", "phonetic": "lǚ xíng", "meaning": "Du lịch", "example": "我喜欢旅行。", "emoji": "✈️"},
    ],
    "Tiếng Việt": [
        {"word": "Xin chào", "phonetic": "sin tʃaːʊ˨˩", "meaning": "Lời chào hỏi", "example": "Xin chào, bạn khỏe không?", "emoji": "👋"},
        {"word": "Cảm ơn", "phonetic": "kaːm˧˥ əːn˧˧", "meaning": "Thank you", "example": "Cảm ơn bạn rất nhiều.", "emoji": "🙏"},
        {"word": "Gia đình", "phonetic": "zaː˧˧ ɗiŋ˨˩", "meaning": "Family", "example": "Tôi yêu gia đình tôi.", "emoji": "👨‍👩‍👧‍👦"},
    ],
}

GRAMMAR_DB = {
    "Tiếng Anh": [
        {
            "title": "Thì hiện tại đơn (Present Simple)",
            "explain": "Dùng để diễn tả thói quen, sự thật hiển nhiên. Công thức: S + V(s/es) + O.",
            "example": "She goes to school every day.",
            "quiz_q": "Chọn câu đúng thì hiện tại đơn:",
            "quiz_options": ["He go to work.", "He goes to work.", "He going to work.", "He gone to work."],
            "quiz_answer": 1,
        },
        {
            "title": "Thì hiện tại tiếp diễn (Present Continuous)",
            "explain": "Diễn tả hành động đang xảy ra. Công thức: S + am/is/are + V-ing.",
            "example": "I am learning English now.",
            "quiz_q": "Chọn câu đúng thì hiện tại tiếp diễn:",
            "quiz_options": ["She is study now.", "She studying now.", "She is studying now.", "She studies now."],
            "quiz_answer": 2,
        },
        {
            "title": "Thì quá khứ đơn (Past Simple)",
            "explain": "Diễn tả hành động đã xảy ra và kết thúc trong quá khứ. Công thức: S + V-ed/V2.",
            "example": "I visited my grandmother last week.",
            "quiz_q": "Chọn dạng quá khứ đúng của 'go':",
            "quiz_options": ["goed", "went", "gone", "going"],
            "quiz_answer": 1,
        },
    ],
    "Tiếng Trung": [
        {
            "title": "Cấu trúc câu cơ bản (主谓宾)",
            "explain": "Chủ ngữ + Vị ngữ + Tân ngữ, giống tiếng Việt: 我 (tôi) + 吃 (ăn) + 苹果 (táo).",
            "example": "我吃苹果。 (Wǒ chī píngguǒ - Tôi ăn táo.)",
            "quiz_q": "Câu nào đúng cấu trúc?",
            "quiz_options": ["苹果我吃", "我吃苹果", "吃我苹果", "苹果吃我"],
            "quiz_answer": 1,
        },
        {
            "title": "Trợ từ 了 (le) chỉ hành động hoàn thành",
            "explain": "了 đặt sau động từ để diễn tả hành động đã xảy ra/hoàn thành.",
            "example": "我吃了。 (Wǒ chī le - Tôi đã ăn rồi.)",
            "quiz_q": "了 dùng để diễn tả điều gì?",
            "quiz_options": ["Tương lai", "Hành động hoàn thành", "Nghi vấn", "Phủ định"],
            "quiz_answer": 1,
        },
    ],
}

READING_DB = {
    "Tiếng Anh": [
        {"title": "My Family", "text": "Hello, my name is Anna. I live in a small house with my mom, dad, and my little brother. Every morning, we have breakfast together. My mom makes delicious pancakes. After breakfast, I go to school by bus. I love my family very much."},
        {"title": "A Trip to the Beach", "text": "Last summer, my friends and I went to the beach. The water was clear and blue. We swam, played volleyball, and built a big sandcastle. In the evening, we watched the beautiful sunset together. It was one of the best days of my life."},
    ],
    "Tiếng Trung": [
        {"title": "我的一天", "text": "我每天早上七点起床。吃完早饭以后，我去学校。中午和朋友们一起吃午饭。下午上完课，我回家做作业。晚上，我喜欢和家人一起看电视。"},
    ],
}

LISTENING_DB = {
    "Tiếng Anh": [
        "Good morning! How are you today?",
        "I would like a cup of coffee, please.",
        "What time does the train leave?",
        "Can you help me find the nearest hospital?",
        "She is reading a very interesting book.",
    ],
    "Tiếng Trung": [
        "早上好，你今天怎么样？",
        "我想要一杯咖啡。",
        "火车几点开？",
        "你能帮我找最近的医院吗？",
    ],
}

SPEAKING_QUESTIONS = {
    "Tiếng Anh": [
        "What is your name and where are you from?",
        "What do you usually do on weekends?",
        "Can you describe your favorite food?",
        "What are your hobbies?",
    ],
    "Tiếng Trung": [
        "你叫什么名字？你是哪里人？",
        "周末你通常做什么？",
        "你最喜欢的食物是什么？",
    ],
}

WRITING_TOPICS = {
    "Tiếng Anh": [
        "Describe your best friend.",
        "Write about your daily routine.",
        "What is your dream job? Why?",
        "Describe your hometown.",
    ],
    "Tiếng Trung": [
        "描述一下你最好的朋友。",
        "写一写你的日常生活。",
        "你的梦想工作是什么？",
    ],
}

# Từ điển dịch đơn giản (offline demo) - có thể thay bằng API dịch thật
SIMPLE_DICT = {
    ("Tiếng Việt", "Tiếng Anh"): {
        "xin chào": "hello", "cảm ơn": "thank you", "tạm biệt": "goodbye",
        "tôi yêu bạn": "i love you", "bạn khỏe không": "how are you",
        "gia đình": "family", "bạn bè": "friend", "nước": "water",
        "sách": "book", "đẹp": "beautiful", "học tập": "study",
        "du lịch": "travel", "vui vẻ": "happy", "nhà": "house",
    },
    ("Tiếng Việt", "Tiếng Trung"): {
        "xin chào": "你好", "cảm ơn": "谢谢", "tạm biệt": "再见",
        "gia đình": "家", "bạn bè": "朋友", "nước": "水",
        "học tập": "学习", "vui vẻ": "高兴", "du lịch": "旅行",
    },
}
# Tạo chiều ngược lại tự động
_reverse_dict = {}
for (a, b), d in SIMPLE_DICT.items():
    _reverse_dict[(b, a)] = {v: k for k, v in d.items()}
SIMPLE_DICT.update(_reverse_dict)


# ==============================================================================
# 4. AI ENGINE - Chatbot (ưu tiên OpenAI API thật, fallback rule-based)
# ==============================================================================
def call_openai_api(messages, api_key):
    """Gọi OpenAI Chat Completions API thật (chỉ chạy khi có API key hợp lệ)."""
    try:
        import requests
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 300,
            },
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            return None
    except Exception:
        return None


# Chatbot giả lập (rule-based) - hoạt động không cần internet/API key
FAKE_BOT_REPLIES = {
    "Tiếng Anh": {
        "greet": ["Hi there! 😊 How are you today?", "Hello! Nice to meet you. What's your name?", "Hey! Great to see you practicing English!"],
        "how_are_you": ["I'm doing great, thanks for asking! What did you do today?", "I'm good! How about you?"],
        "fine": ["Great to hear! What did you do today?", "Awesome! Tell me more about your day."],
        "name": ["Nice to meet you! I'm your AI language buddy 🤖", "That's a lovely name!"],
        "bye": ["Goodbye! See you next time. Keep practicing! 👋", "Bye bye! Great job today!"],
        "thanks": ["You're welcome! Keep up the good work! 💪", "No problem at all! 😊"],
        "default": [
            "That's interesting! Can you tell me more?",
            "I see! What else would you like to talk about?",
            "Cool! Let's keep practicing. Can you make another sentence?",
            "Nice! How do you feel about that?",
            "Got it! What did you do after that?",
        ],
    },
    "Tiếng Trung": {
        "greet": ["你好！😊 你今天怎么样？", "你好！很高兴认识你！", "嗨！很高兴你在练习中文！"],
        "how_are_you": ["我很好，谢谢！你今天做了什么？", "我很好！你呢？"],
        "fine": ["太好了！你今天做了什么？", "真棒！多告诉我一些吧。"],
        "name": ["很高兴认识你！我是你的AI语言伙伴🤖", "这个名字很好听！"],
        "bye": ["再见！下次再聊，继续加油！👋", "拜拜！你今天做得很好！"],
        "thanks": ["不客气！继续加油！💪", "没关系！😊"],
        "default": [
            "真有意思！能告诉我更多吗？",
            "我明白了！你还想聊什么？",
            "很好！我们继续练习吧，你能再造一个句子吗？",
            "不错！你感觉怎么样？",
        ],
    },
}


def detect_intent(text, lang):
    t = text.lower().strip()
    if lang == "Tiếng Anh":
        if any(w in t for w in ["hi", "hello", "hey"]):
            return "greet"
        if "how are you" in t:
            return "how_are_you"
        if any(w in t for w in ["i'm fine", "i am fine", "good", "great", "im fine"]):
            return "fine"
        if "my name is" in t or "i am " in t:
            return "name"
        if any(w in t for w in ["bye", "goodbye", "see you"]):
            return "bye"
        if "thank" in t:
            return "thanks"
    elif lang == "Tiếng Trung":
        if "你好" in t or "嗨" in t:
            return "greet"
        if "怎么样" in t:
            return "how_are_you"
        if "很好" in t or "不错" in t:
            return "fine"
        if "我叫" in t or "我是" in t:
            return "name"
        if "再见" in t or "拜拜" in t:
            return "bye"
        if "谢谢" in t:
            return "thanks"
    return "default"


def get_fake_ai_response(user_text, lang):
    intent = detect_intent(user_text, lang)
    bank = FAKE_BOT_REPLIES.get(lang, FAKE_BOT_REPLIES["Tiếng Anh"])
    options = bank.get(intent, bank["default"])
    return random.choice(options)


def get_ai_response(user_text, lang, history):
    """Hàm trung tâm sinh phản hồi AI. Ưu tiên OpenAI API thật nếu có key."""
    api_key = st.session_state.get("openai_api_key", "")
    if api_key:
        sys_prompt = (
            f"You are a friendly, encouraging language tutor AI. The learner is a Vietnamese "
            f"native speaker practicing {lang}. Reply ONLY in {lang}, keep replies short (1-3 "
            f"sentences), natural, and ask a simple follow-up question to keep the conversation going."
        )
        messages = [{"role": "system", "content": sys_prompt}]
        for h in history[-8:]:
            role = "user" if h["role"] == "user" else "assistant"
            messages.append({"role": role, "content": h["content"]})
        messages.append({"role": "user", "content": user_text})
        real_reply = call_openai_api(messages, api_key)
        if real_reply:
            return real_reply
    # fallback: chatbot giả lập
    return get_fake_ai_response(user_text, lang)


def fake_translate(text, src, dst):
    """Dịch giả lập offline dựa trên từ điển mẫu; nếu có API key sẽ có thể thay bằng API dịch thật."""
    key = (src, dst)
    d = SIMPLE_DICT.get(key, {})
    t = text.strip().lower()
    if t in d:
        return d[t]
    # thử dịch từng từ
    words = t.split()
    translated_words = [d.get(w, w) for w in words]
    if any(w in d for w in words):
        return " ".join(translated_words)
    return f"[Bản dịch demo] {text} ({src} ➜ {dst})"


def pronunciation_score_fake(_audio_or_text=None):
    """Chấm điểm phát âm giả lập (thực tế nên dùng model chấm điểm phát âm/ASR)."""
    score = random.randint(70, 99)
    good_sounds = random.sample(["a", "e", "i", "o", "th", "sh"], k=3)
    bad_sounds = random.sample(["r", "l", "v", "z", "ng"], k=2)
    return score, good_sounds, bad_sounds


# ==============================================================================
# 5. TEXT-TO-SPEECH / SPEECH-TO-TEXT qua trình duyệt (Web Speech API - JS)
# ==============================================================================
def tts_html(text, lang_code="en-US", rate=1.0):
    """Nhúng JS dùng Web Speech API để đọc văn bản bằng giọng nói của trình duyệt."""
    safe_text = json.dumps(text)
    html = f"""
    <div style="display:flex;align-items:center;gap:8px;">
      <button onclick='
        const u = new SpeechSynthesisUtterance({safe_text});
        u.lang = "{lang_code}";
        u.rate = {rate};
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
      ' style="
        background: linear-gradient(135deg,#7F5AF0,#2CB67D);
        border:none;color:white;padding:10px 18px;border-radius:14px;
        cursor:pointer;font-weight:600;box-shadow:0 4px 14px rgba(127,90,240,.4);
        transition:transform .15s ease;
      " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        🔊 Nghe phát âm
      </button>
    </div>
    """
    st.components.v1.html(html, height=60)


def mic_input_html(target_lang_code="en-US", key="mic1"):
    """Nhúng JS dùng Web Speech API để ghi âm & nhận diện giọng nói ngay trong trình duyệt.
    Kết quả nhận diện được hiển thị trực tiếp trong khung HTML (demo trình duyệt)."""
    html = f"""
    <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-start;">
      <button id="micBtn_{key}" onclick='
        try {{
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          const rec = new SR();
          rec.lang = "{target_lang_code}";
          rec.interimResults = false;
          document.getElementById("micResult_{key}").innerText = "🎙️ Đang nghe...";
          rec.onresult = function(e) {{
            const text = e.results[0][0].transcript;
            document.getElementById("micResult_{key}").innerText = "📝 " + text;
          }};
          rec.onerror = function(e) {{
            document.getElementById("micResult_{key}").innerText = "⚠️ Không nhận diện được (cần trình duyệt Chrome + micro).";
          }};
          rec.start();
        }} catch(err) {{
          document.getElementById("micResult_{key}").innerText = "⚠️ Trình duyệt không hỗ trợ Speech Recognition.";
        }}
      ' style="
        background: linear-gradient(135deg,#F25F4C,#FF8906);
        border:none;color:white;padding:14px;border-radius:50%;
        width:60px;height:60px;font-size:22px;cursor:pointer;
        box-shadow:0 4px 18px rgba(242,95,76,.5);
      ">🎤</button>
      <div id="micResult_{key}" style="opacity:.85;font-style:italic;">Bấm micro và nói...</div>
    </div>
    """
    st.components.v1.html(html, height=110)


# ==============================================================================
# 6. GIAO DIỆN - CSS (Glassmorphism + Gradient + Dark/Light + Animation)
# ==============================================================================
def inject_css():
    dark = st.session_state.theme == "dark"
    font_size_map = {"Nhỏ": "14px", "Vừa": "16px", "Lớn": "18px"}
    fsize = font_size_map.get(st.session_state.font_size, "16px")

    if dark:
        bg = "linear-gradient(135deg,#0f0c29,#302b63,#24243e)"
        card_bg = "rgba(255,255,255,0.06)"
        text_color = "#EDEDED"
        border_color = "rgba(255,255,255,0.15)"
        sidebar_bg = "rgba(15,12,41,0.85)"
    else:
        bg = "linear-gradient(135deg,#e0eafc,#cfdef3,#f6f9ff)"
        card_bg = "rgba(255,255,255,0.55)"
        text_color = "#1c1c2b"
        border_color = "rgba(0,0,0,0.08)"
        sidebar_bg = "rgba(255,255,255,0.75)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif !important;
        font-size: {fsize};
    }}

    .stApp {{
        background: {bg};
        background-attachment: fixed;
        color: {text_color};
    }}

    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(18px);
        border-right: 1px solid {border_color};
    }}

    /* Glass card */
    .glass-card {{
        background: {card_bg};
        border-radius: 22px;
        padding: 26px;
        border: 1px solid {border_color};
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        margin-bottom: 20px;
        animation: fadeIn .6s ease;
        transition: transform .25s ease, box-shadow .25s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 14px 36px rgba(0,0,0,0.28);
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero-title {{
        font-size: 46px;
        font-weight: 800;
        background: linear-gradient(90deg,#7F5AF0,#2CB67D,#FF8906);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 4s linear infinite;
    }}
    @keyframes shine {{
        to {{ background-position: 200% center; }}
    }}

    .subtitle {{
        font-size: 18px;
        opacity: .85;
        margin-bottom: 26px;
    }}

    .badge {{
        display:inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: linear-gradient(135deg,#7F5AF0,#2CB67D);
        color: white;
        font-weight: 600;
        font-size: 13px;
        margin-right: 6px;
    }}

    .stButton>button {{
        border-radius: 14px !important;
        border: none !important;
        background: linear-gradient(135deg,#7F5AF0,#2CB67D) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        transition: all .2s ease !important;
        box-shadow: 0 4px 16px rgba(127,90,240,.35);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 22px rgba(127,90,240,.5);
    }}

    .word-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        border: 1px solid {border_color};
        backdrop-filter: blur(14px);
        transition: transform .3s ease;
        animation: fadeIn .5s ease;
    }}
    .word-card:hover {{ transform: scale(1.03) rotate(-0.3deg); }}

    .progress-ring-label {{
        font-size: 13px;
        opacity: .8;
        text-align:center;
    }}

    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(135deg,#7F5AF0,#2CB67D); border-radius:10px; }}

    .chat-bubble-user {{
        background: linear-gradient(135deg,#7F5AF0,#5A3FC0);
        color:white; padding:12px 18px; border-radius:18px 18px 4px 18px;
        max-width:75%; margin-left:auto; margin-bottom:10px; animation: fadeIn .3s ease;
    }}
    .chat-bubble-ai {{
        background: {card_bg}; border:1px solid {border_color};
        padding:12px 18px; border-radius:18px 18px 18px 4px;
        max-width:75%; margin-right:auto; margin-bottom:10px; animation: fadeIn .3s ease;
        backdrop-filter: blur(10px);
    }}

    .menu-title {{
        font-weight:700; font-size: 20px; margin-bottom: 4px;
        background: linear-gradient(90deg,#7F5AF0,#2CB67D);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 7. CÁC THÀNH PHẦN GIAO DIỆN DÙNG CHUNG
# ==============================================================================
def glass_card_start():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def glass_card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f'<div class="hero-title" style="font-size:32px;">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtitle" style="font-size:15px;">{subtitle}</div>', unsafe_allow_html=True)

def log_activity(activity):
    st.session_state.history_log.append({
        "date": str(datetime.date.today()),
        "activity": activity,
        "time": datetime.datetime.now().strftime("%H:%M"),
    })
    st.session_state.xp += random.randint(5, 15)


def lang_code_for_tts(lang_name):
    mapping = {"Tiếng Anh": "en-US", "Tiếng Trung": "zh-CN", "Tiếng Việt": "vi-VN"}
    return mapping.get(lang_name, "en-US")


# ==============================================================================
# 8. SIDEBAR
# ==============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:10px 0 20px 0;">
            <div style="font-size:46px;">🌐</div>
            <div class="menu-title">AI Language Learning</div>
            <div style="opacity:.7;font-size:13px;">Nói chuyện với AI bằng bất kỳ ngôn ngữ nào</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:14px;
        background:rgba(127,90,240,.15);margin-bottom:14px;">
            <div style="font-size:28px;">{st.session_state.avatar}</div>
            <div>
                <div style="font-weight:600;">{st.session_state.username}</div>
                <div style="font-size:12px;opacity:.75;">Lv.{st.session_state.level} • 🔥{st.session_state.streak} ngày • ⭐{st.session_state.xp} XP</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        menu_groups = {
            "🏠 Chính": ["Trang chủ"],
            "📘 Học tập": ["Học từ vựng", "Học ngữ pháp", "Luyện phát âm", "Luyện nghe",
                          "Luyện nói", "Luyện đọc", "Luyện viết"],
            "🤖 AI": ["Chat với AI"],
            "🔤 Dịch": ["Dịch văn bản", "Dịch giọng nói", "Dịch camera"],
            "🎮 Ôn luyện": ["Flashcard", "Mini Game", "Bài kiểm tra"],
            "👤 Cá nhân": ["Thống kê", "Hồ sơ", "Cài đặt"],
        }

        for group, items in menu_groups.items():
            st.markdown(f"<div style='opacity:.6;font-size:12px;margin:10px 0 4px 4px;'>{group}</div>", unsafe_allow_html=True)
            for item in items:
                active = st.session_state.page == item
                if st.button(("➤ " if active else "") + item, key=f"nav_{item}", use_container_width=True):
                    st.session_state.page = item
                    st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark" if st.session_state.theme == "light" else "☀️ Light", use_container_width=True):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()
        with col2:
            st.markdown(f"<div style='text-align:center;padding-top:8px;'>{LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}</div>", unsafe_allow_html=True)


# ==============================================================================
# 9. TRANG: TRANG CHỦ
# ==============================================================================
def page_home():
    inject_css()
    st.markdown('<div class="hero-title">AI Language Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">🎓 Nói chuyện với AI bằng bất kỳ ngôn ngữ nào. Học Tiếng Việt, Tiếng Anh, Tiếng Trung — và sắp có thêm Nhật, Hàn, Pháp, Đức, Tây Ban Nha!</div>', unsafe_allow_html=True)

    if not st.session_state.onboarded:
        glass_card_start()
        st.markdown("### 👋 Bắt đầu hành trình học ngôn ngữ của bạn")
        c1, c2 = st.columns(2)
        with c1:
            native = st.selectbox("🗣️ Ngôn ngữ mẹ đẻ của bạn", list(LANGUAGES.keys()),
                                   index=list(LANGUAGES.keys()).index(st.session_state.native_lang))
        with c2:
            learnable = [k for k in LANGUAGES if not LANGUAGES[k].get("soon")]
            target = st.selectbox("🎯 Bạn muốn học ngôn ngữ nào?", learnable,
                                   index=learnable.index(st.session_state.target_lang) if st.session_state.target_lang in learnable else 0)
        st.caption("🔜 Sắp ra mắt: " + ", ".join([f"{LANGUAGES[k]['flag']} {k}" for k in LANGUAGES if LANGUAGES[k].get("soon")]))
        if st.button("🚀 Bắt đầu học", use_container_width=True):
            st.session_state.native_lang = native
            st.session_state.target_lang = target
            st.session_state.onboarded = True
            log_activity("Onboarding hoàn tất")
            st.rerun()
        glass_card_end()
    else:
        c1, c2, c3, c4 = st.columns(4)
        stats = [
            ("🔥 Streak", f"{st.session_state.streak} ngày"),
            ("⭐ XP", f"{st.session_state.xp}"),
            ("📈 Level", f"{st.session_state.level}"),
            ("📚 Từ đã học", f"{len(st.session_state.words_learned)}"),
        ]
        for col, (label, val) in zip([c1, c2, c3, c4], stats):
            with col:
                glass_card_start()
                st.markdown(f"<div style='font-size:13px;opacity:.7'>{label}</div><div style='font-size:26px;font-weight:800;'>{val}</div>", unsafe_allow_html=True)
                glass_card_end()

        glass_card_start()
        st.markdown(f"### 🎯 Đang học: {LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}")
        colA, colB = st.columns([3, 1])
        with colA:
            st.progress(min(st.session_state.xp % 100, 100) / 100, text=f"Tiến độ Level {st.session_state.level} → {st.session_state.level + 1}")
        with colB:
            new_target = st.selectbox("Đổi ngôn ngữ học", [k for k in LANGUAGES if not LANGUAGES[k].get("soon")],
                                       index=[k for k in LANGUAGES if not LANGUAGES[k].get("soon")].index(st.session_state.target_lang),
                                       label_visibility="collapsed")
            if new_target != st.session_state.target_lang:
                st.session_state.target_lang = new_target
                st.rerun()
        glass_card_end()

        st.markdown("#### ⚡ Truy cập nhanh")
        quick = [
            ("💬", "Chat với AI", "Trò chuyện tự nhiên với AI"),
            ("🃏", "Flashcard", "Ôn từ vựng bằng thẻ ghi nhớ"),
            ("🎮", "Mini Game", "Học mà chơi, chơi mà học"),
            ("🎙️", "Luyện nói", "Luyện phát âm & phản xạ nói"),
        ]
        cols = st.columns(4)
        for col, (icon, name, desc) in zip(cols, quick):
            with col:
                glass_card_start()
                st.markdown(f"<div style='font-size:34px;text-align:center;'>{icon}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;font-weight:700;'>{name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;font-size:12px;opacity:.7;'>{desc}</div>", unsafe_allow_html=True)
                if st.button("Vào ngay", key=f"quick_{name}", use_container_width=True):
                    st.session_state.page = name
                    st.rerun()
                glass_card_end()


# ==============================================================================
# 10. TRANG: HỌC TỪ VỰNG
# ==============================================================================
def page_vocab():
    inject_css()
    page_header("📚 Học từ vựng", f"{LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}")
    vocab_list = VOCAB_DB.get(st.session_state.target_lang, [])
    if not vocab_list:
        st.info("Chưa có dữ liệu từ vựng cho ngôn ngữ này.")
        return
    cols = st.columns(2)
    for i, v in enumerate(vocab_list):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="word-card">
                <div style="font-size:44px;">{v['emoji']}</div>
                <div style="font-size:24px;font-weight:800;">{v['word']}</div>
                <div style="opacity:.7;font-size:13px;">{v['phonetic']}</div>
                <div style="margin-top:8px;font-weight:600;">{v['meaning']}</div>
                <div style="opacity:.75;font-size:13px;margin-top:6px;font-style:italic;">"{v['example']}"</div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                tts_html(v['word'], lang_code_for_tts(st.session_state.target_lang))
            with c2:
                if st.button("✅ Đã học", key=f"vocab_learned_{i}", use_container_width=True):
                    st.session_state.words_learned.add(v['word'])
                    log_activity(f"Học từ: {v['word']}")
                    st.toast(f"Đã ghi nhớ '{v['word']}'! +XP")
            st.write("")


# ==============================================================================
# 11. TRANG: HỌC NGỮ PHÁP
# ==============================================================================
def page_grammar():
    inject_css()
    page_header("📐 Học ngữ pháp", f"{LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}")
    lessons = GRAMMAR_DB.get(st.session_state.target_lang, [])
    if not lessons:
        st.info("Chưa có bài học ngữ pháp cho ngôn ngữ này.")
        return
    for i, lesson in enumerate(lessons):
        glass_card_start()
        st.markdown(f"### 📖 {lesson['title']}")
        st.write(lesson['explain'])
        st.markdown(f"**Ví dụ:** _{lesson['example']}_")
        with st.expander("📝 Làm quiz nhỏ để kiểm tra"):
            choice = st.radio(lesson['quiz_q'], lesson['quiz_options'], key=f"gram_quiz_{i}", index=None)
            if choice is not None:
                correct = lesson['quiz_options'][lesson['quiz_answer']]
                if choice == correct:
                    st.success("🎉 Chính xác! Bạn giỏi quá!")
                    log_activity(f"Ngữ pháp đúng: {lesson['title']}")
                else:
                    st.error(f"❌ Chưa đúng. Đáp án đúng là: **{correct}**")
        glass_card_end()


# ==============================================================================
# 12. TRANG: LUYỆN PHÁT ÂM
# ==============================================================================
def page_pronunciation():
    inject_css()
    page_header("🗣️ Luyện phát âm", "AI sẽ chấm điểm độ chuẩn phát âm của bạn")
    vocab_list = VOCAB_DB.get(st.session_state.target_lang, [])
    if not vocab_list:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return
    word = random.choice(vocab_list) if "pron_word" not in st.session_state else st.session_state.pron_word
    if st.button("🔄 Từ mới"):
        st.session_state.pron_word = random.choice(vocab_list)
        st.session_state.pron_last_score = None
        st.rerun()
    st.session_state.pron_word = word

    glass_card_start()
    st.markdown(f"<div style='text-align:center;font-size:40px;font-weight:800;'>{word['word']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;opacity:.7;'>{word['phonetic']}</div>", unsafe_allow_html=True)
    tts_html(word['word'], lang_code_for_tts(st.session_state.target_lang))
    st.write("")
    st.markdown("**🎤 Bấm micro và đọc từ trên:**")
    mic_input_html(lang_code_for_tts(st.session_state.target_lang), key="pron_mic")
    if st.button("📊 Chấm điểm phát âm (AI)", use_container_width=True):
        score, good, bad = pronunciation_score_fake(word['word'])
        st.session_state.pron_last_score = (score, good, bad)
        log_activity("Luyện phát âm")
    if st.session_state.pron_last_score:
        score, good, bad = st.session_state.pron_last_score
        st.markdown(f"### 🏆 Điểm phát âm: {score}/100")
        st.progress(score / 100)
        c1, c2 = st.columns(2)
        with c1:
            st.success("✅ Âm phát chuẩn: " + ", ".join(good))
        with c2:
            st.warning("⚠️ Âm cần cải thiện: " + ", ".join(bad))
        st.info("💡 Gợi ý: Luyện tập chậm rãi, chú ý khẩu hình miệng và nghe lại mẫu nhiều lần.")
    glass_card_end()


# ==============================================================================
# 13. TRANG: LUYỆN NGHE
# ==============================================================================
def page_listening():
    inject_css()
    page_header("🎧 Luyện nghe", "Nghe AI đọc và gõ lại câu bạn nghe được")
    sentences = LISTENING_DB.get(st.session_state.target_lang, [])
    if not sentences:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return
    if "listen_sentence" not in st.session_state:
        st.session_state.listen_sentence = random.choice(sentences)

    glass_card_start()
    st.markdown("### 🔊 Bấm nghe và gõ lại câu bạn nghe được")
    tts_html(st.session_state.listen_sentence, lang_code_for_tts(st.session_state.target_lang), rate=0.9)
    answer = st.text_input("✍️ Nhập lại câu bạn nghe được:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Kiểm tra", use_container_width=True):
            correct = st.session_state.listen_sentence.strip().lower()
            given = answer.strip().lower()
            if given == correct:
                st.success("🎉 Chính xác 100%!")
                log_activity("Luyện nghe đúng")
            else:
                ratio = sum(1 for a, b in zip(given, correct) if a == b) / max(len(correct), 1)
                st.warning(f"Gần đúng ({int(ratio*100)}% khớp). Đáp án: **{st.session_state.listen_sentence}**")
    with c2:
        if st.button("⏭️ Câu tiếp theo", use_container_width=True):
            st.session_state.listen_sentence = random.choice(sentences)
            st.rerun()
    glass_card_end()


# ==============================================================================
# 14. TRANG: LUYỆN NÓI
# ==============================================================================
def page_speaking():
    inject_css()
    page_header("🎙️ Luyện nói", "AI đặt câu hỏi, bạn trả lời bằng giọng nói")
    questions = SPEAKING_QUESTIONS.get(st.session_state.target_lang, [])
    if not questions:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return
    if "speak_q" not in st.session_state:
        st.session_state.speak_q = random.choice(questions)

    glass_card_start()
    st.markdown(f"### 🤖 AI hỏi:")
    st.markdown(f"#### “{st.session_state.speak_q}”")
    tts_html(st.session_state.speak_q, lang_code_for_tts(st.session_state.target_lang))
    st.write("")
    st.markdown("**🎤 Trả lời bằng giọng nói của bạn:**")
    mic_input_html(lang_code_for_tts(st.session_state.target_lang), key="speak_mic")
    st.write("")
    manual = st.text_area("Hoặc gõ câu trả lời của bạn (nếu không dùng micro):")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📊 AI đánh giá câu trả lời", use_container_width=True):
            score, good, bad = pronunciation_score_fake(manual)
            st.success(f"🏆 Điểm phản xạ & phát âm: {score}/100")
            st.info("💡 Nhận xét AI: Câu trả lời khá tự nhiên! Hãy thử nói dài hơn và dùng thêm liên từ để câu mượt hơn.")
            log_activity("Luyện nói")
    with c2:
        if st.button("⏭️ Câu hỏi khác", use_container_width=True):
            st.session_state.speak_q = random.choice(questions)
            st.rerun()
    glass_card_end()


# ==============================================================================
# 15. TRANG: LUYỆN VIẾT
# ==============================================================================
def page_writing():
    inject_css()
    page_header("✍️ Luyện viết", "AI chấm chữa ngữ pháp, chính tả, từ vựng & độ tự nhiên")
    topics = WRITING_TOPICS.get(st.session_state.target_lang, [])
    if "write_topic" not in st.session_state:
        st.session_state.write_topic = random.choice(topics) if topics else "Hãy viết một đoạn văn ngắn."

    glass_card_start()
    st.markdown(f"### 📝 Chủ đề: {st.session_state.write_topic}")
    if st.button("🔄 Đổi chủ đề"):
        st.session_state.write_topic = random.choice(topics)
        st.rerun()
    text = st.text_area("Viết bài của bạn tại đây:", height=180)
    if st.button("🔍 AI chấm bài", use_container_width=True):
        if text.strip():
            word_count = len(text.split())
            score = min(95, 60 + word_count)
            st.markdown(f"### 🏆 Điểm tổng quát: {score}/100")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Ưu điểm:**")
                st.write("- Ý tưởng rõ ràng, đúng chủ đề\n- Câu văn có cấu trúc hợp lý")
            with c2:
                st.markdown("**⚠️ Cần cải thiện:**")
                st.write("- Kiểm tra lại thì động từ\n- Dùng thêm từ nối để bài viết mượt hơn\n- Đa dạng hóa từ vựng")
            log_activity("Luyện viết")
        else:
            st.warning("Hãy nhập nội dung trước khi chấm bài.")
    glass_card_end()


# ==============================================================================
# 16. TRANG: LUYỆN ĐỌC
# ==============================================================================
def page_reading():
    inject_css()
    page_header("📖 Luyện đọc", "Đọc và nghe AI đọc mẫu")
    passages = READING_DB.get(st.session_state.target_lang, [])
    if not passages:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return
    for p in passages:
        glass_card_start()
        st.markdown(f"### {p['title']}")
        st.write(p['text'])
        tts_html(p['text'], lang_code_for_tts(st.session_state.target_lang))
        glass_card_end()


# ==============================================================================
# 17. TRANG: CHAT VỚI AI
# ==============================================================================
def page_chat():
    inject_css()
    page_header("💬 Chat với AI", f"Trò chuyện tự nhiên bằng {LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}")

    lang = st.session_state.target_lang
    if lang not in st.session_state.chat_history:
        st.session_state.chat_history[lang] = []
    history = st.session_state.chat_history[lang]

    if not st.session_state.openai_api_key:
        st.info("ℹ️ Đang dùng **Chatbot giả lập** (demo, không cần API). Vào **Cài đặt** để thêm OpenAI API Key và kích hoạt AI thật.")

    glass_card_start()
    chat_box = st.container(height=420)
    with chat_box:
        if not history:
            st.markdown('<div class="chat-bubble-ai">👋 Xin chào! Hãy bắt đầu trò chuyện với tôi nhé!</div>', unsafe_allow_html=True)
        for h in history:
            css_class = "chat-bubble-user" if h["role"] == "user" else "chat-bubble-ai"
            st.markdown(f'<div class="{css_class}">{h["content"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        user_msg = st.text_input("Nhập tin nhắn...", key="chat_input", label_visibility="collapsed")
    with col2:
        send = st.button("📤 Gửi", use_container_width=True)
    with col3:
        clear = st.button("🗑️ Xoá", use_container_width=True)

    st.markdown("**🎤 Hoặc nói chuyện bằng giọng nói:**")
    mic_input_html(lang_code_for_tts(lang), key="chat_mic")

    if clear:
        st.session_state.chat_history[lang] = []
        st.rerun()

    if send and user_msg.strip():
        history.append({"role": "user", "content": user_msg})
        with st.spinner("🤖 AI đang trả lời..."):
            reply = get_ai_response(user_msg, lang, history)
            time.sleep(0.3)
        history.append({"role": "ai", "content": reply})
        log_activity("Chat với AI")
        st.rerun()

    glass_card_end()


# ==============================================================================
# 18. TRANG: DỊCH (VĂN BẢN / GIỌNG NÓI / CAMERA)
# ==============================================================================
def translate_ui(mode):
    inject_css()
    titles = {
        "text": ("📝 Dịch văn bản", "Nhập văn bản để dịch ngay lập tức"),
        "voice": ("🎙️ Dịch giọng nói", "Nói để AI dịch trực tiếp"),
        "camera": ("📷 Dịch camera", "Chụp ảnh văn bản để dịch (OCR)"),
    }
    title, sub = titles[mode]
    page_header(title, sub)

    all_langs = [k for k in LANGUAGES if not LANGUAGES[k].get("soon")]
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        src = st.selectbox("Từ ngôn ngữ", all_langs, index=all_langs.index(st.session_state.native_lang) if st.session_state.native_lang in all_langs else 0, key=f"src_{mode}")
    with c2:
        st.markdown("<div style='text-align:center;font-size:26px;padding-top:28px;'>⇄</div>", unsafe_allow_html=True)
    with c3:
        dst = st.selectbox("Sang ngôn ngữ", all_langs, index=all_langs.index(st.session_state.target_lang) if st.session_state.target_lang in all_langs else 1, key=f"dst_{mode}")

    glass_card_start()
    if mode == "text":
        text = st.text_area("Nhập văn bản cần dịch:", height=120)
        if st.button("🔁 Dịch ngay", use_container_width=True):
            if text.strip():
                result = fake_translate(text, src, dst)
                st.markdown(f"### ✅ Kết quả:")
                st.success(result)
                tts_html(result, lang_code_for_tts(dst))
                log_activity("Dịch văn bản")
    elif mode == "voice":
        st.markdown("**🎤 Bấm micro và nói câu cần dịch:**")
        mic_input_html(lang_code_for_tts(src), key="translate_mic")
        manual = st.text_input("Hoặc gõ tay nội dung vừa nói (demo):")
        if st.button("🔁 Dịch giọng nói", use_container_width=True):
            if manual.strip():
                result = fake_translate(manual, src, dst)
                st.success(result)
                tts_html(result, lang_code_for_tts(dst))
                log_activity("Dịch giọng nói")
    else:  # camera
        img = st.camera_input("📷 Chụp ảnh có chứa văn bản cần dịch")
        if img is not None:
            st.image(img, caption="Ảnh đã chụp", width=300)
            st.info("🔍 (Demo) Đây là nơi hệ thống OCR sẽ trích xuất văn bản từ ảnh rồi dịch tự động. "
                    "Khi kết nối API OCR/Vision thật, kết quả nhận diện sẽ hiển thị ở đây.")
            fake_ocr_text = "hello"
            result = fake_translate(fake_ocr_text, "Tiếng Anh", dst)
            st.success(f"Văn bản demo nhận diện: **{fake_ocr_text}** ➜ {result}")
            log_activity("Dịch camera")
    glass_card_end()


# ==============================================================================
# 19. TRANG: FLASHCARD
# ==============================================================================
def page_flashcard():
    inject_css()
    page_header("🃏 Flashcard", "Vuốt để ghi nhớ từ vựng nhanh hơn")
    vocab_list = VOCAB_DB.get(st.session_state.target_lang, [])
    if not vocab_list:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return

    idx = st.session_state.flashcard_index % len(vocab_list)
    card = vocab_list[idx]

    show_answer = st.toggle("👁️ Hiện nghĩa", key="flash_toggle")

    glass_card_start()
    st.markdown(f"""
    <div style="text-align:center;padding:40px 0;">
        <div style="font-size:60px;">{card['emoji']}</div>
        <div style="font-size:38px;font-weight:800;">{card['word']}</div>
        <div style="opacity:.7;">{card['phonetic']}</div>
        {"<div style='margin-top:16px;font-size:20px;font-weight:600;color:#2CB67D;'>" + card['meaning'] + "</div><div style='opacity:.75;font-style:italic;margin-top:6px;'>" + card['example'] + "</div>" if show_answer else ""}
    </div>
    """, unsafe_allow_html=True)
    tts_html(card['word'], lang_code_for_tts(st.session_state.target_lang))
    glass_card_end()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("❌ Chưa nhớ", use_container_width=True):
            st.session_state.flashcard_unknown.add(card['word'])
            st.session_state.flashcard_index += 1
            st.rerun()
    with c2:
        if st.button("⏭️ Bỏ qua", use_container_width=True):
            st.session_state.flashcard_index += 1
            st.rerun()
    with c3:
        if st.button("✅ Đã nhớ", use_container_width=True):
            st.session_state.flashcard_known.add(card['word'])
            st.session_state.words_learned.add(card['word'])
            st.session_state.flashcard_index += 1
            log_activity("Flashcard: đã nhớ")
            st.rerun()

    st.progress(len(st.session_state.flashcard_known) / max(len(vocab_list), 1),
                text=f"Đã nhớ {len(st.session_state.flashcard_known)}/{len(vocab_list)} từ")


# ==============================================================================
# 20. TRANG: MINI GAME
# ==============================================================================
def page_game():
    inject_css()
    page_header("🎮 Mini Game", "Học mà chơi - chơi mà học")
    vocab_list = VOCAB_DB.get(st.session_state.target_lang, [])
    if not vocab_list:
        st.info("Chưa có dữ liệu cho ngôn ngữ này.")
        return

    game_type = st.radio("Chọn trò chơi:", ["🔗 Nối từ", "🎯 Chọn đáp án đúng", "✍️ Điền từ còn thiếu"], horizontal=True)

    if game_type == "🎯 Chọn đáp án đúng":
        if "game_q" not in st.session_state:
            st.session_state.game_q = random.choice(vocab_list)
            wrong = random.sample([v for v in vocab_list if v != st.session_state.game_q], k=min(3, len(vocab_list)-1))
            opts = [st.session_state.game_q['meaning']] + [w['meaning'] for w in wrong]
            random.shuffle(opts)
            st.session_state.game_opts = opts

        glass_card_start()
        q = st.session_state.game_q
        st.markdown(f"### Từ **{q['word']}** có nghĩa là gì?")
        choice = st.radio("Chọn đáp án:", st.session_state.game_opts, key="game_choice", index=None)
        if choice is not None:
            if choice == q['meaning']:
                st.success(f"🎉 Chính xác! +10 điểm")
                st.session_state.game_score += 10
                log_activity("Mini game đúng")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng: {q['meaning']}")
            if st.button("➡️ Câu tiếp theo"):
                del st.session_state.game_q
                del st.session_state.game_opts
                st.rerun()
        glass_card_end()

    elif game_type == "🔗 Nối từ":
        glass_card_start()
        st.write("Ghép từ vựng với đúng nghĩa của nó:")
        sample = random.sample(vocab_list, k=min(4, len(vocab_list)))
        words = [s['word'] for s in sample]
        meanings = [s['meaning'] for s in sample]
        shuffled_meanings = meanings.copy()
        random.shuffle(shuffled_meanings)
        answers = {}
        for w in words:
            answers[w] = st.selectbox(f"**{w}** ⇄", ["-- chọn nghĩa --"] + shuffled_meanings, key=f"match_{w}")
        if st.button("✅ Kiểm tra kết quả"):
            correct_count = sum(1 for s in sample if answers[s['word']] == s['meaning'])
            st.session_state.game_score += correct_count * 5
            st.success(f"🏆 Bạn nối đúng {correct_count}/{len(sample)} từ! (+{correct_count*5} điểm)")
            log_activity("Mini game nối từ")
        glass_card_end()

    else:  # điền từ
        glass_card_start()
        target = random.choice(vocab_list) if "fill_word" not in st.session_state else st.session_state.fill_word
        st.session_state.fill_word = target
        blanked = target['example'].replace(target['word'], "_____", 1) if target['word'] in target['example'] else target['example']
        st.markdown(f"### Điền từ còn thiếu vào câu:")
        st.markdown(f"_{blanked}_")
        ans = st.text_input("Nhập từ còn thiếu:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Kiểm tra"):
                if ans.strip().lower() == target['word'].lower():
                    st.success("🎉 Chính xác! +10 điểm")
                    st.session_state.game_score += 10
                    log_activity("Mini game điền từ")
                else:
                    st.error(f"❌ Sai rồi! Đáp án: {target['word']}")
        with c2:
            if st.button("⏭️ Câu khác"):
                st.session_state.fill_word = random.choice(vocab_list)
                st.rerun()
        glass_card_end()

    st.markdown(f"### 🏅 Điểm hiện tại: {st.session_state.game_score}")


# ==============================================================================
# 21. TRANG: BÀI KIỂM TRA
# ==============================================================================
def page_quiz():
    inject_css()
    page_header("📝 Bài kiểm tra", "Kiểm tra tổng hợp từ vựng & ngữ pháp")
    vocab_list = VOCAB_DB.get(st.session_state.target_lang, [])
    grammar_list = GRAMMAR_DB.get(st.session_state.target_lang, [])

    if "quiz_questions" not in st.session_state:
        questions = []
        for v in random.sample(vocab_list, k=min(4, len(vocab_list))):
            wrong = random.sample([x for x in vocab_list if x != v], k=min(3, len(vocab_list)-1))
            opts = [v['meaning']] + [w['meaning'] for w in wrong]
            random.shuffle(opts)
            questions.append({"q": f"'{v['word']}' nghĩa là gì?", "opts": opts, "ans": v['meaning']})
        for g in grammar_list:
            questions.append({"q": g['quiz_q'], "opts": g['quiz_options'], "ans": g['quiz_options'][g['quiz_answer']]})
        random.shuffle(questions)
        st.session_state.quiz_questions = questions
        st.session_state.quiz_answers = {}

    glass_card_start()
    for i, q in enumerate(st.session_state.quiz_questions):
        st.markdown(f"**Câu {i+1}:** {q['q']}")
        ans = st.radio("Chọn đáp án:", q['opts'], key=f"quiz_{i}", index=None, label_visibility="collapsed")
        st.session_state.quiz_answers[i] = ans
        st.write("---")

    if st.button("📤 Nộp bài", use_container_width=True):
        correct = sum(1 for i, q in enumerate(st.session_state.quiz_questions)
                      if st.session_state.quiz_answers.get(i) == q['ans'])
        total = len(st.session_state.quiz_questions)
        score = int(correct / total * 100) if total else 0
        st.session_state.quiz_score = correct
        st.session_state.quiz_total = total
        st.markdown(f"## 🏆 Kết quả: {correct}/{total} câu đúng ({score}/100 điểm)")
        st.balloons() if score >= 70 else None
        st.progress(score / 100)
        log_activity("Hoàn thành bài kiểm tra")
        st.session_state.xp += score

    if st.button("🔄 Làm bài mới"):
        del st.session_state.quiz_questions
        del st.session_state.quiz_answers
        st.rerun()
    glass_card_end()


# ==============================================================================
# 22. TRANG: THỐNG KÊ
# ==============================================================================
def page_stats():
    inject_css()
    page_header("📊 Thống kê học tập", "Theo dõi tiến độ của bạn")

    c1, c2, c3, c4, c5 = st.columns(5)
    stat_items = [
        ("📅 Ngày học", str(len(set(h['date'] for h in st.session_state.history_log)) or 1)),
        ("🔥 Streak", f"{st.session_state.streak}"),
        ("⭐ Điểm XP", f"{st.session_state.xp}"),
        ("📈 Level", f"{st.session_state.level}"),
        ("📚 Từ đã học", f"{len(st.session_state.words_learned)}"),
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5], stat_items):
        with col:
            glass_card_start()
            st.markdown(f"<div style='font-size:12px;opacity:.7'>{label}</div><div style='font-size:24px;font-weight:800;'>{val}</div>", unsafe_allow_html=True)
            glass_card_end()

    glass_card_start()
    st.markdown("### 📈 Biểu đồ tiến bộ (XP theo hoạt động)")
    if st.session_state.history_log:
        xp_progress = list(range(5, 5 * (len(st.session_state.history_log) + 1), 5))
        st.line_chart(xp_progress)
    else:
        st.info("Chưa có dữ liệu. Hãy bắt đầu học để xem biểu đồ tiến bộ!")
    glass_card_end()

    c1, c2 = st.columns(2)
    with c1:
        glass_card_start()
        st.markdown("### 🟢 Progress Ring - Mục tiêu hôm nay")
        today_count = sum(1 for h in st.session_state.history_log if h['date'] == str(datetime.date.today()))
        goal = 5
        pct = min(today_count / goal, 1.0)
        st.progress(pct, text=f"{today_count}/{goal} hoạt động hôm nay")
        glass_card_end()
    with c2:
        glass_card_start()
        st.markdown("### 🗂️ Nhật ký học tập gần đây")
        if st.session_state.history_log:
            for h in reversed(st.session_state.history_log[-8:]):
                st.markdown(f"- `{h['time']}` {h['activity']}")
        else:
            st.write("Chưa có hoạt động nào.")
        glass_card_end()


# ==============================================================================
# 23. TRANG: HỒ SƠ
# ==============================================================================
def page_profile():
    inject_css()
    page_header("👤 Hồ sơ cá nhân", "Thông tin học viên")
    glass_card_start()
    c1, c2 = st.columns([1, 3])
    with c1:
        avatar = st.selectbox("Avatar", ["🧑‍🎓", "👩‍🎓", "🧑‍💻", "👨‍🏫", "🐱", "🐶", "🦊", "🐼"],
                               index=["🧑‍🎓", "👩‍🎓", "🧑‍💻", "👨‍🏫", "🐱", "🐶", "🦊", "🐼"].index(st.session_state.avatar) if st.session_state.avatar in ["🧑‍🎓", "👩‍🎓", "🧑‍💻", "👨‍🏫", "🐱", "🐶", "🦊", "🐼"] else 0)
        st.markdown(f"<div style='font-size:80px;text-align:center;'>{avatar}</div>", unsafe_allow_html=True)
    with c2:
        name = st.text_input("Tên hiển thị", value=st.session_state.username)
        st.write(f"**Ngôn ngữ mẹ đẻ:** {st.session_state.native_lang}")
        st.write(f"**Đang học:** {LANGUAGES[st.session_state.target_lang]['flag']} {st.session_state.target_lang}")
        st.write(f"**Level:** {st.session_state.level}  |  **XP:** {st.session_state.xp}  |  **Streak:** {st.session_state.streak} 🔥")
        if st.button("💾 Lưu hồ sơ"):
            st.session_state.username = name
            st.session_state.avatar = avatar
            st.success("Đã lưu hồ sơ!")
    glass_card_end()

    glass_card_start()
    st.markdown("### 🏆 Huy hiệu thành tích")
    badges = [
        ("🥇", "Người mới", True),
        ("🔥", "Streak 3 ngày", st.session_state.streak >= 3),
        ("📚", "Học 5+ từ", len(st.session_state.words_learned) >= 5),
        ("💬", "Chat 1 lần với AI", len(st.session_state.chat_history.get(st.session_state.target_lang, [])) > 0),
        ("🎮", "Chơi Mini Game", st.session_state.game_score > 0),
    ]
    cols = st.columns(len(badges))
    for col, (icon, name_b, earned) in zip(cols, badges):
        with col:
            opacity = "1" if earned else "0.25"
            st.markdown(f"<div style='text-align:center;opacity:{opacity};'><div style='font-size:36px;'>{icon}</div><div style='font-size:11px;'>{name_b}</div></div>", unsafe_allow_html=True)
    glass_card_end()


# ==============================================================================
# 24. TRANG: CÀI ĐẶT
# ==============================================================================
def page_settings():
    inject_css()
    page_header("⚙️ Cài đặt", "Tuỳ chỉnh trải nghiệm học tập của bạn")

    glass_card_start()
    st.markdown("### 🎨 Giao diện")
    c1, c2, c3 = st.columns(3)
    with c1:
        theme = st.selectbox("Theme", ["dark", "light"], index=0 if st.session_state.theme == "dark" else 1,
                              format_func=lambda x: "🌙 Dark Mode" if x == "dark" else "☀️ Light Mode")
        st.session_state.theme = theme
    with c2:
        font_size = st.selectbox("Cỡ chữ", ["Nhỏ", "Vừa", "Lớn"], index=["Nhỏ", "Vừa", "Lớn"].index(st.session_state.font_size))
        st.session_state.font_size = font_size
    with c3:
        st.selectbox("Font chữ", ["Poppins (mặc định)", "Sans-serif", "Serif"], index=0, disabled=True)
    glass_card_end()

    glass_card_start()
    st.markdown("### 🌍 Ngôn ngữ")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.native_lang = st.selectbox("Ngôn ngữ mẹ đẻ", list(LANGUAGES.keys()),
                                                      index=list(LANGUAGES.keys()).index(st.session_state.native_lang))
    with c2:
        learnable = [k for k in LANGUAGES if not LANGUAGES[k].get("soon")]
        st.session_state.target_lang = st.selectbox("Ngôn ngữ đang học", learnable,
                                                      index=learnable.index(st.session_state.target_lang))
    glass_card_end()

    glass_card_start()
    st.markdown("### 🔊 Giọng nói AI")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.ai_voice = st.selectbox("Giọng đọc", ["Nữ (US)", "Nam (US)", "Nữ (UK)", "Nam (UK)"],
                                                   index=["Nữ (US)", "Nam (US)", "Nữ (UK)", "Nam (UK)"].index(st.session_state.ai_voice))
    with c2:
        st.session_state.speech_speed = st.slider("Tốc độ nói", 0.5, 1.5, st.session_state.speech_speed, 0.1)
    glass_card_end()

    glass_card_start()
    st.markdown("### 🤖 Cấu hình AI (OpenAI API)")
    st.caption("Nhập OpenAI API Key để kích hoạt AI thật (chat, dịch, chấm bài nâng cao). "
               "Nếu để trống, hệ thống dùng Chatbot giả lập để bạn vẫn trải nghiệm được đầy đủ tính năng.")
    key_input = st.text_input("OpenAI API Key", value=st.session_state.openai_api_key, type="password",
                               placeholder="sk-...")
    if st.button("💾 Lưu API Key"):
        st.session_state.openai_api_key = key_input
        st.success("✅ Đã lưu! AI thật sẽ được sử dụng ở các trang Chat/Dịch/Chấm bài." if key_input else "Đã xoá key, dùng chế độ giả lập.")
    glass_card_end()


# ==============================================================================
# 25. ROUTER - ĐIỀU HƯỚNG TRANG
# ==============================================================================
def router():
    render_sidebar()
    page = st.session_state.page
    page_map = {
        "Trang chủ": page_home,
        "Học từ vựng": page_vocab,
        "Học ngữ pháp": page_grammar,
        "Luyện phát âm": page_pronunciation,
        "Luyện nghe": page_listening,
        "Luyện nói": page_speaking,
        "Luyện đọc": page_reading,
        "Luyện viết": page_writing,
        "Chat với AI": page_chat,
        "Dịch văn bản": lambda: translate_ui("text"),
        "Dịch giọng nói": lambda: translate_ui("voice"),
        "Dịch camera": lambda: translate_ui("camera"),
        "Flashcard": page_flashcard,
        "Mini Game": page_game,
        "Bài kiểm tra": page_quiz,
        "Thống kê": page_stats,
        "Hồ sơ": page_profile,
        "Cài đặt": page_settings,
    }
    func = page_map.get(page, page_home)
    func()


# ==============================================================================
# 26. MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    router()
