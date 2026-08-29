import streamlit as st
from google import genai
from PIL import Image
import requests
from datetime import datetime

# ---------------- Page Config ----------------
st.set_page_config(page_title="જિરા સ્કૂલ વિશ્લેષણ", page_icon="🏫")
st.title("🏫 જિરા સ્કૂલમાંથી બાળકોને લખી અપેલ ૩૦ થી ૪૦ મુદ્દાનું વિશ્લેષણ")
st.write("બાળકોએ લખેલા મુદ્દાઓના ફોટા અપલોડ કરો અને એકસાથે વિશ્લેષણ મેળવો.")

# ---------------- Secrets ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except Exception:
    st.error("મહેરબાની કરીને Secrets સેટ કરો.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- Telegram મોકલવાનું ફંક્શન ----------------
def send_to_telegram(priority, student_name, std, file_names, analysis_text):
    message = f"""
🏫 *નવું રેસ્પોન્સ મળ્યું*

📅 તારીખ: {datetime.now().strftime("%d-%m-%Y %H:%M")}
🎯 પ્રાધાન્ય: {priority}
👶 બાળકનું નામ: {student_name}
📚 ધોરણ: {std}
📄 ફાઈલો: {file_names}

---------- એનાલિસિસ ----------
{analysis_text}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
        return True
    except Exception as e:
        st.error(f"Telegram મોકલવામાં ભૂલ: {e}")
        return False

# ---------------- ૧. પ્રાધાન્યનો પ્રશ્ન ----------------
st.subheader("૧. તમે શિક્ષણમાં શેનું પ્રાધાન્ય આપો છો?")

priority = st.radio(
    "પસંદ કરો:",
    ["પસંદ કરો", "📚 શિક્ષણ", "🏫 સુવિધા"],
    horizontal=True
)

# ---------------- ૨. વિદ્યાર્થીની વિગતો ----------------
if priority != "પસંદ કરો":
    st.subheader("૨. વિદ્યાર્થીની વિગતો")

    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("બાળકનું નામ *")

    with col2:
        std = st.selectbox("ધોરણ *", ["પસંદ કરો", "૬", "૭", "૮"])

    # ---------------- ૩. ફાઈલ અપલોડ ----------------
    if student_name and std != "પસંદ કરો":
        st.subheader("૩. ફોટો અપલોડ કરો")

        uploaded_files = st.file_uploader(
            "બાળકોએ લખેલા મુદ્દાઓના ફોટા અહીં અપલોડ કરો (એકસાથે ઘણા પણ સિલેક્ટ કરી શકો છો)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.write(f"**કુલ {len(uploaded_files)} ફાઈલ અપલોડ થઈ છે**")

            # બધા ફોટા બતાવો
            for i, uploaded_file in enumerate(uploaded_files):
                image = Image.open(uploaded_file)
                st.image(image, caption=f"ફોટો {i+1}: {uploaded_file.name}", use_container_width=True)

            if st.button("બધાનું એકસાથે એનાલિસિસ કરો 🚀"):

                prompt = """
                આ બધા ફોટામાં આપેલા તમામ મુદ્દાઓને ધ્યાનથી વાંચો અને તેને માત્ર ૩ કેટેગરીમાં વહેંચીને ટકાવારી (Percentage) સાથે ટૂંકું વિશ્લેષણ આપો:
                ૧. 📚 મૂળભૂત શિક્ષણ
                ૨. 🏫 શૈક્ષણિક સુવિધા
                ૩. 🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી

                જવાબ માત્ર આ ફોર્મેટમાં આપો:
                📚 મૂળભૂત શિક્ષણ: __ મુદ્દા — __%
                🏫 શૈક્ષણિક સુવિધા: __ મુદ્દા — __%
                🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી: __ મુદ્દા — __%

                પછી માત્ર ૪–૬ સરળ ગુજરાતી વાક્યોમાં સમજાવો કે બાળકના ભવિષ્ય માટે “મૂળભૂત શિક્ષણ” શા માટે સૌથી મહત્વનું છે.
                
                અંતે એક અસરકારક વાક્ય આપો:
                “સુવિધા બાળકને સગવડ આપે છે, પરંતુ ગુણવત્તાયુક્ત શિક્ષણ બાળકનું ભવિષ્ય ઘડે છે.”
                """

                with st.spinner("બધા ફોટાનું એકસાથે એનાલિસિસ થઈ રહ્યું છે..."):
                    try:
                        # બધા ફોટા એકસાથે મોકલો
                        images = [Image.open(f) for f in uploaded_files]
                        contents = [prompt] + images

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=contents
                        )

                        analysis_text = response.text

                        st.success("✅ બધા ફોટાનું એકસાથે એનાલિસિસ તૈયાર છે!")
                        st.markdown(analysis_text)
                        st.divider()

                        # ફાઈલ નામો
                        file_names = ", ".join([f.name for f in uploaded_files])

                        # Telegram પર મોકલો
                        sent = send_to_telegram(
                            priority=priority,
                            student_name=student_name,
                            std=std,
                            file_names=file_names,
                            analysis_text=analysis_text
                        )

                        if sent:
                            st.success("📱 રેસ્પોન્સ Telegram પર મોકલાઈ ગયું છે!")

                    except Exception as e:
                        st.error(f"ભૂલ: {e}")
