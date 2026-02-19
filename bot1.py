import streamlit as st
import google.generativeai as genai
import csv
import os
from datetime import datetime
from streamlit_session_browser_storage import SessionStorage

# ==========================================
# 🔐 إعدادات
# ==========================================
BOT_PASSWORD = "12345"
HISTORY_FILE = "chat_history.csv"

# --- الاتصال بجوجل ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⛔ لم يتم العثور على مفتاح Google في Secrets.")
    st.stop()

# إعداد الصفحة
st.set_page_config(page_title="المساعد الذكي", page_icon="🔒", layout="centered")

# إخفاء العلامات + تنسيق عربي كامل
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stSidebar"] {display: none;}
            
            /* تنسيق النصوص العربية */
            .stChatMessage {direction: rtl; text-align: right;}
            .stTextInput input {direction: rtl; text-align: right;}
            .stMarkdown p {direction: rtl; text-align: right;}
            h1, h2, h3 {direction: rtl; text-align: right;}
            
            /* ضبط العنوان عشان ميتلخبطش */
            .title-text {
                direction: rtl; 
                text-align: right;
                font-size: 2.5rem;
                font-weight: bold;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- استرجاع الشات ---
session = SessionStorage()
if "messages" not in session:
    session["messages"] = []

# دوال الحفظ والمسح
def save_chat(question, answer):
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["التاريخ", "الوقت", "السؤال", "الرد"])
        now = datetime.now()
        writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), question, answer])

def clear_chat():
    session["messages"] = []
    st.rerun()

# الحماية
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 تسجيل الدخول")
    password_input = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("دخول"):
        if password_input == BOT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة ⛔")
    st.stop()

# ==========================================
# ✅ واجهة البوت
# ==========================================
# العنوان المظبوط (بدون لخبطة)
st.markdown('<div class="title-text">🤖 المساعد الذكي لمنصة 1xBet</div>', unsafe_allow_html=True)

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🗑️ مسح الشات"):
        clear_chat()

st.success("أهلاً بك! المحادثة محفوظة تلقائياً ✅")

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
for msg in session["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    session["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner('جاري التحليل...'):
        try:
            available_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_model = m.name
                    break
            
            if available_model:
                model = genai.GenerativeModel(available_model)
                full_text = f"أنت موظف دعم فني. جاوب فقط بناءً على المعلومات التالية:\n{knowledge_base}\nالسؤال: {prompt}"
                response = model.generate_content(full_text)
                bot_reply = response.text
                
                session["messages"].append({"role": "assistant", "content": bot_reply})
                st.chat_message("assistant").write(bot_reply)
                save_chat(prompt, bot_reply)
                
                # حفظ في المتصفح
                session.save()
            else:
                st.error("عذراً، الخدمة مشغولة حالياً.")
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
