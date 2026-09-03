import streamlit as st
from google import genai
from PIL import Image
import requests
import time
from datetime import datetime

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="રક્ષા શક્તિ સ્કૂલ જીરા વિશ્લેષણ",
    page_icon="🏫"
)

st.title("🏫 રક્ષા શક્તિ સ્કૂલ જીરામાંથી બાળકોને લખી આપેલ ૩૦ થી ૪૦ મુદ્દાનું વિશ્લેષણ")
st.write("બાળકોએ લખેલા મુદ્દાઓના ફોટા અપલોડ કરો અને એકસાથે વિશ્લેષણ મેળવો.")


# =========================================================
# SECRETS
# =========================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

except Exception:
    st.error("મહેરબાની કરીને Streamlit Secrets સેટ કરો.")
    st.stop()


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=api_key)


# =========================================================
# GEMINI ANALYSIS FUNCTION
# =========================================================

def generate_gemini_analysis(images, prompt):

    # Primary → Fallback models
    models = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    ]

    last_error = None

    for model_name in models:

        # દરેક model માટે 3 attempts
        for attempt in range(3):

            try:

                # દરેક image file pointer શરૂઆતથી વાંચાય
                prepared_images = []

                for image in images:
                    try:
                        image.seek(0)
                    except Exception:
                        pass

                    prepared_images.append(image)

                contents = [prompt] + prepared_images

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )

                # Empty response protection
                if response is None:
                    raise Exception("Gemini તરફથી response મળ્યો નથી.")

                analysis_text = getattr(response, "text", None)

                if not analysis_text:
                    raise Exception("Gemini તરફથી ખાલી response મળ્યો છે.")

                return analysis_text, model_name

            except Exception as e:

                last_error = e
                error_text = str(e)

                # 503 / UNAVAILABLE
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text
                    or "overloaded" in error_text
                ):

                    # છેલ્લો attempt નથી તો retry
                    if attempt < 2:

                        wait_seconds = 2 ** attempt

                        st.info(
                            f"⏳ {model_name} હાલમાં વ્યસ્ત છે. "
                            f"{wait_seconds} સેકન્ડ પછી ફરી પ્રયાસ થઈ રહ્યો છે..."
                        )

                        time.sleep(wait_seconds)
                        continue

                    else:
                        # આ modelના 3 attempts પૂરા
                        break

                else:
                    # 503 સિવાયની error હોય તો તરત બહાર
                    raise e

    # બધા models fail થયા
    raise Exception(
        "Gemini હાલમાં ઉપલબ્ધ નથી. "
        "થોડા સમય પછી ફરી પ્રયાસ કરો.\n\n"
        f"છેલ્લી ભૂલ: {last_error}"
    )


# =========================================================
# TELEGRAM SEND FUNCTION
# =========================================================

def send_to_telegram(
    priority,
    student_name,
    std,
    mobile_number,
    file_names,
    analysis_text
):

    message = f"""
🏫 *નવું રેસ્પોન્સ મળ્યું*

📅 તારીખ: {datetime.now().strftime("%d-%m-%Y %H:%M")}
🎯 પ્રાધાન્ય: {priority}
👶 બાળકનું નામ: {student_name}
📚 ધોરણ: {std}
📱 મોબાઈલ નંબર: {mobile_number}
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

        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        if response.status_code == 200:
            return True

        else:
            st.warning(
                f"Telegram મોકલવામાં સમસ્યા આવી. "
                f"Status: {response.status_code}"
            )
            return False

    except Exception as e:

        st.warning(
            f"Telegram મોકલવામાં ભૂલ: {e}"
        )

        return False


# =========================================================
# ૧. PRIORITY
# =========================================================

st.subheader("૧. તમે શિક્ષણમાં શેનું પ્રાધાન્ય આપો છો?")

priority = st.radio(
    "પસંદ કરો:",
    [
        "પસંદ કરો",
        "📚 શિક્ષણ",
        "🏫 સુવિધા"
    ],
    horizontal=True
)


# =========================================================
# ૨. STUDENT DETAILS
# =========================================================

if priority != "પસંદ કરો":

    st.subheader("૨. વિદ્યાર્થીની વિગતો")

    col1, col2 = st.columns(2)

    with col1:

        student_name = st.text_input(
            "બાળકનું નામ *"
        )

    with col2:

        std = st.selectbox(
            "ધોરણ *",
            [
                "પસંદ કરો",
                "૬",
                "૭",
                "૮"
            ]
        )

    mobile_number = st.text_input(
        "મોબાઈલ નંબર *",
        max_chars=10
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if (
        student_name
        and std != "પસંદ કરો"
        and mobile_number
    ):

        if not (
            mobile_number.isdigit()
            and len(mobile_number) == 10
        ):

            st.warning(
                "કૃપા કરી માન્ય ૧૦ અંકનો મોબાઈલ નંબર દાખલ કરો."
            )

            st.stop()


        # =================================================
        # ૩. FILE UPLOAD
        # =================================================

        st.subheader("૩. ફોટો અપલોડ કરો")

        uploaded_files = st.file_uploader(
            "બાળકોએ લખેલા મુદ્દાઓના ફોટા અહીં અપલોડ કરો "
            "(એકસાથે ઘણા પણ સિલેક્ટ કરી શકો છો)",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            accept_multiple_files=True
        )


        # =================================================
        # FILES AVAILABLE
        # =================================================

        if uploaded_files:

            st.write(
                f"**કુલ {len(uploaded_files)} ફાઈલ અપલોડ થઈ છે**"
            )


            # ---------------------------------------------
            # SHOW ALL PHOTOS
            # ---------------------------------------------

            for i, uploaded_file in enumerate(
                uploaded_files
            ):

                try:

                    uploaded_file.seek(0)

                    image = Image.open(
                        uploaded_file
                    )

                    st.image(
                        image,
                        caption=(
                            f"ફોટો {i+1}: "
                            f"{uploaded_file.name}"
                        ),
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"{uploaded_file.name} વાંચવામાં ભૂલ: {e}"
                    )


            # =================================================
            # ANALYSIS BUTTON
            # =================================================

            if st.button(
                "બધાનું એકસાથે એનાલિસિસ કરો 🚀",
                type="primary"
            ):

                # ---------------------------------------------
                # PROMPT
                # ---------------------------------------------

                prompt = """
