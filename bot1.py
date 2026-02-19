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
st.set_page_config(page_title="المساعد الذكي لـ 1xBet", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

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
    max-width: 450px;
    margin-left: auto;
    margin-right: auto;
}

/* 4. تنسيق فقاعات الشات (Soft UI) */
/* رسالة العميل (أبيض مع ظل) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #ffffff !important;
    border-radius: 20px 20px 0px 20px !important;
    padding: 15px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.03) !important;
    border: 1px solid #EAEAEA !important;
    color: #4a4a4a !important;
    direction: rtl; text-align: right;
    margin-bottom: 10px;
}

/* رسالة البوت (أزرق باستيل هادي مع ظل) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #F0F2F5 !important; 
    border-radius: 20px 20px 20px 0px !important;
    padding: 15px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.03) !important;
    border: 1px solid #E2E8F0 !important;
    color: #2c3e50 !important;
    direction: rtl; text-align: right;
    margin-bottom: 10px;
}

/* 5. تنسيق عام للنصوص العربية */
.stMarkdown p {direction: rtl; text-align: right; line-height: 1.6; font-size: 1.1rem !important;}
h1, h2, h3 {direction: rtl; text-align: right; color: #2c3e50;}

/* 6. تنسيق مربع إدخال النص (دائري وناعم) */
.stTextInput input, .stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 30px !important;
    border: 1px solid #D1D9E6 !important;
    box-shadow: inset 2px 2px 5px rgba(0,0,0,0.02) !important;
    padding: 15px 20px !important;
    background-color: #ffffff !important;
    color: #4a4a4a !important;
}

/* 7. تنسيق الأزرار (ناعمة) */
div.stButton > button:first-child {
    background-color: #ffffff;
    color: #556ee6;
    border-radius: 30px;
    border: 1px solid #D1D9E6;
    font-weight: bold;
    padding: 10px 25px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}
div.stButton > button:first-child:hover {
    background-color: #556ee6;
    color: #ffffff;
    box-shadow: 0px 6px 15px rgba(85,110,230,0.3);
}

/* 8. العناوين الداخلية */
.chat-title {
    text-align: center;
    color: #1a365d;
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 5px;
    direction: ltr; /* لضمان عدم تداخل الأرقام والإنجليزية */
}
.chat-subtitle {
    text-align: center;
    color: #8c98a4;
    font-size: 1.1rem;
    margin-bottom: 30px;
}

/* 9. الصورة المتحركة (الترحيب في شاشة الدخول فقط) */
.welcome-gif {
    display: block;
    margin: 0 auto;
    width: 140px;
    margin-bottom: 15px;
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
    
    # الإيموجي المتحرك (تلويح) يظهر هنا فقط
    st.markdown('<img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f44b_1f3fb/512.gif" class="welcome-gif">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-container">
            <h2 style="text-align:center; color:#2c3e50;">مرحباً بك 👋</h2>
            <p style="text-align:center; color:#7f8c8d; font-size:14px;">يرجى إدخال الرمز السري للبدء</p>
    """, unsafe_allow_html=True)
    
    password_input = st.text_input("كلمة المرور", type="password", placeholder="الرمز السري...", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2: 
        if st.button("تسجيل الدخول", use_container_width=True):
            if password_input == BOT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("عذراً، الرمز غير صحيح ⛔")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# ✨ واجهة البوت
# ==========================================
# العنوان الصحيح الذي لا يتداخل
st.markdown('<div class="chat-title">المساعد الذكي لـ 1xBet 🤖</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح المحادثة", use_container_width=True):
        clear_chat()

st.write("") # مسافة للترتيب

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

# عرض الرسائل بالأيقونات الصحيحة
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

            # 🛑 التعليمات الصارمة جداً للمصري
            system_instruction = f"""
            تعليمات صارمة جداً (Strict Instructions):
            1. أنت موظف خدمة عملاء مصري لمنصة 1xBet.
            2. تحدث **فقط** باللهجة المصرية العامية الودودة والمحترمة.
            3. **ممنوع منعاً باتاً** استخدام اللغة الإنجليزية أو الفصحى المعقدة (يسمح فقط بكتابة 1xBet).
            4. أجب بناءً على المعلومات التالية فقط ولا تقم بتأليف أي شيء:
            {knowledge_base}
            
            سياق المحادثة السابقة:
            {conversation_history}
            
            السؤال الحالي: {prompt}
            الرد (بالمصري فقط):
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2, # لضمان عدم التأليف والالتزام بالنص
            )
            bot_reply = chat_completion.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant", avatar="🤖"):
                st.write(bot_reply)
            
            save_chat(prompt, bot_reply)
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
