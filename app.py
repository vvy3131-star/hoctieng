# -*- coding: utf-8 -*-
"""
================================================================================
 AI BUDDY - Người bạn đồng hành học ngoại ngữ
 Một nhân vật AI hoạt hình lớn, có cá tính, đứng giữa màn hình trò chuyện
 và dạy ngoại ngữ cho người dùng.

 File DUY NHẤT: app.py
 - Không sidebar, không menu phức tạp.
 - Toàn bộ code (giao diện, logic, AI, lưu trữ) nằm trong 1 file này.
================================================================================
 CÁCH CHẠY:
     pip install streamlit
     streamlit run app.py

 TÍCH HỢP AI THẬT (tuỳ chọn):
     - Mở phần cài đặt (icon ⚙️ góc trên) và dán OpenAI API Key.
     - Nếu không có Key, ứng dụng dùng "bộ não" rule-based có cá tính
       riêng để vẫn dạy học & trò chuyện được đầy đủ (chế độ demo).

 LƯU TRỮ TIẾN TRÌNH:
     - Tự động lưu vào file JSON "ai_buddy_data.json" cùng thư mục.
     - Mỗi lần mở lại app, AI sẽ nhớ tên bạn, ngôn ngữ đang học, cấp độ,
       streak, từ đã học... và chào bạn như một người bạn quen.
================================================================================
"""

import streamlit as st
import json
import os
import random
import re
import time
import datetime
import unicodedata

# ==============================================================================
# 1. CẤU HÌNH TRANG
# ==============================================================================
st.set_page_config(
    page_title="AI Buddy - Bạn đồng hành học ngoại ngữ",
    page_icon="🐻",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_buddy_data.json")

# ==============================================================================
# 2. DỮ LIỆU NGÔN NGỮ & GIÁO TRÌNH
# ==============================================================================
LANGUAGES = {
    "Tiếng Anh":          {"flag": "🇬🇧", "tts": "en-US", "keywords": ["anh", "english", "tiếng anh"]},
    "Tiếng Trung":        {"flag": "🇨🇳", "tts": "zh-CN", "keywords": ["trung", "chinese", "tiếng trung", "trung quốc"]},
    "Tiếng Nhật":         {"flag": "🇯🇵", "tts": "ja-JP", "keywords": ["nhật", "japanese", "tiếng nhật"]},
    "Tiếng Hàn":          {"flag": "🇰🇷", "tts": "ko-KR", "keywords": ["hàn", "korean", "tiếng hàn", "hàn quốc"]},
    "Tiếng Pháp":         {"flag": "🇫🇷", "tts": "fr-FR", "keywords": ["pháp", "french", "tiếng pháp"]},
    "Tiếng Đức":          {"flag": "🇩🇪", "tts": "de-DE", "keywords": ["đức", "german", "tiếng đức"]},
    "Tiếng Tây Ban Nha":  {"flag": "🇪🇸", "tts": "es-ES", "keywords": ["tây ban nha", "spanish", "tiếng tây ban nha"]},
    "Tiếng Nga":          {"flag": "🇷🇺", "tts": "ru-RU", "keywords": ["nga", "russian", "tiếng nga"]},
    "Tiếng Việt":         {"flag": "🇻🇳", "tts": "vi-VN", "keywords": ["việt", "vietnamese", "tiếng việt"]},
}

# Giáo trình theo cấp độ - dễ mở rộng: chỉ cần thêm phần tử vào list bên dưới.
# Mỗi ngôn ngữ có các Level, mỗi Level có tiêu đề + danh sách từ/câu cần học.
LESSON_DB = {
    "Tiếng Anh": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Hello", "meaning": "Xin chào", "phonetic": "/həˈloʊ/"},
            {"phrase": "Goodbye", "meaning": "Tạm biệt", "phonetic": "/ˌɡʊdˈbaɪ/"},
            {"phrase": "Thank you", "meaning": "Cảm ơn", "phonetic": "/ˈθæŋk juː/"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "My name is...", "meaning": "Tôi tên là...", "phonetic": "/maɪ neɪm ɪz/"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Family", "meaning": "Gia đình", "phonetic": "/ˈfæm.əl.i/"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "How much is this?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "/haʊ mʌtʃ ɪz ðɪs/"},
        ]},
    ],
    "Tiếng Trung": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "你好", "meaning": "Xin chào", "phonetic": "nǐ hǎo"},
            {"phrase": "再见", "meaning": "Tạm biệt", "phonetic": "zài jiàn"},
            {"phrase": "谢谢", "meaning": "Cảm ơn", "phonetic": "xiè xiè"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "我叫...", "meaning": "Tôi tên là...", "phonetic": "wǒ jiào..."},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "家人", "meaning": "Gia đình", "phonetic": "jiā rén"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "这个多少钱？", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "zhège duōshǎo qián?"},
        ]},
    ],
    "Tiếng Nhật": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "こんにちは", "meaning": "Xin chào", "phonetic": "Konnichiwa"},
            {"phrase": "さようなら", "meaning": "Tạm biệt", "phonetic": "Sayounara"},
            {"phrase": "ありがとう", "meaning": "Cảm ơn", "phonetic": "Arigatou"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "私の名前は...です", "meaning": "Tôi tên là...", "phonetic": "Watashi no namae wa... desu"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "家族", "meaning": "Gia đình", "phonetic": "Kazoku"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "これはいくらですか？", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "Kore wa ikura desu ka?"},
        ]},
    ],
    "Tiếng Hàn": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "안녕하세요", "meaning": "Xin chào", "phonetic": "Annyeonghaseyo"},
            {"phrase": "안녕히 가세요", "meaning": "Tạm biệt", "phonetic": "Annyeonghi gaseyo"},
            {"phrase": "감사합니다", "meaning": "Cảm ơn", "phonetic": "Gamsahamnida"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "제 이름은...입니다", "meaning": "Tôi tên là...", "phonetic": "Je ireumeun...imnida"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "가족", "meaning": "Gia đình", "phonetic": "Gajok"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "이거 얼마예요?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "Igeo eolmayeyo?"},
        ]},
    ],
    "Tiếng Pháp": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Bonjour", "meaning": "Xin chào", "phonetic": "/bɔ̃.ʒuʁ/"},
            {"phrase": "Au revoir", "meaning": "Tạm biệt", "phonetic": "/o ʁə.vwaʁ/"},
            {"phrase": "Merci", "meaning": "Cảm ơn", "phonetic": "/mɛʁ.si/"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "Je m'appelle...", "meaning": "Tôi tên là...", "phonetic": "/ʒə ma.pɛl/"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Famille", "meaning": "Gia đình", "phonetic": "/fa.mij/"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "Combien ça coûte?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "/kɔ̃.bjɛ̃ sa kut/"},
        ]},
    ],
    "Tiếng Đức": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Hallo", "meaning": "Xin chào", "phonetic": "/ˈhalo/"},
            {"phrase": "Auf Wiedersehen", "meaning": "Tạm biệt", "phonetic": "/aʊf ˈviːdɐˌzeːən/"},
            {"phrase": "Danke", "meaning": "Cảm ơn", "phonetic": "/ˈdaŋkə/"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "Ich heiße...", "meaning": "Tôi tên là...", "phonetic": "/ɪç ˈhaɪsə/"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Familie", "meaning": "Gia đình", "phonetic": "/faˈmiːli̯ə/"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "Wie viel kostet das?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "/viː fiːl ˈkɔstət das/"},
        ]},
    ],
    "Tiếng Tây Ban Nha": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Hola", "meaning": "Xin chào", "phonetic": "/ˈola/"},
            {"phrase": "Adiós", "meaning": "Tạm biệt", "phonetic": "/aˈðjos/"},
            {"phrase": "Gracias", "meaning": "Cảm ơn", "phonetic": "/ˈɡɾaθjas/"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "Me llamo...", "meaning": "Tôi tên là...", "phonetic": "/me ˈʝamo/"},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Familia", "meaning": "Gia đình", "phonetic": "/faˈmilja/"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "¿Cuánto cuesta esto?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "/ˈkwanto ˈkwesta ˈesto/"},
        ]},
    ],
    "Tiếng Nga": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Привет", "meaning": "Xin chào", "phonetic": "Privet"},
            {"phrase": "До свидания", "meaning": "Tạm biệt", "phonetic": "Do svidaniya"},
            {"phrase": "Спасибо", "meaning": "Cảm ơn", "phonetic": "Spasibo"},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "Меня зовут...", "meaning": "Tôi tên là...", "phonetic": "Menya zovut..."},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Семья", "meaning": "Gia đình", "phonetic": "Sem'ya"},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "Сколько это стоит?", "meaning": "Cái này bao nhiêu tiền?", "phonetic": "Skol'ko eto stoit?"},
        ]},
    ],
    "Tiếng Việt": [
        {"title": "Chào hỏi", "items": [
            {"phrase": "Xin chào", "meaning": "Hello", "phonetic": ""},
            {"phrase": "Tạm biệt", "meaning": "Goodbye", "phonetic": ""},
            {"phrase": "Cảm ơn", "meaning": "Thank you", "phonetic": ""},
        ]},
        {"title": "Giới thiệu bản thân", "items": [
            {"phrase": "Tôi tên là...", "meaning": "My name is...", "phonetic": ""},
        ]},
        {"title": "Gia đình", "items": [
            {"phrase": "Gia đình", "meaning": "Family", "phonetic": ""},
        ]},
        {"title": "Mua sắm", "items": [
            {"phrase": "Cái này bao nhiêu tiền?", "meaning": "How much is this?", "phonetic": ""},
        ]},
    ],
}

