import streamlit as st
from groq import Groq
import csv
import os
from datetime import datetime

# ==========================================
# 🔐 إعدادات أساسية
# ==========================================
BOT_PASSWORD = "12345"
HISTORY_FILE = "chat_history.csv"

# الاتصال بـ Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⛔ لم يتم العثور على مفتاح Groq في Secrets.")
    st.stop()

# إعداد الصفحة
st.set_page_config(page_title="المساعد الذكي", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 التصميم الشامل (Soft UI & Clean Bubbles)
# ==========================================
custom_css = """
<style>
/* 1. إخفاء القوائم والعلامات المزعجة */
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important;}
header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stSidebar"] {display: none;}
[data-testid="stDecoration"] {display: none;}

/* 2. خلفية الصفحة (رمادي فاتح مريح جداً) */
.stApp {
    background-color: #F4F7F6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 3. تنسيق فقاعات الشات (كروت بيضاء ناعمة 3D) */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 20px !important;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.03) !important;
    padding: 15px 25px !important;
    margin-bottom: 20px !important;
    direction: rtl; 
    text-align: right;
}

/* تنسيق النصوص داخل الفقاعات */
[data-testid="stMarkdownContainer"] p {
    font-size: 1.1rem;
    color: #333333;
    line-height: 1.7;
}

/* 4. تنسيق مربع إدخال النص */
.stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 20px !important;
    border: 1px solid #D1D9E6 !important;
    box-shadow: inset 0px 2px 5px rgba(0,0,0,0.02) !important;
    background-color: #FFFFFF !important;
}

/* 5. شاشة الدخول (تصميم زجاجي) */
.glass-container {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 25px;
    border: 1px solid #EAEAEA;
    box-shadow: 0 8px 30px rgba(0,0,0,0.05);
    padding: 40px;
    text-align: center;
    direction: rtl;
    max-width: 450px;
    margin: 0 auto;
}

/* 6. الصورة المتحركة (الترحيب) */
.welcome-gif {
    display: block;
    margin: 0 auto;
    width: 140px;
    margin-bottom: 15px;
}

/* 7. تنسيق العناوين */
.main-title {
    text-align: center;
    color: #2C3E50;
    font-size: 2.2rem;
    font-weight: bold;
    margin-bottom: 30px;
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
# 🛑 شاشة الدخول (الترحيب + الباسورد)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    
    # الإيموجي المتحرك (تلويح) - مضمون 100%
    st.markdown('<img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f44b_1f3fb/512.gif" class="welcome-gif">', unsafe_allow_html=True)
    
    st.markdown('<h2 style="color:#2c3e50;">مرحباً بك 👋</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7f8c8d;">يرجى إدخال الرمز السري للبدء</p>', unsafe_allow_html=True)
    
    password_input = st.text_input("كلمة المرور", type="password", placeholder="أدخل الرمز هنا...", label_visibility="collapsed")
    
    if st.button("تسجيل الدخول", use_container_width=True):
        if password_input == BOT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("عذراً، الرمز غير صحيح ⛔")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# ✨ واجهة الشات الداخلية (البوت)
# ==========================================
st.markdown('<div class="main-title">🤖 المساعد الذكي</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح المحادثة", use_container_width=True):
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

# عرض الرسائل في الفقاعات البيضاء الناعمة
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
            # تجميع السياق
            conversation_history = ""
            for msg in st.session_state.messages[-4:]:
                conversation_history += f"{msg['role']}: {msg['content']}\n"

            system_instruction = f"""
            أنت مساعد ذكي ولطيف جداً ومصري لمنصة 1xBet.
            - تحدث باللهجة المصرية العامية المحترمة والودودة.
            - جاوب فقط بناءً على هذه المعلومات:
            {knowledge_base}
            - تذكر السياق التالي: {conversation_history}
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
