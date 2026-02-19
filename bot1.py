import streamlit as st
import google.generativeai as genai
import csv
import os
import random
from datetime import datetime

# ==========================================
# 🔐 إعدادات
# ==========================================
BOT_PASSWORD = "12345"
HISTORY_FILE = "chat_history.csv"

# --- قائمة المفاتيح (هنسحبها كلها من الخزنة) ---
api_keys = []
if "KEY1" in st.secrets: api_keys.append(st.secrets["KEY1"])
if "KEY2" in st.secrets: api_keys.append(st.secrets["KEY2"])
if "KEY3" in st.secrets: api_keys.append(st.secrets["KEY3"])

if not api_keys:
    st.error("⛔ لا توجد مفاتيح في Secrets.")
    st.stop()

# دالة ذكية للتبديل بين المفاتيح
def get_response_smart(prompt, knowledge):
    # نجرب المفاتيح واحد واحد لحد ما واحد يشتغل
    for key in api_keys:
        try:
            genai.configure(api_key=key)
            # نختار موديل سريع
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            full_text = f"أنت موظف دعم فني. جاوب بناءً على هذا فقط:\n{knowledge}\nالسؤال: {prompt}"
            response = model.generate_content(full_text)
            return response.text # لو نجح يرجع الرد
            
        except Exception:
            continue # لو فشل، يجرب المفتاح اللي بعده فوراً
            
    return "عذراً، السيرفر مشغول جداً حالياً. يرجى المحاولة بعد دقيقة." # لو كلهم خلصوا

# إعداد الصفحة
st.set_page_config(page_title="مساعد 1xBet", page_icon="🔒", layout="centered")

# إخفاء العلامات
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stSidebar"] {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# حفظ المحادثة
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

# البوت
st.title("🤖 مساعد 1xBet الذكي")
col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🗑️ مسح الشات"):
        clear_chat()
        st.rerun()

st.success("أهلاً بك! النظام متصل بعدة سيرفرات لضمان السرعة. 🚀")

with st.expander("📂 لوحة التحكم (للمدير فقط)"):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "rb") as f:
            st.download_button("📥 تحميل سجل المحادثات", f, "chat_history.csv", "text/csv")
    else:
        st.info("لا توجد سجلات حالياً.")

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

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner('جاري الاتصال بالسيرفر...'):
        # هنا بننادي الدالة الذكية اللي بتبدل المفاتيح
        bot_reply = get_response_smart(prompt, knowledge_base)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.chat_message("assistant").write(bot_reply)
        save_chat(prompt, bot_reply)