ROLEPLAY_SCENARIOS = ["Khách hàng", "Nhân viên", "Bạn bè", "Du lịch", "Nhà hàng", "Phỏng vấn"]

ANIMALS = {
    "bear":   {"name": "Gấu nâu", "face": "#B98255", "muzzle": "#F3D9BC", "ear": "#A9744F"},
    "panda":  {"name": "Gấu trúc", "face": "#FDFDFD", "muzzle": "#FFFFFF", "ear": "#2E2E2E"},
    "cat":    {"name": "Mèo cam", "face": "#F0A94E", "muzzle": "#FCE4C4", "ear": "#E8933A"},
    "fox":    {"name": "Cáo lửa", "face": "#ED7D31", "muzzle": "#FCEBDD", "ear": "#D96522"},
    "rabbit": {"name": "Thỏ bông", "face": "#F7F1EA", "muzzle": "#FFFFFF", "ear": "#F3D9E6"},
    "robot":  {"name": "Robot Bo", "face": "#B7C2CC", "muzzle": "#DCE4EA", "ear": "#8C98A4"},
}

# ==============================================================================
# 3. LƯU TRỮ DỮ LIỆU (JSON) - BỘ NHỚ DÀI HẠN CỦA AI
# ==============================================================================
DEFAULT_DATA = {
    "name": "",
    "target_lang": "",
    "level": 1,                 # số thứ tự level hiện tại (1-based)
    "item_index": 0,            # vị trí từ/câu đang học trong level
    "words_learned": [],
    "mistakes": {},             # {phrase: số lần đọc sai}
    "chat_log": [],             # [{role, text, ts}]
    "total_study_minutes": 0,
    "streak": 0,
    "last_study_date": "",
    "character": "bear",
    "voice_gender": "female",
    "voice_rate": 1.0,
    "onboard_stage": "ask_language",   # ask_language -> ask_name -> lesson
    "mode": "lesson",           # lesson / roleplay / free_chat
    "roleplay_scenario": "",
    "theme": "dark",
    "openai_api_key": "",
    "first_time": True,
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
    """Lưu toàn bộ tiến trình học xuống file JSON (bộ nhớ dài hạn)."""
    try:
        payload = {k: st.session_state[k] for k in DEFAULT_DATA.keys() if k in st.session_state}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # không chặn UI nếu ghi file lỗi (ví dụ môi trường read-only)


def init_state():
    if "loaded" not in st.session_state:
        data = load_data()
        for k, v in data.items():
            st.session_state[k] = v
        st.session_state.loaded = True
        st.session_state.mood = "wave"          # trạng thái biểu cảm hiện tại
        st.session_state.speaking_id = 0         # đổi số này để trigger animation nói
        st.session_state.pending_greeting = True  # sẽ hiển thị lời chào khi vừa mở app
        st.session_state.last_score = None
        _update_streak_on_open()


def _update_streak_on_open():
    today = str(datetime.date.today())
    last = st.session_state.last_study_date
    if last == today:
        pass  # đã học hôm nay rồi, giữ nguyên streak
    elif last == str(datetime.date.today() - datetime.timedelta(days=1)):
        st.session_state.streak += 1
        st.session_state.last_study_date = today
    elif last == "":
        st.session_state.streak = 0
        st.session_state.last_study_date = today
    else:
        st.session_state.streak = 1  # gián đoạn -> tính lại từ đầu
        st.session_state.last_study_date = today


init_state()


# ==============================================================================
# 4. CÁ TÍNH AI - KHO CÂU THOẠI (vui vẻ, hài hước, hay trêu, luôn động viên)
# ==============================================================================
PERSONA = {
    "greet_new": [
        "Xin chào! Mình là {char_name} 🐾 — bạn đồng hành học ngoại ngữ của bạn đây! Bạn muốn học ngôn ngữ nào nào?",
        "Yo yo! Mình là {char_name}! Rất vui được làm quen. Bạn muốn chinh phục ngôn ngữ nào cùng mình?",
    ],
    "greet_returning": [
        "Chào mừng quay lại, {name}! 🎉 Hôm nay là ngày học thứ {streak} liên tiếp của bạn đấy. Lần trước chúng ta học đến '{lesson_title}'. Tiếp tục nhé?",
        "Ơ, {name} về rồi kìa! 😄 Streak {streak} ngày rồi đó nha, đừng để đứt gánh giữa đường! Mình đang chờ ở bài '{lesson_title}'.",
    ],
    "ask_name": [
        "Được rồi! Trước khi bắt đầu, mình gọi bạn là gì cho thân mật nè?",
        "Ok chốt đơn {lang}! À mà mình chưa biết tên bạn, xưng hô sao cho tiện đây?",
    ],
    "confirm_language": [
        "Được rồi! Hôm nay chúng ta sẽ bắt đầu từ bài đầu tiên nhé, {name}!",
        "Yeah! {lang} có mình đồng hành là auto dễ luôn. Bắt đầu bài đầu tiên thôi!",
    ],
    "present_word": [
        "Nghe mình đọc nè: '{phrase}' — nghĩa là '{meaning}'. Đọc lại thử xem!",
        "Từ này hay lắm nè: '{phrase}' ({meaning}). Bạn đọc lại cho mình nghe nào!",
    ],
    "correct": [
        "Chuẩn không cần chỉnh luôn! 🎯 Giỏi ghê!",
        "Ơ hay đó! Phát âm nghe xịn phết! 😎",
        "Đỉnh của chóp! Tiếp tục phát huy nhé!",
    ],
    "close_enough": [
        "Suýt chuẩn rồi đó! Chỉ thiếu xíu xiu nữa thôi. Thử lại nhé!",
        "Gần đúng rồi nè! Cố lên xíu nữa là ăn điểm tuyệt đối!",
    ],
    "wrong": [
        "Hmm, chưa đúng lắm đâu 😅 Để mình đọc lại cho nghe, thử lần nữa nhé!",
        "Ấy ấy chưa trúng rồi! Không sao, nghe kỹ lại rồi đọc lại nào!",
    ],
    "lazy_tease": [
        "Hừm... bạn định lười thật à? Thôi học với mình 5 phút thôi, biết đâu lại học luôn 30 phút đó 😏",
        "Lười hả? Được thôi, vậy mình... đợi bạn ở đây luôn 🙂 Nhưng mà 5 phút thôi cũng được, thử không?",
    ],
    "encourage_progress": [
        "Hôm nay tiến bộ hơn hôm qua đấy! Mình có để ý nhé! 👀✨",
        "Bạn học nhanh ghê, mình phải tăng độ khó lên rồi đây!",
    ],
    "many_mistakes": [
        "Không sao đâu. Mình sẽ chậm lại để học chắc hơn nhé, đừng nản!",
        "Sai là chuyện thường mà, ngay cả mình đôi lúc còn lú nữa là! Học tiếp thôi!",
    ],
    "level_up": [
        "Chúc mừng! 🥳 Bạn vừa lên Level {level} — '{lesson_title}'. Xịn sò quá đi!",
        "Ting ting! 🔔 Level {level} mở khoá: '{lesson_title}'. Cùng chinh phục nào!",
    ],
    "idle_prompt": [
        "Bạn còn ở đó không? Mình đang chờ đây 👀",
        "Ơ... đi đâu mất rồi ta? Mình vẫn chờ bạn đọc bài nè!",
    ],
    "not_understand_ack": [
        "À, để mình giải thích bằng tiếng Việt nhé:",
        "Ok không hiểu thì mình dịch giúp nè:",
    ],
    "farewell": [
        "Hẹn gặp lại nhé! Nhớ quay lại học tiếp với mình đó! 👋",
        "Bye bye! Đừng để streak bị đứt nha, mình chờ bạn quay lại!",
    ],
    "roleplay_intro": [
        "Giờ mình đóng vai '{scenario}' nhé, còn bạn cứ thử dùng {lang} nói chuyện với mình xem sao!",
        "Hehe, tới màn nhập vai rồi! Mình sẽ là '{scenario}'. Bạn thử giao tiếp bằng {lang} nhé!",
    ],
    "ask_new_or_review": [
        "Bạn muốn ôn bài cũ hay học từ mới nào? 🤔",
    ],
}


def persona_pick(category, **kwargs):
    text = random.choice(PERSONA[category])
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalize_text(s):
    return strip_accents(s).lower().strip().replace("?", "").replace(".", "").replace(",", "")


def detect_language_intent(text):
    t = normalize_text(text)
    for lang, meta in LANGUAGES.items():
        for kw in meta["keywords"]:
            if strip_accents(kw) in t:
                return lang
    return None


def detect_lazy(text):
    t = normalize_text(text)
    return any(k in t for k in ["luoi", "khong muon hoc", "met qua", "chan qua", "nghi hoc"])


def detect_not_understand(text):
    t = normalize_text(text)
    return any(k in t for k in ["khong hieu", "nghia la gi", "la gi vay", "giai thich"])


def detect_review_request(text):
    t = normalize_text(text)
    return any(k in t for k in ["on bai cu", "on lai", "bai cu"])


def detect_new_lesson_request(text):
    t = normalize_text(text)
    return any(k in t for k in ["bai moi", "hoc moi", "tiep tuc", "hoc tiep"])


def detect_roleplay_request(text):
    t = normalize_text(text)
    return any(k in t for k in ["hoi thoai", "nhap vai", "luyen noi chuyen", "roleplay"])


def score_pronunciation_attempt(user_text, target_phrase):
    """So khớp gần đúng (demo). Trả điểm 0-100 dựa trên độ giống ký tự."""
    a = normalize_text(user_text)
    b = normalize_text(target_phrase)
    if not a:
        return 0
    if a == b:
        return random.randint(93, 100)
    # tính điểm tương đồng đơn giản theo ký tự chung
    common = sum(1 for ch in a if ch in b)
    ratio = common / max(len(b), 1)
    base = int(ratio * 80) + random.randint(0, 15)
    return max(20, min(base, 92))


# ==============================================================================
# 5. AI ENGINE - ƯU TIÊN OPENAI API THẬT, FALLBACK RULE-BASED CÓ CÁ TÍNH
# ==============================================================================
def call_openai_api(messages, api_key):
    try:
        import requests
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.85, "max_tokens": 250},
            timeout=20,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None


