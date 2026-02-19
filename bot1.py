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
st.set_page_config(page_title="مساعد 1xBet", page_icon="🔒", layout="centered")

# إخفاء العلامات + تنسيق عربي
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stSidebar"] {display: none;}
            .stChatMessage {direction: rtl; text-align: right;}
            .stTextInput input {direction: rtl; text-align: right;}
            .stMarkdown p {direction: rtl; text-align: right;}
            h1, h2, h3 {direction: rtl; text-align: right;}
            .title-text {direction: rtl; text-align: right; font-size: 2.5rem; font-weight: bold;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
    st.session_state.messages = []
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
st.markdown('<div class="title-text">🤖 المساعد الذكي لمنصة 1xBet</div>', unsafe_allow_html=True)

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🗑️ مسح الشات"):
        clear_chat()

st.success("مرحباً! كيف يمكنني مساعدتك اليوم؟ ✅")

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

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner('جاري الرد...'):
        try:
            # تجميع المحادثة السابقة
            conversation_history = ""
            for msg in st.session_state.messages[-4:]: 
                conversation_history += f"{msg['role']}: {msg['content']}\n"

            # تعليمات صارمة جداً للغة
            system_instruction = f"""
            تعليمات صارمة (Strict Instructions):
            1. أنت موظف خدمة عملاء مصري لمنصة 1xBet.
            2. تحدث **فقط** باللهجة المصرية العامية المحترمة.
            3. **ممنوع منعاً باتاً** الكتابة باللغة الإنجليزية (إلا عند ذكر اسم المنصة "1xBet" فقط).
            4. تأكد أن الجمل العربية مرتبة وصحيحة ومفيدة.
            5. لا تقم بتأليف معلومات غير موجودة في النص المرفق.
            
            معلوماتك (المصدر الوحيد):
            {knowledge_base}
            
            سياق المحادثة السابقة:
            {conversation_history}
            
            السؤال الحالي: {prompt}
            الرد (باللهجة المصرية فقط):
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3, # تقليل الإبداع عشان يلتزم بالنص
            )
            bot_reply = chat_completion.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.chat_message("assistant").write(bot_reply)
            save_chat(prompt, bot_reply)
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
