import streamlit as st
import google.generativeai as genai
import csv
import os
from datetime import datetime

# ==========================================
# 🔐 إعدادات أساسية
# ==========================================
BOT_PASSWORD = "12345"
HISTORY_FILE = "chat_history.csv"

# الاتصال بجوجل (من الخزنة)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⛔ لم يتم العثور على مفتاح Google في Secrets.")
    st.stop()

# إعداد الصفحة (بدون شريط جانبي)
st.set_page_config(page_title="المساعد الذكي", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 التصميم الشامل (Soft UI / Neumorphism) + الزجاج
# ==========================================
custom_css = """
<style>
/* 1. إخفاء قوائم Streamlit الافتراضية تماماً */
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important;}
header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stSidebar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}

/* 2. خلفية الصفحة (تدرج لوني هادي ومريح جداً للعين) */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 3. تنسيق شاشة الدخول (تأثير الزجاج - Glassmorphism) */
.glass-container {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    padding: 40px;
    text-align: center;
    margin-top: 50px;
    direction: rtl;
}

/* 4. تنسيق فقاعات الشات (Soft UI / Neumorphism) */
/* رسالة العميل (أبيض مع ظل) */
[data-testid="chatAvatarIcon-user"] + div {
    background-color: #ffffff !important;
    border-radius: 20px 20px 0px 20px !important;
    padding: 15px !important;
    box-shadow: 5px 5px 15px #d1d9e6, -5px -5px 15px #ffffff !important;
    border: none !important;
    color: #4a4a4a !important;
    direction: rtl; text-align: right;
    margin-bottom: 10px;
}

/* رسالة البوت (أزرق باستيل هادي مع ظل) */
[data-testid="chatAvatarIcon-assistant"] + div {
    background-color: #e8f4f8 !important; 
    border-radius: 20px 20px 20px 0px !important;
    padding: 15px !important;
    box-shadow: 5px 5px 15px #d1d9e6, -5px -5px 15px #ffffff !important;
    border: none !important;
    color: #2c3e50 !important;
    direction: rtl; text-align: right;
    margin-bottom: 10px;
}

/* 5. تنسيق عام للنصوص العربية */
.stMarkdown p {direction: rtl; text-align: right; line-height: 1.6;}
h1, h2, h3 {direction: rtl; text-align: right; color: #2c3e50;}

/* 6. تنسيق مربع إدخال النص (دائري وناعم) */
.stTextInput input, .stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 30px !important;
    border: none !important;
    box-shadow: inset 5px 5px 10px #d1d9e6, inset -5px -5px 10px #ffffff !important;
    padding: 15px 20px !important;
    background-color: #f5f7fa !important;
    color: #4a4a4a !important;
}

/* 7. تنسيق الأزرار (ناعمة و 3D) */
div.stButton > button:first-child {
    background-color: #f5f7fa;
    color: #556ee6;
    border-radius: 30px;
    border: none;
    font-weight: bold;
    padding: 10px 25px;
    box-shadow: 5px 5px 10px #d1d9e6, -5px -5px 10px #ffffff;
    transition: all 0.2s ease;
}
div.stButton > button:first-child:hover {
    box-shadow: inset 5px 5px 10px #d1d9e6, inset -5px -5px 10px #ffffff;
    color: #3b50ce;
}

/* 8. العنوان الترحيبي في الشات */
.chat-title {
    text-align: center;
    color: #556ee6;
    font-size: 2.2rem;
    font-weight: bold;
    margin-bottom: 5px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
}
.chat-subtitle {
    text-align: center;
    color: #8c98a4;
    font-size: 1.1rem;
    margin-bottom: 30px;
}

/* 9. الصورة المتحركة (الترحيب) */
.welcome-gif {
    display: block;
    margin: 0 auto;
    width: 150px;
    border-radius: 50%;
    margin-bottom: 20px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 💾 دوال الحفظ والمسح
# ==========================================
def save_chat(question, answer):
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["التاريخ", "الوقت", "السؤال", "الرد"])
        now = datetime.now()
        writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), question, answer])

def clear_chat():
    st.session_state.messages = []
    st.rerun()

# ==========================================
# 🛑 شاشة الدخول (تأثير الزجاج)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # رسم الصندوق الزجاجي
    st.markdown("""
        <div class="glass-container">
            <h2 style="text-align:center; color:#2c3e50;">مرحباً بك في المساعد الذكي</h2>
            <p style="text-align:center; color:#7f8c8d;">يرجى تسجيل الدخول للوصول إلى النظام</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # مسافة
    password_input = st.text_input("🔑 كلمة المرور:", type="password", placeholder="أدخل الرمز السري هنا...")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2: 
        if st.button("تسجيل الدخول", use_container_width=True):
            if password_input == BOT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("عذراً، كلمة المرور غير صحيحة ⛔")
    st.stop()

# ==========================================
# ✨ واجهة البوت (Soft UI)
# ==========================================
# صورة الكائن اللطيف (GIF) بيلوح
st.markdown('<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjRmMjMyYjM5NjFkMzBhNjU5ZTk1MWNmYmRhNTE4ZjQ3NzZjYzJlZiZlcD12MV9pbnRlcm5hbF9naWZzX3NlYXJjaCZjdD1n/ASd0Ukj0y3qMM/giphy.gif" class="welcome-gif">', unsafe_allow_html=True)

# العناوين
st.markdown('<div class="chat-title">المساعد الذكي 1xBet ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">مرحباً! أنا هنا للإجابة على جميع استفساراتك.</div>', unsafe_allow_html=True)

# زرار مسح الشات
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح الشات", use_container_width=True):
        clear_chat()

st.divider()

# --- قاعدة المعرفة ---
knowledge_base = """
كيفية ربط بريد إلكتروني على منصة 1xBet:
1. نضغط القائمة > الملف الشخصي > ربط بجانب البريد الإلكتروني.
2. نكتب الإيميل ونضغط إرسال رمز التحقق.
3. نحل الكابتشا، وسيصل كود للتفعيل على الإيميل.
4. ننسخ الكود ونضعه في الخانة ونضغط تفعيل.

أسباب رفض ربط البريد:
1. الإيميل مسجل بحساب آخر: يظهر خطأ "حدث خطأ ما". الحل: استخدام إيميل جديد.
2. عدم وصول الكود: تأكد من الرسائل غير المرغوب فيها (Spam). حاول مرة أخرى، أو تواصل مع الدعم.

رهان محظوظ (Lucky Bet):
- هو دمج بين الرهان الأحادي والاكسبريس.
- يمكن وضع من 2 لـ 8 أحداث.
- الميزة: لو حدث واحد فقط كسب، ستحصل على عائد (مش لازم كله يكسب).
"""

# عرض الرسائل
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

if prompt := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    with st.spinner('جاري كتابة الرد... ✨'):
        try:
            available_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_model = m.name
                    break
            
            if available_model:
                model = genai.GenerativeModel(available_model)
                
                system_instruction = f"""
                أنت مساعد ذكي ولطيف جداً ومصري لمنصة 1xBet.
                - تحدث باللهجة المصرية العامية المحترمة والودودة.
                - جاوب فقط بناءً على هذه المعلومات:
                {knowledge_base}
                - السؤال الحالي: {prompt}
                """
                
                response = model.generate_content(system_instruction)
                bot_reply = response.text
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(bot_reply)
                
                save_chat(prompt, bot_reply)
            else:
                st.error("عذراً، الخدمة مشغولة حالياً.")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}"