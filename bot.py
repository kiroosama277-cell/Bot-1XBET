import streamlit as st
import google.generativeai as genai

# --- مفتاحك الحقيقي ---
my_secret_key = "AIzaSyCvVoS1Miq83dVhLCNAApAKBnx7iArMLH0"

st.set_page_config(page_title="مساعد 1xBet", page_icon="🤖")
st.title("🤖 مساعد 1xBet الذكي")

# --- المعلومات ---
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

# --- الكود الذكي لاختيار الموديل تلقائياً ---
try:
    genai.configure(api_key=my_secret_key)
    
    # البحث عن موديل متاح
    available_model = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_model = m.name
            break
    
    if available_model:
        # استخدام الموديل اللي لقيناه
        model = genai.GenerativeModel(available_model)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("اكتب سؤالك هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            full_prompt = f"أنت موظف دعم فني. جاوب بناءً على هذا فقط:\n{knowledge_base}\nالسؤال: {prompt}"
            
            with st.spinner('جاري التفكير...'):
                response = model.generate_content(full_prompt)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.chat_message("assistant").write(response.text)
    else:
        st.error("لم يتم العثور على أي موديل متاح في هذا الحساب.")

except Exception as e:
    st.error(f"حدث خطأ: {e}")
