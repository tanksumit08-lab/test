import streamlit as st
from google import genai
from PIL import Image

# 1. સાઇટનું ટાઇટલ
st.set_page_config(page_title="સ્કૂલ એનાલિસિસ ટૂલ", page_icon="🏫")
st.title("🏫 સ્કૂલ કામગીરી પત્રક એનાલિસિસ ટૂલ")
st.write("તમારા સ્કૂલના લિસ્ટ કે પત્રકનો ફોટો અપલોડ કરો અને ટૂંકમાં વિશ્લેષણ મેળવો.")

# 2. API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("મહેરબાની કરીને Gemini API Key સેટ કરો.")
    st.stop()

# નવું Client બનાવો
client = genai.Client(api_key=api_key)

# 3. મલ્ટીપલ ફાઈલ અપલોડ
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
        આ ફોટામાં આપેલા તમામ મુદ્દાઓને ધ્યાનથી વાંચો અને તેને માત્ર 3 કેટેગરીમાં વહેંચીને ટકાવારી (Percentage) સાથે ટૂંકું વિશ્લેષણ આપો:
        1. 📚 મૂળભૂત શિક્ષણ
        2. 🏫 શૈક્ષણિક સુવિધા
        3. 🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી

        જવાબ માત્ર આ ફોર્મેટમાં આપો:
        📚 મૂળભૂત શિક્ષણ: __ મુદ્દા — __%
        🏫 શૈક્ષણિક સુવિધા: __ મુદ્દા — __%
        🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી: __ મુદ્દા — __%

        પછી માત્ર 4–6 સરળ ગુજરાતી વાક્યોમાં સમજાવો કે બાળકના ભવિષ્ય માટે “મૂળભૂત શિક્ષણ” શા માટે સૌથી મહત્વનું છે.
        
        અંતે એક અસરકારક વાક્ય આપો:
        “સુવિધા બાળકને સગવડ આપે છે, પરંતુ ગુણવત્તાયુક્ત શિક્ષણ બાળકનું ભવિષ્ય ઘડે છે.”
        """

        for i, uploaded_file in enumerate(uploaded_files):
            with st.spinner(f"ફોટો {i+1} નું એનાલિસિસ થઈ રહ્યું છે..."):
                try:
                    image = Image.open(uploaded_file)
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[prompt, image]
                    )
                    
                    st.success(f"✅ ફોટો {i+1} ({uploaded_file.name}) નું એનાલિસિસ તૈયાર છે!")
                    st.markdown(response.text)
                    st.divider()
                    
                except Exception as e:
                    st.error(f"ફોટો {i+1} માં ભૂલ: {e}")