આ બધા ફોટામાં આપેલા તમામ મુદ્દાઓને ધ્યાનથી વાંચો.

બધા ફોટાના તમામ મુદ્દાઓને એકસાથે ગણો અને માત્ર નીચેની ૩ કેટેગરીમાં વહેંચો:

૧. 📚 મૂળભૂત શિક્ષણ
૨. 🏫 શૈક્ષણિક સુવિધા
૩. 🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી

ખાસ સૂચના:

- દરેક મુદ્દો માત્ર એક જ કેટેગરીમાં ગણવો.
- બધા ફોટાના બધા મુદ્દાઓ ગણવા.
- એક જ મુદ્દો બે વાર ગણવો નહીં.
- કુલ મુદ્દાઓની સંખ્યા સ્પષ્ટ રીતે ગણવી.
- Percentage કુલ 100% થવી જોઈએ.
- ફોટામાં લખેલા મુદ્દાઓ પરથી જ વિશ્લેષણ કરવું.
- તમારી તરફથી નવા મુદ્દા ઉમેરવા નહીં.

જવાબ પહેલા માત્ર આ formatમાં આપો:

📚 મૂળભૂત શિક્ષણ: __ મુદ્દા — __%
🏫 શૈક્ષણિક સુવિધા: __ મુદ્દા — __%
🎯 પ્રવૃત્તિ / વહીવટ / ઉજવણી: __ મુદ્દા — __%

કુલ મુદ્દા: __

પછી માત્ર ૪–૬ સરળ ગુજરાતી વાક્યોમાં સમજાવો કે બાળકના ભવિષ્ય માટે "મૂળભૂત શિક્ષણ" શા માટે સૌથી મહત્વનું છે.

છેલ્લે આ અસરકારક વાક્ય આપો:

"સુવિધા બાળકને સગવડ આપે છે, પરંતુ ગુણવત્તાયુક્ત શિક્ષણ બાળકનું ભવિષ્ય ઘડે છે."
"""


                # =================================================
                # GEMINI ANALYSIS
                # =================================================

                with st.spinner(
                    "બધા ફોટાનું એકસાથે એનાલિસિસ થઈ રહ્યું છે..."
                ):

                    try:

                        # -----------------------------------------
                        # IMAGE OBJECTS PREPARE
                        # -----------------------------------------

                        images = []

                        for uploaded_file in uploaded_files:

                            uploaded_file.seek(0)

                            image = Image.open(
                                uploaded_file
                            ).convert("RGB")

                            images.append(image)


                        # -----------------------------------------
                        # GEMINI CALL WITH RETRY + FALLBACK
                        # -----------------------------------------

                        analysis_text, used_model = (
                            generate_gemini_analysis(
                                images,
                                prompt
                            )
                        )


                        # =================================================
                        # SUCCESS
                        # =================================================

                        st.success(
                            "✅ બધા ફોટાનું એકસાથે એનાલિસિસ તૈયાર છે!"
                        )

                        st.caption(
                            f"Gemini Model: {used_model}"
                        )

                        st.markdown(
                            analysis_text
                        )

                        st.divider()


                        # =================================================
                        # FILE NAMES
                        # =================================================

                        file_names = ", ".join(
                            [
                                f.name
                                for f in uploaded_files
                            ]
                        )


                        # =================================================
                        # TELEGRAM
                        # =================================================

                        send_to_telegram(

                            priority=priority,

                            student_name=student_name,

                            std=std,

                            mobile_number=mobile_number,

                            file_names=file_names,

                            analysis_text=analysis_text
                        )


                    # =====================================================
                    # ERROR HANDLING
                    # =====================================================

                    except Exception as e:

                        error_text = str(e)

                        if (
                            "503" in error_text
                            or "UNAVAILABLE" in error_text
                            or "high demand" in error_text
                        ):

                            st.error(
                                "⚠️ Gemini સર્વર હાલમાં વ્યસ્ત છે."
                            )

                            st.info(
                                "થોડીવાર પછી ફરી "
                                "'બધાનું એકસાથે એનાલિસિસ કરો 🚀' "
                                "બટન દબાવો."
                            )

                        else:

                            st.error(
                                f"ભૂલ: {error_text}"
                            )
