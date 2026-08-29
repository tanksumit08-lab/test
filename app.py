import streamlit as st
from google import genai
from PIL import Image
import pandas as pd
from io import BytesIO
from datetime import datetime

# ---------------- Page Config ----------------
st.set_page_config(page_title="સ્કૂલ એનાલિસિસ ટૂલ", page_icon="🏫")
st.title("🏫 સ્કૂલ કામગીરી પત્રક એનાલિસિસ ટૂલ")
st.write("તમારા સ્કૂલના લિસ્ટ કે પત્રકનો ફોટો અપલોડ કરો અને ટૂંકમાં વિશ્લેષણ મેળવો.")

# ---------------- API Key ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("મહેરબાની કરીને Gemini API Key સેટ કરો.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- Session State ----------------
if "records" not in st.session_state:
    st.session_state.records = []

# ---------------- ૧. પ્રાધાન્યનો પ્રશ્ન ----------------
st.subheader("૧. તમે શિક્ષણમાં શેનું પ્રાધાન્ય આપો છો?")

priority = st.radio(
    "પસંદ કરો:",
    ["પસંદ કરો", "📚 શિક્ષણ", "🏫 સુવિધા"],
    horizontal=True
)

# ---------------- ૨. વિદ્યાર્થીની વિગતો (પ્રાધાન્ય પસંદ કર્યા પછી જ) ----------------
if priority != "પસંદ કરો":
    st.subheader("૨. વિદ્યાર્થીની વિગતો")

    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("બાળકનું નામ *")

    with col2:
        std = st.selectbox("ધોરણ *", ["પસંદ કરો", "૬", "૭", "૮"])

    # ---------------- ૩. ફાઈલ અપલોડ (નામ અને ધોરણ ભર્યા પછી જ) ----------------
    if student_name and std != "પસંદ કરો":
        st.subheader("૩. ફોટો અપલોડ કરો")

        uploaded_files = st.file_uploader(
            "શાળાની કામગીરીની યાદીના ફોટા અહીં અપલોડ કરો (એકસાથે ઘણા પણ સિલેક્ટ કરી શકો છો)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.write(f"**કુલ {len(uploaded_files)} ફાઈલ અપલોડ થઈ છે**")

            for i, uploaded_file in enumerate(uploaded_files):
                image = Image.open(uploaded_file)
                st.image(image, caption=f"ફોટો {i+1}: {uploaded_file.name}", use_container_width=True)

            if st.button("બધાનું એનાલિસિસ કરો 🚀"):

                prompt = """
                આ ફોટામાં આપેલા તમામ મુદ્દાઓને ધ્યાનથી વાંચો અને તેને માત્ર ૩ કેટેગરીમાં વહેંચીને ટકાવારી (Percentage) સાથે ટૂંકું વિશ્લેષણ આપો:
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

                for i, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(f"ફોટો {i+1} નું એનાલિસિસ થઈ રહ્યું છે..."):
                        try:
                            image = Image.open(uploaded_file)

                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=[prompt, image]
                            )

                            analysis_text = response.text

                            st.success(f"✅ ફોટો {i+1} ({uploaded_file.name}) નું એનાલિસિસ તૈયાર છે!")
                            st.markdown(analysis_text)
                            st.divider()

                            # બધું Excel માટે સેવ કરો
                            st.session_state.records.append({
                                "તારીખ": datetime.now().strftime("%d-%m-%Y %H:%M"),
                                "પ્રાધાન્ય": priority,
                                "બાળકનું નામ": student_name,
                                "ધોરણ": std,
                                "ફાઈલનું નામ": uploaded_file.name,
                                "એનાલિસિસ": analysis_text
                            })

                        except Exception as e:
                            st.error(f"ફોટો {i+1} માં ભૂલ: {e}")

# ---------------- Excel ડાઉનલોડ ----------------
if st.session_state.records:
    st.subheader("📊 સેવ થયેલ બધા રેસ્પોન્સ")

    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Analysis")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Excel ડાઉનલોડ કરો",
        data=excel_data,
        file_name=f"School_Analysis_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