def build_system_prompt():
    char = ANIMALS[st.session_state.character]["name"]
    lang = st.session_state.target_lang or "chưa chọn"
    return (
        f"Bạn là {char}, một AI đồng hành dạy ngoại ngữ, tính cách vui vẻ, hài hước, hay trêu đùa nhẹ nhàng "
        f"nhưng luôn động viên tích cực, giống bạn thân chứ không phải trợ lý khô khan. "
        f"Học viên tên là '{st.session_state.name or 'bạn học'}', đang học {lang}, "
        f"hiện ở Level {st.session_state.level}, streak {st.session_state.streak} ngày. "
        f"Nếu đang ở chế độ hội thoại nhập vai '{st.session_state.roleplay_scenario}', chỉ dùng {lang} để nói, "
        f"và nếu học viên nói 'không hiểu' thì giải thích lại bằng tiếng Việt. Trả lời ngắn gọn, tự nhiên, có cảm xúc."
    )


def get_ai_reply(user_text):
    api_key = st.session_state.openai_api_key
    history = st.session_state.chat_log[-10:]
    if api_key:
        messages = [{"role": "system", "content": build_system_prompt()}]
        for h in history:
            role = "user" if h["role"] == "user" else "assistant"
            messages.append({"role": role, "content": h["text"]})
        messages.append({"role": "user", "content": user_text})
        real = call_openai_api(messages, api_key)
        if real:
            return real
    # ---- fallback rule-based (không cần API) ----
    return rule_based_reply(user_text)


