import streamlit as st
import google.generativeai as genai

# ==========================================
# 🔐 إعدادات كلمة المرور
# ==========================================
BOT_PASSWORD = "12345"  # غيري الرقم ده للباسورد اللي تحبيها

# --- مفتاحك الحقيقي الجديد ---
my_secret_key = "AIzaSyBTdcwG8iLiyMmjTUuB9juvYThWHJC9fzg"

# إعداد الصفحة
st.set_page_config(page_title="مساعد 1xBet", page_icon="🔒", layout="centered")

# ==========================================
# 🚫 كود إخفاء العلامات المائية والقوائم (لزيادة الخصوصية)
# ==========================================
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

# ==========================================
# 🛑 نظام الحماية (تسجيل الدخول)
# ==========================================
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
# ✅ هنا يبدأ البوت (بعد الدخول الصحيح)
# ==========================================
st.title("🤖 مساعد 1xBet الذكي")
st.success("أهلاً بك! أنت الآن متصل بأمان. ✅")

# المعلومات
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
- لو كسب حدث واحد (مثلاً معامله 1.5)، العائد يكون 15 جنيه.
- لو كسبت كل الأحداث، العائد يكون كبيراً جداً.
"""

# تشغيل الذكاء الاصطناعي
try:
    genai.configure(api_key=my_secret_key)
    
    # البحث الذكي عن الموديل
    available_model = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_model = m.name
            break
            
    if available_model:
        model = genai.GenerativeModel(available_model)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("اكتب سؤالك هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            full_prompt = f"أنت موظف دعم فني. جاوب بناءً على هذا فقط:\n{knowledge_base}\nالسؤال: {prompt}
