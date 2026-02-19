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
st.set_page_config(page_title="المساعد الذكي 1xBet", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 التصميم الاحترافي الشامل (CSS)
# ==========================================
custom_css = """
<style>
/* إخفاء القوائم الافتراضية */
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important;}
header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stSidebar"] {display: none;}
[data-testid="stDecoration"] {display: none;}

/* 🌟 خلفية احترافية متطورة (تدرج لوني ناعم جداً مريح للعين) */
.stApp {
    background-color: #f0f4f8;
    background-image: radial-gradient(circle at 100% 0%, #dbe9f4 0%, transparent 50%), 
                      radial-gradient(circle at 0% 100%, #e1eaf2 0%, transparent 50%);
    background-attachment: fixed;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 💬 تنسيق فقاعات الشات */
/* إزالة الخلفية الافتراضية المزعجة */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* 1. فقاعة العميل (أبيض ناصع مع ظل 3D) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #FFFFFF !important;
    border-radius: 20px 20px 0px 20px !important;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.06) !important;
    border: 1px solid #ececec !important;
    padding: 15px 25px !important;
    margin-bottom: 20px !important;
    direction: rtl; text-align: right;
}

/* 2. فقاعة البوت (رصاصي فاتح / ثلجي مع ظل 3D) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #F4F6F9 !important; 
    border-radius: 20px 20px 20px 0px !important;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.06) !important;
    border: 1px solid #e2e8f0 !important;
    padding: 15px 25px !important;
    margin-bottom: 20px !important;
    direction: rtl; text-align: right;
}

/* تنسيق النصوص داخل الفقاعات */
.stMarkdown p {
    direction: rtl; text-align: right; 
    font-size: 1.1rem !important; 
    color: #2c3e50 !important; 
    line-height: 1.7 !important;
}

/* ✍️ تنسيق مربع الإدخال */
.stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 25px !important;
    border: 2px solid #D1D9E6 !important;
    background-color: #FFFFFF !important;
    padding: 15px !important;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.05) !important;
}

/* 🎛️ تنسيق الأزرار (تسجيل الدخول ومسح الشات) */
div.stButton > button:first-child {
    background-color: #ffffff;
    color: #3182ce;
    border-radius: 25px;
    border: 1px solid #D1D9E6;
    font-weight: bold;
    padding: 10px 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    transition: all 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: #3182ce;
    color: #ffffff;
    border-color: #3182ce;
}

/* 📌 العناوين */
.main-title {
    text-align: center;
    color: #1a365d;
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 20px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
.welcome-gif {
    display: block;
    margin: 0 auto;
    width: 130px;
    margin-bottom: 20px;
    border-radius: 50%;
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
# 🛑 شاشة الدخول
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("<br><br>", unsafe_allow_html=True)
    
    # الصورة الترحيبية (بتلوح)
    st.markdown('<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjRmMjMyYjM5NjFkMzBhNjU5ZTk1MWNmYmRhNTE4ZjQ3NzZjYzJlZiZlcD12MV9pbnRlcm5hbF9naWZzX3NlYXJjaCZjdD1n/ASd0Ukj0y3qMM/giphy.gif" class="welcome-gif">', unsafe_allow_html=True)
    
    st.markdown('<h2 style="text-align:center; color:#2c3e50;">مرحباً بك 👋</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#7f8c8d;">يرجى إدخال الرمز السري للبدء</p>', unsafe_allow_html=True)
    
    password_input = st.text_input("كلمة المرور", type="password", placeholder="الرمز السري...", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2: 
        if st.button("تسجيل الدخول", use_container_width=True):
            if password_input == BOT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("عذراً، الرمز غير صحيح ⛔")
    st.stop()

# ==========================================
# ✨ واجهة الشات الداخلية (البوت)
# ==========================================
st.markdown('<div class="main-title">🤖 المساعد الذكي 1xBet</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح المحادثة", use_container_width=True):
        clear_chat()

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
- مثال: 4 أحداث برهان 150 جنيه. يقسم النظام المبلغ على 15 رهان مختلف.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل (Streamlit هيستخدم الأيقونات الافتراضية عشان الكود يقدر يلونها)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
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
            - سياق الكلام السابق: {conversation_history}
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
            with st.chat_message("assistant"):
                st.write(bot_reply)
            
            save_chat(prompt, bot_reply)
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