def rule_based_reply(user_text):
    """'Bộ não' giả lập có cá tính, biết dẫn dắt bài học theo state hiện tại."""
    stage = st.session_state.onboard_stage

    # --- Giai đoạn onboarding: hỏi ngôn ngữ ---
    if stage == "ask_language":
        lang = detect_language_intent(user_text)
        if lang:
            st.session_state.target_lang = lang
            st.session_state.onboard_stage = "ask_name"
            st.session_state.mood = "happy"
            return persona_pick("ask_name", lang=lang)
        else:
            st.session_state.mood = "thinking"
            return "Mình chưa nghe rõ bạn muốn học ngôn ngữ nào 🤔 Thử nói ví dụ: 'Tôi muốn học tiếng Trung' xem!"

    # --- Giai đoạn onboarding: hỏi tên ---
    if stage == "ask_name":
        name = user_text.strip()
        name = re.sub(r"(?i)^(mình|tôi|em|anh|chị)\s*(tên|là)?\s*", "", name).strip() or name
        st.session_state.name = name[:30] if name else "bạn học"
        st.session_state.onboard_stage = "lesson"
        st.session_state.mode = "lesson"
        st.session_state.mood = "wave"
        return persona_pick("confirm_language", name=st.session_state.name, lang=st.session_state.target_lang)

    # --- Chế độ học bài (lesson) ---
    if st.session_state.mode == "lesson":
        return handle_lesson_input(user_text)

    # --- Chế độ hội thoại nhập vai ---
    if st.session_state.mode == "roleplay":
        return handle_roleplay_input(user_text)

    # --- Chế độ tự do ---
    st.session_state.mood = "happy"
    return random.choice([
        "Ồ thú vị đấy! Kể mình nghe thêm đi!",
        "Haha được đó! Rồi sao nữa?",
        "Nghe hay ghê! Bạn còn muốn học thêm gì không?",
    ])


def current_level_data():
    lang = st.session_state.target_lang
    plan = LESSON_DB.get(lang, [])
    idx = st.session_state.level - 1
    if 0 <= idx < len(plan):
        return plan[idx]
    return None


def current_item():
    level_data = current_level_data()
    if not level_data:
        return None
    items = level_data["items"]
    idx = st.session_state.item_index
    if 0 <= idx < len(items):
        return items[idx]
    return None


def advance_item():
    level_data = current_level_data()
    st.session_state.item_index += 1
    if st.session_state.item_index >= len(level_data["items"]):
        # hết level -> lên level mới
        st.session_state.level += 1
        st.session_state.item_index = 0
        new_level = current_level_data()
        if new_level is None:
            # hết giáo trình -> chuyển sang hội thoại tự do / nhập vai
            st.session_state.mode = "roleplay"
            st.session_state.roleplay_scenario = random.choice(ROLEPLAY_SCENARIOS)
            st.session_state.mood = "surprised"
            return "level_finished"
        st.session_state.mood = "happy"
        return "level_up"
    return "next_item"


