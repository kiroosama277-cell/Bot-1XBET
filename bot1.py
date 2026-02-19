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
st.set_page_config(page_title="المساعد الذكي لـ 1xBet", page_icon="🤖", layout="centered")

# ==========================================
# 🎨 التصميم الاحترافي (ألوان هادية وفقاعات)
# ==========================================
custom_css = """
<style>
/* إخفاء القوائم */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stSidebar"] {display: none;}

/* 1. خلفية الصفحة (رمادي فاتح جداً ومريح للعين) */
.stApp {
    background-color: #F2F5F8;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 2. شاشة الدخول الزجاجية */
.glass-box {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
    padding: 30px;
    text-align: center;
    direction: rtl;
    max-width: 400px;
    margin: 0 auto;
}

/* الإيموجي اللي بيلوح في شاشة الدخول */
.waving-hand {
    width: 120px;
    margin: 0 auto 15px auto;
    display: block;
}

/* 3. تنسيق فقاعات الشات (Bubbles) */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 20px !important;
}

/* فقاعة العميل (أبيض ناصع مع ظل خفيف) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #FFFFFF !important;
    border-radius: 20px 20px 0px 20px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.04) !important;
    padding: 15px 20px !important;
    direction: rtl; text-align: right;
    border: 1px solid #EAEAEA !important;
}

/* فقاعة البوت (رصاصي فاتح مريح) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #F8F9FA !important; 
    border-radius: 20px 20px 20px 0px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.04) !important;
    padding: 15px 20px !important;
    direction: rtl; text-align: right;
    border: 1px solid #E2E8F0 !important;
}

/* نصوص الشات */
.stMarkdown p {
    direction: rtl; 
    text-align: right; 
    font-size: 1.05rem !important; 
    color: #2C3E50 !important;
}

/* 4. مربع الكتابة */
.stChatInputContainer textarea {
    direction: rtl; text-align: right;
    border-radius: 25px !important;
    border: 1px solid #D1D9E6 !important;
    background-color: #FFFFFF !important;
    padding: 15px !important;
}

/* 5. العنوان */
.main-title {
    text-align: center;
    color: #1A365D;
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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

# ==========================================
# 🛑 الحماية وشاشة الدخول
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("<br><br>", unsafe_allow_html=True)
    
    # الصورة المتحركة (بتلوح) جوه شاشة الدخول بس
    st.markdown('<img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f44b_1f3fb/512.gif" class="waving-hand">', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-box">
            <h2 style="color:#2C3E50; margin-bottom:5px;">مرحباً بك 👋</h2>
            <p style="color:#7F8C8D; font-size:14px; margin-bottom:20px;">يرجى تسجيل الدخول للبدء</p>
    """, unsafe_allow_html=True)
    
    password_input = st.text_input("كلمة المرور", type="password", placeholder="أدخل الرمز السري...", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("دخول", use_container_width=True):
            if password_input == BOT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة ⛔")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# ✅ واجهة البوت (الشات الداخلي)
# ==========================================
# العنوان المظبوط
st.markdown('<div class="main-title">🤖 المساعد الذكي لـ 1xBet</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🧹 مسح المحادثة", use_container_width=True):
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

if prompt := st.chat_input("اكتب رسالتك هنا..."):
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
