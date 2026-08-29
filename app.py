import streamlit as st
from google import genai
from PIL import Image

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="રક્ષા શક્તિ સ્કુલ જીરા - સટીક વિશ્લેષણ",
    page_icon="🏫"
)

st.title("🏫 રક્ષા શક્તિ સ્કુલ જીરા માંથી આપેલ ૩૦ થી ૪૦ મુદ્દાનું સટીક વિશ્લેષણ")

st.write(
    "બાળકોને આપવામાં આવેલા મુદ્દાઓના ફોટા અપલોડ કરો "
    "અને એકસાથે સટીક વિશ્લેષણ મેળવો."
)

# ---------------- Gemini API Key ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("મહેરબાની કરીને Gemini API Key Secrets માં સેટ કરો.")
    st.stop()

client = genai.Client(api_key=api_key)

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
        std = st.selectbox(
            "ધોરણ *",
            ["પસંદ કરો", "૬", "૭", "૮"]
        )

    # ---------------- ૩. ફાઈલ અપલોડ ----------------
    if student_name and std != "પસંદ કરો":

        st.subheader("૩. ફોટો અપલોડ કરો")

        uploaded_files = st.file_uploader(
            "બાળકોને આપવામાં આવેલા મુદ્દાઓના ફોટા અહીં અપલોડ કરો "
            "(એકસાથે ઘણા ફોટા પણ સિલેક્ટ કરી શકો છો)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        if uploaded_files:

            st.write(
                f"**કુલ {len(uploaded_files)} ફોટા અપલોડ થયા છે.**"
            )

            # ---------------- બધા ફોટા બતાવો ----------------
            for i, uploaded_file in enumerate(uploaded_files):

                image = Image.open(uploaded_file)

                st.image(
                    image,
                    caption=f"ફોટો {i + 1}: {uploaded_file.name}",
                    use_container_width=True
                )

            # ---------------- Analysis Button ----------------
            if st.button(
                "🔍 બધાનું એકસાથે સટીક વિશ્લેષણ કરો",
                type="primary",
                use_container_width=True
            ):

                prompt = """
રક્ષા શક્તિ સ્કુલ જીરા દ્વારા બાળકોને આપવામાં આવેલા
આ તમામ ફોટામાં લખાયેલા દરેક મુદ્દાને ધ્યાનથી વાંચો.

તમારે માત્ર નીચેની ૩ કેટેગરી પ્રમાણે સટીક અને નિષ્પક્ષ વિશ્લેષણ કરવાનું છે:

📚 ૧. મૂળભૂત શિક્ષણ

જે બાબતો બાળકના સીધા શિક્ષણ સાથે જોડાયેલી હોય:
- શિક્ષક
- શિક્ષકની ગુણવત્તા
- અનુભવી વિષય શિક્ષક
- નિયમિત teaching
- વર્ગખંડનું શિક્ષણ
- વિષયની સમજણ
- concept understanding
- homework / classwork
- પરીક્ષા
- ટેસ્ટ
- assessment
- academic progress
- પરિણામ
- answer writing
- actual learning outcome

🏫 ૨. શૈક્ષણિક સુવિધા

જે બાબતો બાળકને શિક્ષણમાં મદદરૂપ થતી સુવિધા અથવા welfare હોય:
- લેબ
- લાઇબ્રેરી
- કોમ્પ્યુટર
- રમતગમત
- આરોગ્ય
- સુરક્ષા
- હોસ્ટેલ
- પાણી
- ફર્નિચર
- અન્ય શૈક્ષણિક અથવા વિદ્યાર્થી સુવિધાઓ

🎯 ૩. પ્રવૃત્તિ / વહીવટ / ઉજવણી

જે બાબતો મુખ્યત્વે:
- કાર્યક્રમ
- ઉજવણી
- પ્રવાસ
- વિવિધ activity
- વસ્તુ વિતરણ
- વહીવટી કામગીરી
- સંચાલન
- અન્ય event / promotion

સાથે જોડાયેલી હોય અને જેનાથી સીધો academic improvement સાબિત થતો ન હોય.

------------------------------------------------

મહત્વપૂર્ણ નિયમ:

માત્ર કોઈ કામ કરવામાં આવ્યું છે એટલે તેને
"મૂળભૂત શિક્ષણ" ગણવું નહીં.

બાળકની:
વિષય સમજણ,
teaching quality,
નિયમિત અભ્યાસ,
assessment,
academic progress
અથવા learning outcome
સાથે સીધો સંબંધ હોય ત્યારે જ તેને
"મૂળભૂત શિક્ષણ" ગણવું.

સુવિધા અને activity ને શિક્ષણ સાથે ભેળવવી નહીં.

------------------------------------------------

કુલ મળેલા તમામ મુદ્દાઓની ગણતરી કરીને આ રીતે જવાબ આપો:

📚 મૂળભૂત શિક્ષણ: __ મુદ્દા — __%

🏫 શૈક્ષણિક સુવિધા: __ મુદ્દા — __%

🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી: __ મુદ્દા — __%

કુલ મુદ્દા: __

------------------------------------------------

ત્યારબાદ માત્ર ૪ થી ૬ સરળ ગુજરાતી વાક્યોમાં સમજાવો:

બાળકના ભવિષ્ય માટે મૂળભૂત શિક્ષણ શા માટે સૌથી મહત્વનું છે?

ખાસ કરીને સમજાવો કે:

સારી અને સ્થિર અનુભવી વિષય શિક્ષકમંડળી,
નિયમિત teaching,
વિષયની સમજણ,
concept-based learning,
English answer writing,
written practice
અને regular assessment
બાળકના academic outcome માટે શા માટે મહત્વપૂર્ણ છે.

ધોરણ ૮થી જ concept સમજણ અને answer writingની
નિયમિત practice બાળકને આગળની પરીક્ષાઓ માટે કેવી રીતે મદદ કરે છે
તે ટૂંકમાં સમજાવો.

GSEB ચોક્કસપણે CBSE જેવી જ પરીક્ષા પદ્ધતિ અપનાવશે
એવો દાવો ન કરવો.

જો પરીક્ષા પદ્ધતિ competency-based અથવા descriptive
પ્રશ્નો તરફ વધુ જાય તો concept understanding,
answer writing અને regular assessmentનું મહત્વ વધે છે
એટલું જ સમજાવવું.

------------------------------------------------

અંતે આ અસરકારક વાક્ય આપો:

"સુવિધા બાળકને સગવડ આપે છે, પરંતુ ગુણવત્તાયુક્ત શિક્ષણ બાળકનું ભવિષ્ય ઘડે છે."

------------------------------------------------

જવાબ:
- ટૂંકો રાખવો
- સરળ ગુજરાતી ભાષામાં આપવો
- સામાન્ય વાલીને તરત સમજાય એવો હોવો
- પક્ષપાત વગરનો હોવો
- કોઈ વ્યક્તિ, સંચાલક કે શિક્ષકની તરફેણ અથવા વિરોધ ન કરવો
- માત્ર ફોટામાં ઉપલબ્ધ માહિતીના આધારે analysis કરવું

મુદ્દાઓની લાંબી યાદી ફરીથી ન લખવી.
દરેક મુદ્દાનો અલગ score આપવો નહીં.
મુખ્ય ધ્યાન "મૂળભૂત શિક્ષણ" અને "સુવિધા/પ્રવૃત્તિ" વચ્ચેના તફાવત પર રાખવું.
"""

                with st.spinner(
                    "બધા ફોટાનું એકસાથે સટીક વિશ્લેષણ થઈ રહ્યું છે..."
                ):

                    try:

                        # બધા ફોટા વાંચવા
                        images = []

                        for uploaded_file in uploaded_files:
                            image = Image.open(uploaded_file).convert("RGB")
                            images.append(image)

                        # Prompt + બધા ફોટા
                        contents = [prompt] + images

                        # Gemini Analysis
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents
                        )

                        analysis_text = response.text

                        st.success(
                            "✅ સટીક વિશ્લેષણ તૈયાર છે!"
                        )

                        st.markdown(analysis_text)

                    except Exception as e:

                        st.error(
                            f"વિશ્લેષણ કરવામાં ભૂલ આવી: {e}"
                        )