def handle_lesson_input(user_text):
    if detect_lazy(user_text):
        st.session_state.mood = "sad"
        return persona_pick("lazy_tease")

    if detect_not_understand(user_text):
        item = current_item()
        st.session_state.mood = "thinking"
        if item:
            return persona_pick("not_understand_ack") + f" '{item['phrase']}' nghĩa là '{item['meaning']}' đó!"
        return persona_pick("not_understand_ack")

    if detect_roleplay_request(user_text):
        st.session_state.mode = "roleplay"
        st.session_state.roleplay_scenario = random.choice(ROLEPLAY_SCENARIOS)
        st.session_state.mood = "surprised"
        return persona_pick("roleplay_intro", scenario=st.session_state.roleplay_scenario, lang=st.session_state.target_lang)

    if detect_review_request(user_text):
        st.session_state.item_index = max(0, st.session_state.item_index - 1)
        st.session_state.mood = "thinking"
        item = current_item()
        return "Ôn lại bài trước nhé! " + persona_pick("present_word", phrase=item["phrase"], meaning=item["meaning"])

    item = current_item()
    if not item:
        return "Hình như bạn đã học hết giáo trình hiện có rồi! Mình chuyển qua hội thoại tự do nhé 😄"

    score = score_pronunciation_attempt(user_text, item["phrase"])
    st.session_state.last_score = score
    word = item["phrase"]

    if score >= 85:
        st.session_state.mood = "happy"
        st.session_state.words_learned = list(set(st.session_state.words_learned + [word]))
        feedback = persona_pick("correct")
        result = advance_item()
        if result == "level_up":
            level_data = current_level_data()
            feedback += " " + persona_pick("level_up", level=st.session_state.level, lesson_title=level_data["title"])
            next_item = current_item()
            feedback += " " + persona_pick("present_word", phrase=next_item["phrase"], meaning=next_item["meaning"])
        elif result == "level_finished":
            feedback += (" Bạn vừa hoàn thành hết giáo trình cơ bản rồi đó! 🎓 Giờ mình chuyển sang chế độ "
                         f"hội thoại nhập vai '{st.session_state.roleplay_scenario}' để luyện phản xạ thật nhé!")
        else:
            next_item = current_item()
            feedback += " Từ tiếp theo nè: " + persona_pick("present_word", phrase=next_item["phrase"], meaning=next_item["meaning"])
        return feedback
    elif score >= 55:
        st.session_state.mood = "thinking"
        st.session_state.mistakes[word] = st.session_state.mistakes.get(word, 0) + 1
        return persona_pick("close_enough") + f" (Điểm: {score}/100)"
    else:
        st.session_state.mood = "sad"
        st.session_state.mistakes[word] = st.session_state.mistakes.get(word, 0) + 1
        extra = ""
        if st.session_state.mistakes[word] >= 2:
            extra = " " + persona_pick("many_mistakes")
        return persona_pick("wrong") + f" (Điểm: {score}/100){extra} Nghe lại: '{word}' ({item['meaning']})."


ROLEPLAY_LINES = {
    "Nhà hàng": {
        "Tiếng Anh": ["Welcome! What would you like to order today?", "Would you like something to drink?", "Here is your food, enjoy your meal!"],
        "Tiếng Trung": ["欢迎光临！你想点什么？", "要喝点什么吗？", "这是你的菜，请慢用！"],
    },
    "Du lịch": {
        "Tiếng Anh": ["Excuse me, do you need directions?", "This place is famous for its old town.", "Have a wonderful trip!"],
        "Tiếng Trung": ["请问你需要问路吗？", "这个地方以老城区出名。", "祝你旅途愉快！"],
    },
    "Phỏng vấn": {
        "Tiếng Anh": ["Can you tell me about yourself?", "What are your strengths?", "Why do you want this job?"],
        "Tiếng Trung": ["能介绍一下你自己吗？", "你的优点是什么？", "你为什么想要这份工作？"],
    },
}


def handle_roleplay_input(user_text):
    if detect_not_understand(user_text):
        st.session_state.mood = "thinking"
        return persona_pick("not_understand_ack") + " (giải thích ngữ cảnh) Đây là tình huống '" + st.session_state.roleplay_scenario + "', cứ trả lời tự nhiên theo vai của bạn nhé!"
    scenario = st.session_state.roleplay_scenario
    lang = st.session_state.target_lang
    lines = ROLEPLAY_LINES.get(scenario, {}).get(lang)
    st.session_state.mood = random.choice(["happy", "thinking", "surprised"])
    if lines:
        return random.choice(lines)
    return f"(nhập vai '{scenario}' bằng {lang}) " + random.choice([
        "Interesting! Tell me more.", "Haha, thú vị đấy! Tiếp tục nào.", "Được đó, nói tiếp xem sao!"
    ])


