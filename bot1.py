import streamlit as st
from groq import Groq
import csv
import os
from datetime import datetime

# ==========================================
# 🔐 إعدادات
# ==========================================
BOT_PASSWORD = "12345"
HISTORY_FILE = "chat_history.csv"

# --- الاتصال بـ Groq ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⛔ لم يتم العثور على مفتاح Groq في Secrets.")
    st.stop()

# إعداد الصفحة
st.set_page_config(page_title="المساعد الذكي", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 التصميم الشامل (Soft Bubbles & Glassmorphism)
# ==========================================
custom_css = """
<style>
/* إخفاء القوائم */
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important;}
header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stSidebar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}

/* خلفية الصفحة (رمادي فاتح جداً مريح) */
.stApp {
    background-color: #F4F7F6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ------------------------------------- */
/* 🛑 تنسيق شاشة تسجيل الدخول */
/* ------------------------------------- */
.login-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 2rem;
}

/* الكائن الترحيبي في شاشة الدخول */
.welcome-gif {
    width: 150px;
    border-radius: 50%;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.glass-container {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 25px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    padding: 40px;
    text-align: center;
    direction: rtl;
    max-width: 400px;
    margin: 0 auto;
}

/* ------------------------------------- */
/* 💬 تنسيق فقاعات الشات (Chat Bubbles) */
/* ------------------------------------- */
/* إخفاء خلفية رسائل Streamlit الافتراضية */
.stChatMessage {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 15px !important;
}

/* رسالة المستخدم (العميل) - أبيض ناصع مع ظل خفيف */
[data-testid="chatAvatarIcon-user"] + div {
    background-color: #FFFFFF !important;
    border-radius: 20px 20px 0px 20px !important;
    padding: 12px 18px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    border: 1px solid #EAEAEA !important;
    color: #333333 !important;
    direction: rtl; text-align: right;
    display: inline-block;
    max-width: 85%;
}

/* رسالة البوت (المساعد) - رمادي فاتح مائل للأزرق الهادي */
[data-testid="chatAvatarIcon-assistant"] + div {
    background-color: #EBF2FA !important; 
    border-radius: 20px 20px 20px 0px !important;
    padding: 12px 18px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    border: 1px solid #D6E4F0 !important;
    color: #2C3E50 !important;
    direction: rtl; text-align: right;
    display: inline-block;
    max-width: 85%;
}

/* إخفاء صورة الأفاتار الافتراضية عشان شكل الفقاعة يبان أنظف (اختياري) */
/* [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none; } */

/* ------------------------------------- */
/* ✍️ تنسيق المدخلات والأزرار */
/* ------------------------------------- */
.stMarkdown p {direction: rtl; text-align: right; line-height: 1.6; margin-bottom: 0;}
h1, h2, h3 {direction: rtl; text-align: right; color: #2C3E50;}

.stTextInput input, .stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 25px !important;
    border: 1px solid #D1D9E6 !important;
    box-shadow: inset 0px 2px 5px rgba(0,0,0,0.02) !important;
    padding: 12px 20px !important;
    background-color: #FFFFFF !important;
}

div.stButton > button:first-child {
    background-color: #FFFFFF;
    color: #556EE6;
    border-radius: 25px;
    border: 1px solid #EAEAEA;
    font-weight: bold;
    padding: 8px 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}
div.stButton > button:first-child:hover {
    background-color: #556EE6;
    color: #FFFFFF;
    box-shadow: 0px 6px 15px rgba(85,110,230,0.3);
}

.chat-title {
    text-align: center;
    color: #2C3E50;
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 5px;
}
.chat-subtitle {
    text-align: center;
    color: #7F8C8D;
    font-size: 1rem;
    margin-bottom: 30px;
}

/* لوجو الشات الداخلي (صغير) */
.inner-logo {
    display: block;
    margin: 0 auto;
    width: 60px;
    margin-bottom: 10px;
    opacity: 0.8;
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
# 🛑 شاشة الدخول (فيها الـ GIF الترحيبي)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    # الـ GIF الترحيبي برة بس
    st.markdown('<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjRmMjMyYjM5NjFkMzBhNjU5ZTk1MWNmYmRhNTE4ZjQ3NzZjYzJlZiZlcD12MV9pbnRlcm5hbF9naWZzX3NlYXJjaCZjdD1n/ASd0Ukj0y3qMM/giphy.gif" class="welcome-gif">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-container">
            <h2 style="color:#2c3e50; margin-bottom: 5px;">مرحباً بك مجدداً 👋</h2>
            <p style="color:#7f8c8d; margin-bottom: 20px; font-size: 0.9rem;">يرجى تسجيل الدخول للوصول للمساعد الذكي</p>
    """, unsafe_allow_html=True)
    
    password_input = st.text_input("كلمة المرور", type="password", placeholder="أدخل الرمز السري هنا...", label_visibility="collapsed")
    
    st.write("") 
    if st.button("تسجيل الدخول", use_container_width=True):
        if password_input == BOT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("عذراً، كلمة المرور غير صحيحة ⛔")
            
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# ✨ واجهة الشات الداخلية (البوت)
# ==========================================
# لوجو صغير جوه الشات بدل الـ GIF
st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/1XBET_Logo.png" class="inner-logo">', unsafe_allow_html=True)

st.markdown('<div class="chat-title">المساعد الذكي ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">أنا هنا للإجابة على استفساراتك حول منصة 1xBet</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح محادثة اليوم", use_container_width=True):
        clear_chat()

st.write("") # مسافة

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

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل في فقاعات ملونة
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
            # تجميع السياق عشان يفتكر الكلام
            conversation_history = ""
            for msg in st.session_state.messages[-4:]:
                conversation_history += f"{msg['role']}: {msg['content']}\n"

            system_instruction = f"""
            أنت مساعد ذكي ولطيف جداً ومصري لمنصة 1xBet.
            - تحدث باللهجة المصرية العامية المحترمة والودودة.
            - جاوب فقط بناءً على هذه المعلومات:
            {knowledge_base}
            
            - سياق الكلام السابق (للتذكر):
            {conversation_history}
            
            - السؤال الحالي: {prompt}
            """
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            bot_reply = chat_completion.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant", avatar="🤖"):
                st.write(bot_reply)
            
            save_chat(prompt, bot_reply)
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
