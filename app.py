import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. સાઇટનું ટાઇટલ અને હેડિંગ
st.set_page_config(page_title="સ્કૂલ એનાલિસિસ ટૂલ", page_icon="🏫")
st.title("🏫 સ્કૂલ કામગીરી પત્રક એનાલિસિસ ટૂલ")
st.write("તમારા સ્કૂલના લિસ્ટ કે પત્રકનો ફોટો અપલોડ કરો અને ટૂંકમાં વિશ્લેષણ મેળવો.")

# 2. Gemini API Key સેટअप (અહીં તમારી API Key મૂકવી અથવા Streamlit Secrets નો ઉપયોગ કરવો)
# st.secrets ["GEMINI_API_KEY"] નો ઉપયોગ કરવો વધારે સુરક્ષિત છે.
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("મહેરબાની કરીને Gemini API Key સેટ કરો.")
    st.stop()

genai.configure(api_key=api_key)

# 3. ફાઈલ અપલોડર
uploaded_file = st.file_uploader("શાળાની કામગીરીની યાદીનો ફોટો અહીં અપલોડ કરો (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # અપલોડ કરેલો ફોટો બતાવો
    image = Image.open(uploaded_file)
    st.image(image, caption="અપલોડ કરેલ ફોટો", use_column_width=True)
    
    if st.button("એનાલિસિસ કરો 🚀"):
        with st.spinner("એનાલિસિસ થઈ રહ્યું છે, કૃપા કરીને રાહ જુઓ..."):
            try:
                # Gemini 1.5 Flash મોડેલનો ઉપયોગ
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # તમારો ફિક્સ પ્રોમ્પ્ટ (સિસ્ટમ ઇન્સ્ટ્રક્શન)
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
                
                # API Call
                response = model.generate_content([prompt, image])
                
                # પરિણામ દર્શાવો
                st.success("એનાલિસિસ તૈયાર છે!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"કંઈક ભૂલ આવી છે: {e}")