# ==============================================================================
# 6. GIAO DIỆN - CSS + NHÂN VẬT SVG HOẠT HÌNH
# ==============================================================================
def inject_css():
    dark = st.session_state.theme == "dark"
    bg = "linear-gradient(160deg,#0f1020,#1b1836,#241b3f)" if dark else "linear-gradient(160deg,#fef6ff,#eaf2ff,#f7f9ff)"
    text_color = "#F2F0FF" if dark else "#242233"
    bubble_bg = "rgba(255,255,255,0.08)" if dark else "rgba(255,255,255,0.85)"
    bubble_border = "rgba(255,255,255,0.2)" if dark else "rgba(0,0,0,0.08)"
    panel_bg = "rgba(255,255,255,0.06)" if dark else "rgba(255,255,255,0.6)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Quicksand:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Quicksand', sans-serif !important; }}
    .stApp {{ background: {bg}; background-attachment: fixed; color: {text_color}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    .buddy-name {{
        text-align:center; font-family:'Baloo 2', sans-serif; font-weight:800; font-size:26px;
        background: linear-gradient(90deg,#FF8FAB,#7F5AF0,#2CB67D);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-size:200% auto; animation: shine 5s linear infinite; margin-bottom:2px;
    }}
    @keyframes shine {{ to {{ background-position: 200% center; }} }}

    .buddy-sub {{ text-align:center; opacity:.65; font-size:13px; margin-bottom:10px; }}

    /* ---- Bong bóng hội thoại ---- */
    .speech-bubble {{
        background: {bubble_bg};
        border: 1px solid {bubble_border};
        backdrop-filter: blur(14px);
        border-radius: 24px;
        padding: 16px 22px;
        max-width: 480px;
        margin: 0 auto 6px auto;
        text-align: center;
        font-size: 17px;
        font-weight: 600;
        box-shadow: 0 8px 28px rgba(0,0,0,0.18);
        animation: bubbleIn .35s ease;
        position: relative;
    }}
    .speech-bubble:after {{
        content:""; position:absolute; left:50%; bottom:-9px; transform:translateX(-50%);
        border-width: 10px 9px 0 9px; border-style: solid;
        border-color: {bubble_bg} transparent transparent transparent;
    }}
    @keyframes bubbleIn {{ from {{ opacity:0; transform: translateY(10px) scale(.95);}} to {{opacity:1; transform:translateY(0) scale(1);}} }}

    /* ---- Nhân vật ---- */
    .character-wrap {{
        display:flex; justify-content:center; margin: 6px 0 4px 0;
        animation: floaty 3.2s ease-in-out infinite;
    }}
    @keyframes floaty {{ 0%,100% {{ transform: translateY(0);}} 50% {{ transform: translateY(-12px);}} }}

    .char-eye {{ transform-origin: center; animation: blink 4.6s infinite; }}
    @keyframes blink {{ 0%,92%,100% {{ transform: scaleY(1);}} 95% {{ transform: scaleY(0.12);}} }}

    .char-mouth.talking {{ animation: talk .35s ease-in-out 7; transform-origin: center; }}
    @keyframes talk {{ 0%,100% {{ transform: scaleY(1);}} 50% {{ transform: scaleY(1.7);}} }}

    .char-hand-wave {{ transform-origin: 70% 20%; animation: wave 1s ease-in-out 3; }}
    @keyframes wave {{ 0%,100% {{ transform: rotate(0deg);}} 25% {{ transform: rotate(-18deg);}} 75% {{ transform: rotate(14deg);}} }}

    /* ---- Panel dưới nhân vật ---- */
    .status-row {{
        display:flex; justify-content:center; gap:10px; margin: 6px 0 18px 0; flex-wrap: wrap;
    }}
    .status-chip {{
        background: {panel_bg}; border:1px solid {bubble_border}; backdrop-filter: blur(10px);
        padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight:600;
    }}

    .stButton>button {{
        border-radius: 14px !important; border:none !important;
        background: linear-gradient(135deg,#7F5AF0,#2CB67D) !important;
        color:white !important; font-weight:700 !important;
        box-shadow: 0 4px 16px rgba(127,90,240,.35);
        transition: all .2s ease !important;
    }}
    .stButton>button:hover {{ transform: translateY(-2px) scale(1.02); }}

    .stTextInput>div>div>input {{
        border-radius: 16px !important; padding: 12px 16px !important;
    }}

    @media (max-width: 640px) {{
        .speech-bubble {{ max-width: 92%; font-size:15px; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def build_character_svg(animal="bear", mood="idle", speaking=False):
    a = ANIMALS.get(animal, ANIMALS["bear"])
    face, ear, muzzle = a["face"], a["ear"], a["muzzle"]

    # Tai theo loại con vật
    if animal == "rabbit":
        ears = f"""
        <ellipse cx="118" cy="55" rx="16" ry="55" fill="{ear}" transform="rotate(-12 118 55)"/>
        <ellipse cx="182" cy="55" rx="16" ry="55" fill="{ear}" transform="rotate(12 182 55)"/>
        """
    elif animal == "cat" or animal == "fox":
        ears = f"""
        <polygon points="95,90 70,20 135,70" fill="{ear}"/>
        <polygon points="205,90 230,20 165,70" fill="{ear}"/>
        """
    elif animal == "robot":
        ears = f"""
        <rect x="145" y="10" width="10" height="35" rx="4" fill="{ear}"/>
        <circle cx="150" cy="10" r="9" fill="#FF6B6B"/>
        <rect x="55" y="95" width="20" height="55" rx="8" fill="{ear}"/>
        <rect x="225" y="95" width="20" height="55" rx="8" fill="{ear}"/>
        """
    else:  # bear / panda
        ears = f"""
        <circle cx="90" cy="65" r="34" fill="{ear}"/>
        <circle cx="210" cy="65" r="34" fill="{ear}"/>
        """

    # Miệng theo tâm trạng
    if mood == "sad":
        mouth = '<path d="M130 210 Q150 195 170 210" stroke="#3A2E2E" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif mood == "surprised":
        mouth = '<ellipse cx="150" cy="208" rx="12" ry="15" fill="#3A2E2E"/>'
    elif mood == "thinking":
        mouth = '<path d="M132 208 Q150 208 168 202" stroke="#3A2E2E" stroke-width="5" fill="none" stroke-linecap="round"/>'
    else:  # happy / idle / wave
        mouth = '<path d="M125 198 Q150 225 175 198" stroke="#3A2E2E" stroke-width="6" fill="none" stroke-linecap="round"/>'

    cheeks = ""
    if mood in ("happy", "wave"):
        cheeks = f"""
        <ellipse cx="108" cy="185" rx="14" ry="9" fill="#FF9FB0" opacity="0.55"/>
        <ellipse cx="192" cy="185" rx="14" ry="9" fill="#FF9FB0" opacity="0.55"/>
        """

    eyebrows = ""
    if mood == "thinking":
        eyebrows = '<path d="M110 130 Q120 122 132 128" stroke="#3A2E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if mood == "sad":
        eyebrows = ('<path d="M108 128 Q122 138 136 130" stroke="#3A2E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
                    '<path d="M164 130 Q178 138 192 128" stroke="#3A2E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')

    hand_class = "char-hand-wave" if mood == "wave" else ""
    mouth_class = "talking" if speaking else ""

    svg = f"""
    <svg viewBox="0 0 300 320" width="100%" height="100%" style="max-width:280px;">
        <!-- Thân -->
        <ellipse cx="150" cy="290" rx="80" ry="34" fill="{face}" opacity="0.9"/>
        <!-- Tay -->
        <ellipse class="{hand_class}" cx="55" cy="260" rx="20" ry="30" fill="{face}"/>
        <ellipse cx="245" cy="260" rx="20" ry="30" fill="{face}"/>
        <!-- Tai -->
        {ears}
        <!-- Đầu -->
        <circle cx="150" cy="150" r="105" fill="{face}"/>
        <!-- Mõm / mặt trong -->
        <ellipse cx="150" cy="185" rx="62" ry="48" fill="{muzzle}"/>
        {eyebrows}
        <!-- Mắt -->
        <g class="char-eye">
            <ellipse cx="118" cy="150" rx="14" ry="17" fill="white"/>
            <circle cx="120" cy="152" r="7" fill="#2B2B2B"/>
        </g>
        <g class="char-eye">
            <ellipse cx="182" cy="150" rx="14" ry="17" fill="white"/>
            <circle cx="184" cy="152" r="7" fill="#2B2B2B"/>
        </g>
        <!-- Má hồng -->
        {cheeks}
        <!-- Mũi -->
        <ellipse cx="150" cy="178" rx="9" ry="6" fill="#3A2E2E"/>
        <!-- Miệng -->
        <g class="char-mouth {mouth_class}">{mouth}</g>
    </svg>
    """
    return svg


def render_character():
    svg = build_character_svg(st.session_state.character, st.session_state.mood, speaking=True)
    st.markdown(f'<div class="character-wrap">{svg}</div>', unsafe_allow_html=True)


def render_speech_bubble(text):
    st.markdown(f'<div class="speech-bubble">{text}</div>', unsafe_allow_html=True)


# ==============================================================================
# 7. GIỌNG NÓI: TTS + MIC (Web Speech API nhúng JS trong Streamlit)
# ==============================================================================
def speak_text(text, lang_code):
    rate = st.session_state.voice_rate
    gender = st.session_state.voice_gender
    safe_text = json.dumps(text)
    html = f"""
    <script>
    (function() {{
        try {{
            const synth = window.speechSynthesis;
            const utter = new SpeechSynthesisUtterance({safe_text});
            utter.lang = "{lang_code}";
            utter.rate = {rate};
            const voices = synth.getVoices();
            let chosen = voices.find(v => v.lang === "{lang_code}" &&
                (("{gender}" === "female" && /female|nữ|woman/i.test(v.name)) ||
                 ("{gender}" === "male" && /male|nam|man/i.test(v.name))));
            if (!chosen) {{ chosen = voices.find(v => v.lang === "{lang_code}"); }}
            if (chosen) {{ utter.voice = chosen; }}
            synth.cancel();
            synth.speak(utter);
        }} catch(e) {{}}
    }})();
    </script>
    """
    st.components.v1.html(html, height=0)


def mic_button(lang_code, key="mic"):
    """Nút micro dùng Web Speech API. Kết quả nhận diện hiển thị ngay trong khung,
    đồng thời cố gắng tự điền vào ô nhập liệu chính của Streamlit (best-effort)."""
    html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; gap:6px;">
      <button onclick='
        try {{
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          const rec = new SR();
          rec.lang = "{lang_code}";
          rec.interimResults = false;
          document.getElementById("micres_{key}").innerText = "🎙️ Đang nghe...";
          rec.onresult = function(e) {{
            const text = e.results[0][0].transcript;
            document.getElementById("micres_{key}").innerText = "📝 " + text;
            // best-effort: tự điền vào ô input chính của Streamlit
            try {{
              const inputs = window.parent.document.querySelectorAll("input[type=text]");
              if (inputs.length > 0) {{
                const target = inputs[inputs.length - 1];
                const nativeSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
                nativeSetter.call(target, text);
                target.dispatchEvent(new Event("input", {{ bubbles: true }}));
              }}
            }} catch(err) {{}}
          }};
          rec.onerror = function() {{
            document.getElementById("micres_{key}").innerText = "⚠️ Không nghe rõ, thử lại nhé (cần Chrome + micro).";
          }};
          rec.start();
        }} catch(err) {{
          document.getElementById("micres_{key}").innerText = "⚠️ Trình duyệt không hỗ trợ nhận diện giọng nói.";
        }}
      ' style="
        background: linear-gradient(135deg,#FF8FAB,#7F5AF0);
        border:none; color:white; width:64px; height:64px; border-radius:50%;
        font-size:26px; cursor:pointer; box-shadow:0 6px 20px rgba(127,90,240,.45);
      ">🎤</button>
      <div id="micres_{key}" style="font-size:12px; opacity:.75; font-style:italic; text-align:center;">
        Bấm để nói (kết quả sẽ tự điền vào ô nhập bên dưới)
      </div>
    </div>
    """
    st.components.v1.html(html, height=100)


# ==============================================================================
# 8. XỬ LÝ GỬI TIN NHẮN
# ==============================================================================
def handle_send(user_text):
    if not user_text or not user_text.strip():
        return
    st.session_state.chat_log.append({"role": "user", "text": user_text, "ts": datetime.datetime.now().isoformat()})
    reply = get_ai_reply(user_text)
    st.session_state.chat_log.append({"role": "ai", "text": reply, "ts": datetime.datetime.now().isoformat()})
    st.session_state.chat_log = st.session_state.chat_log[-60:]  # giới hạn log
    st.session_state.total_study_minutes += 0.5  # ước lượng thời gian học mỗi lượt trao đổi
    st.session_state.speaking_id += 1
    save_data()


# ==============================================================================
# 9. GIAO DIỆN CHÍNH
# ==============================================================================
def render_top_bar():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("⚙️", help="Cài đặt"):
            st.session_state.show_settings = not st.session_state.get("show_settings", False)
    with c3:
        if st.button("🌙" if st.session_state.theme == "light" else "☀️", help="Đổi giao diện sáng/tối"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            save_data()
            st.rerun()

    if st.session_state.get("show_settings", False):
        with st.container(border=True):
            st.markdown("#### ⚙️ Cài đặt")
            cc1, cc2 = st.columns(2)
            with cc1:
                animal = st.selectbox("Nhân vật", list(ANIMALS.keys()), format_func=lambda k: ANIMALS[k]["name"],
                                       index=list(ANIMALS.keys()).index(st.session_state.character))
                if animal != st.session_state.character:
                    st.session_state.character = animal
                    save_data()
                    st.rerun()
                gender = st.selectbox("Giọng nói", ["female", "male"], format_func=lambda x: "Giọng nữ" if x == "female" else "Giọng nam",
                                       index=0 if st.session_state.voice_gender == "female" else 1)
                st.session_state.voice_gender = gender
            with cc2:
                rate = st.slider("Tốc độ nói", 0.5, 1.5, float(st.session_state.voice_rate), 0.1)
                st.session_state.voice_rate = rate
                key_in = st.text_input("OpenAI API Key (tuỳ chọn)", value=st.session_state.openai_api_key, type="password")
                st.session_state.openai_api_key = key_in

            if st.button("💾 Lưu cài đặt"):
                save_data()
                st.success("Đã lưu!")

            st.markdown("---")
            if st.button("🗑️ Đặt lại toàn bộ tiến trình học"):
                st.session_state.confirm_reset = True
            if st.session_state.get("confirm_reset"):
                st.warning("Bạn chắc chắn muốn xoá toàn bộ tiến trình học chứ? Hành động này không thể hoàn tác.")
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("✅ Xác nhận xoá"):
                        for k, v in DEFAULT_DATA.items():
                            st.session_state[k] = v
                        st.session_state.confirm_reset = False
                        save_data()
                        st.rerun()
                with rc2:
                    if st.button("❌ Huỷ"):
                        st.session_state.confirm_reset = False


def render_status_chips():
    chips = []
    if st.session_state.name:
        chips.append(f"👤 {st.session_state.name}")
    if st.session_state.target_lang:
        meta = LANGUAGES.get(st.session_state.target_lang, {})
        chips.append(f"{meta.get('flag','')} {st.session_state.target_lang}")
        chips.append(f"📈 Level {st.session_state.level}")
    chips.append(f"🔥 {st.session_state.streak} ngày")
    chips.append(f"📚 {len(st.session_state.words_learned)} từ")
    html = "".join([f'<span class="status-chip">{c}</span>' for c in chips])
    st.markdown(f'<div class="status-row">{html}</div>', unsafe_allow_html=True)


def get_greeting_message():
    char_name = ANIMALS[st.session_state.character]["name"]
    if st.session_state.onboard_stage == "ask_language":
        return persona_pick("greet_new", char_name=char_name)
    if st.session_state.name and st.session_state.target_lang and st.session_state.mode == "lesson":
        level_data = current_level_data()
        lesson_title = level_data["title"] if level_data else "hội thoại tự do"
        return persona_pick("greet_returning", name=st.session_state.name, streak=max(st.session_state.streak, 1),
                             lesson_title=lesson_title)
    return f"Chào {st.session_state.name or 'bạn'}! Mình đã sẵn sàng, cùng học tiếp nhé!"


def main():
    inject_css()
    st.markdown(f'<div class="buddy-name">{ANIMALS[st.session_state.character]["name"]} 🐾 AI Buddy</div>', unsafe_allow_html=True)
    st.markdown('<div class="buddy-sub">Người bạn đồng hành học ngoại ngữ của bạn</div>', unsafe_allow_html=True)

    render_top_bar()
    render_character()

    # xác định tin nhắn hiển thị trong bong bóng thoại
    if st.session_state.pending_greeting:
        msg = get_greeting_message()
        st.session_state.chat_log.append({"role": "ai", "text": msg, "ts": datetime.datetime.now().isoformat()})
        st.session_state.pending_greeting = False
        save_data()
    else:
        ai_msgs = [h for h in st.session_state.chat_log if h["role"] == "ai"]
        msg = ai_msgs[-1]["text"] if ai_msgs else get_greeting_message()

    render_speech_bubble(msg)

    lang_code = LANGUAGES.get(st.session_state.target_lang, {}).get("tts", "vi-VN")
    speak_text(msg, lang_code)

    if st.session_state.target_lang and st.session_state.onboard_stage == "lesson":
        render_status_chips()

    st.write("")
    mic_button(lang_code if st.session_state.target_lang else "vi-VN", key="main_mic")

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_text = st.text_input("Nhập câu trả lời...", label_visibility="collapsed",
                                       placeholder="Gõ hoặc dùng micro để trả lời...")
        with col2:
            submitted = st.form_submit_button("Gửi ➤", use_container_width=True)

    if submitted and user_text.strip():
        handle_send(user_text)
        st.rerun()

    # Gợi ý nhanh khi vừa hỏi ngôn ngữ / chưa có tên
    if st.session_state.onboard_stage == "ask_language":
        st.write("")
        st.caption("Hoặc chọn nhanh:")
        cols = st.columns(3)
        learnable = list(LANGUAGES.keys())
        for i, lang in enumerate(learnable):
            with cols[i % 3]:
                if st.button(f"{LANGUAGES[lang]['flag']} {lang}", key=f"quick_lang_{lang}", use_container_width=True):
                    handle_send(f"Tôi muốn học {lang}")
                    st.rerun()

    # thanh hành động nhanh trong lúc học
    if st.session_state.onboard_stage == "lesson" and st.session_state.mode == "lesson":
        st.write("")
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            if st.button("🔁 Ôn bài cũ", use_container_width=True):
                handle_send("ôn bài cũ")
                st.rerun()
        with qc2:
            if st.button("💬 Luyện hội thoại", use_container_width=True):
                handle_send("luyện hội thoại")
                st.rerun()
        with qc3:
            if st.button("❓ Không hiểu", use_container_width=True):
                handle_send("không hiểu")
                st.rerun()

    if st.session_state.mode == "roleplay":
        st.caption(f"🎭 Đang nhập vai: {st.session_state.roleplay_scenario} — chỉ dùng {st.session_state.target_lang} nhé, gõ 'không hiểu' nếu cần trợ giúp!")

    with st.expander("🗂️ Lịch sử trò chuyện gần đây"):
        for h in st.session_state.chat_log[-14:]:
            who = "🙋 Bạn" if h["role"] == "user" else ANIMALS[st.session_state.character]["name"]
            st.markdown(f"**{who}:** {h['text']}")


if __name__ == "__main__":
    main()
