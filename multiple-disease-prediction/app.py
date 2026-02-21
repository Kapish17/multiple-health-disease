import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Health Assistant",
    layout="wide",
    page_icon="🧑‍⚕️"
)

# ===================== SMOOTH FADE ANIMATION =====================
# Fade-in animation CSS
st.markdown("""
<style>
.fade-in {
    animation: fadeIn 0.8s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# Hospital card hover CSS
st.markdown("""
<style>
.hospital-card {
    padding: 18px;
    border-radius: 14px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}
.hospital-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# ===================== DISCLAIMER =====================
st.warning("⚠️ This system is for educational purposes only and does NOT replace professional medical advice.")

# ===================== LOAD MODELS =====================
working_dir = os.path.dirname(os.path.abspath(__file__))

diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))

# ===================== ANIMATED RISK BAR =====================
def show_risk_bar(risk):
    if risk <= 30:
        color = "#2ECC71"
    elif risk <= 60:
        color = "#F1C40F"
    else:
        color = "#E74C3C"

    st.markdown(f"""
    <div style="background-color:#eee;border-radius:20px;padding:4px;">
        <div style="
            width:{risk}%;
            background-color:{color};
            padding:10px;
            border-radius:20px;
            text-align:center;
            color:white;
            font-weight:bold;
            transition: width 1.2s ease-in-out;">
            {risk:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===================== LOCATION INPUT =====================
st.sidebar.subheader("📍 Location Details")
city = st.sidebar.text_input("Enter Your City for Nearby Hospitals")

# ===================== SPECIALIST MAPPING =====================
def get_specialist(disease):
    mapping = {
        "Diabetes": "Diabetologist",
        "Heart Disease": "Cardiologist",
        "Parkinson": "Neurologist"
    }
    return mapping.get(disease, "General Physician")

# ===================== HOLISTIC THERAPY MODULES =====================
def show_color_therapy(disease):
    color_map = {
        "Diabetes": "#3498DB",
        "Heart Disease": "#2ECC71",
        "Parkinson": "#9B59B6"
    }
    color = color_map.get(disease, "#95A5A6")

    st.markdown(f"""
    <div style="background-color:{color};padding:20px;border-radius:12px;">
    <h3 style="color:white;">🌈 Colour Therapy</h3>
    <p style="color:white;">
    Focus on this calming colour for 3–5 minutes.
    Practice deep breathing: Inhale 4 sec → Hold 4 sec → Exhale 4 sec.
    </p>
    </div>
    """, unsafe_allow_html=True)

def show_acupressure(disease):

    if disease == "Heart Disease":
        image_url = "https://i.imgur.com/3XjKX8N.png"
        top, left = "150px", "135px"
        point = "PC6 (Inner Wrist)"
        instruction = "Use your thumb and apply firm circular pressure for 1–2 minutes."

    elif disease == "Diabetes":
        image_url = "https://i.imgur.com/4Q9Z1Zm.png"
        top, left = "220px", "155px"
        point = "SP6 (Inner Leg)"
        instruction = "Press gently using steady circular motion for 2 minutes."

    elif disease == "Parkinson":
        image_url = "https://i.imgur.com/qkdpN.jpg"
        top, left = "40px", "140px"
        point = "GV20 (Top Center of Head)"
        instruction = "Apply gentle upward pressure for 1–2 minutes."

    else:
        return

    st.subheader("🖐 Animated Acupressure Guidance")

    st.markdown(f"""
    <style>
    .body-container {{
        position: relative;
        width: 300px;
        margin: auto;
    }}

    .pulse-dot {{
        position: absolute;
        top: {top};
        left: {left};
        width: 25px;
        height: 25px;
        background: red;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); opacity: 0.8; }}
        50% {{ transform: scale(1.6); opacity: 0.3; }}
        100% {{ transform: scale(1); opacity: 0.8; }}
    }}
    </style>

    <div class="body-container">
        <img src="{image_url}" width="300">
        <div class="pulse-dot"></div>
    </div>

    <p style="text-align:center;">
    📍 <b>{point}</b><br>
    {instruction}
    </p>
    """, unsafe_allow_html=True)

def show_lifestyle(disease):
    st.subheader("🧘 Lifestyle Recommendations")

    if disease == "Diabetes":
        st.write("• 🚶 30 min brisk walking daily")
        st.write("• 🥗 Reduce sugar & refined carbs")
        st.write("• 💧 Stay hydrated")

    elif disease == "Heart Disease":
        st.write("• 🏃 Light cardio exercise")
        st.write("• 🥑 Low saturated fat diet")
        st.write("• 🧘 Stress reduction practices")

    elif disease == "Parkinson":
        st.write("• 🧘 Balance & coordination exercises")
        st.write("• 🥦 Anti-inflammatory diet")
        st.write("• 💤 Maintain regular sleep routine")

def show_therapy_modules(disease):
    st.markdown("---")
    st.header("🌿 Holistic Therapy Support")
    show_color_therapy(disease)
    show_acupressure(disease)
    show_lifestyle(disease)

# ===================== GET COORDINATES =====================
def get_coordinates(city):
    try:
        geolocator = Nominatim(user_agent="health_app")
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# ===================== GET NEARBY HOSPITALS =====================
def get_nearby_hospitals(lat, lon):
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"hospital|clinic|doctors"](around:15000,{lat},{lon});
      way["amenity"~"hospital|clinic|doctors"](around:15000,{lat},{lon});
      relation["amenity"~"hospital|clinic|doctors"](around:15000,{lat},{lon});
    );
    out center;
    """

    data = None
    for url in overpass_urls:
        try:
            response = requests.post(url, data=query, timeout=30)
            if response.status_code == 200:
                data = response.json()
                break
        except:
            continue

    if not data:
        st.error("⚠ Overpass server busy. Please try again later.")
        return []

    hospitals = []
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name', 'N/A')
        phone = tags.get('phone') or tags.get('contact:phone') or "Not Available"
        address = (
            tags.get('addr:full') or
            tags.get('addr:street') or
            tags.get('addr:city') or
            "Address Not Available"
        )

        if 'lat' in element:
            hospital_location = (element['lat'], element['lon'])
        else:
            hospital_location = (element['center']['lat'], element['center']['lon'])

        distance = geodesic((lat, lon), hospital_location).km

        hospitals.append({
            "name": name,
            "phone": phone,
            "address": address,
            "distance": round(distance, 2),
            "lat": hospital_location[0],
            "lon": hospital_location[1]
        })

    hospitals = sorted(hospitals, key=lambda x: x['distance'])
    return hospitals[:8]

# ===================== SHOW HOSPITALS =====================
# ===================== SHOW HOSPITALS =====================
def show_hospitals_if_needed(disease, risk, city):

    if risk > 60 and city:

        specialist = get_specialist(disease)
        st.info(f"👨‍⚕ Recommended Specialist: {specialist}")

        lat, lon = get_coordinates(city)

        if lat and lon:

            with st.spinner("🔍 Searching nearby healthcare centers..."):
                hospitals = get_nearby_hospitals(lat, lon)

            if hospitals:

                st.subheader("🏥 Nearby Healthcare Centers (15km radius)")
                st.success("💡 Click hospital name to view details.")

                for i, hospital in enumerate(hospitals):

                    maps_link = f"https://www.google.com/maps/search/?api=1&query={hospital['lat']},{hospital['lon']}"
                    directions_link = f"https://www.google.com/maps/dir/?api=1&destination={hospital['lat']},{hospital['lon']}"

                    with st.expander(f"🏥 {hospital['name']} • {hospital['distance']} km"):

                        st.markdown(f"""
                        <div class="hospital-card">
                        📍 <b>Distance:</b> {hospital['distance']} km <br>
                        🏠 <b>Address:</b> {hospital['address']} <br>
                        ☎ <b>Contact:</b> {hospital['phone']} <br><br>
                        🔗 <a href="{maps_link}" target="_blank">Open in Google Maps</a><br>
                        🧭 <a href="{directions_link}" target="_blank">Get Directions</a>
                        </div>
                        """, unsafe_allow_html=True)

            else:
                st.warning("No hospitals found nearby.")

        else:
            st.error("City not found. Please enter a valid city name.")

        
# ===================== SIDEBAR =====================
with st.sidebar:
    selected = option_menu(
        'Multiple Disease Prediction System',
        ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction'],
        menu_icon='hospital-fill',
        icons=['activity', 'heart', 'person'],
        default_index=0
    )

# ===================== DIABETES PAGE =====================
if selected == 'Diabetes Prediction':

    st.markdown('<div class="fade-in"><h1>Diabetes Prediction using Hybrid ML</h1></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        Pregnancies = st.text_input('Pregnancies')
        SkinThickness = st.text_input('Skin Thickness')
        DPF = st.text_input('Diabetes Pedigree Function')

    with col2:
        Glucose = st.text_input('Glucose Level')
        Insulin = st.text_input('Insulin Level')
        Age = st.text_input('Age')

    with col3:
        BP = st.text_input('Blood Pressure')
        BMI = st.text_input('BMI')

    if st.button('Diabetes Test Result'):
        user_input = [
            float(Pregnancies), float(Glucose), float(BP),
            float(SkinThickness), float(Insulin),
            float(BMI), float(DPF), float(Age)
        ]

        prediction = diabetes_model.predict([user_input])[0]

        try:
            risk = diabetes_model.predict_proba([user_input])[0][1] * 100
        except:
            risk = 100 if prediction == 1 else 0

        if float(Glucose) > 160 and float(BMI) > 30:
            risk = max(risk, 75)

        st.subheader("Diabetes Risk Score")
        show_risk_bar(risk)

        if risk > 60:
            st.error("High Risk of Diabetes")
            show_hospitals_if_needed("Diabetes", risk, city)
            show_therapy_modules("Diabetes")
        elif risk > 30:
            st.warning("Moderate Risk of Diabetes")
        else:
            st.success("Low Risk of Diabetes")

# ===================== HEART PAGE =====================
if selected == 'Heart Disease Prediction':

    st.markdown('<div class="fade-in"><h1>Heart Disease Prediction using Hybrid ML</h1></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.text_input('Age')
        trestbps = st.text_input('Resting Blood Pressure')
        restecg = st.text_input('Resting ECG')
        oldpeak = st.text_input('ST Depression')

    with col2:
        sex = st.text_input('Sex (1=Male, 0=Female)')
        chol = st.text_input('Cholesterol')
        thalach = st.text_input('Max Heart Rate')
        slope = st.text_input('Slope')

    with col3:
        cp = st.text_input('Chest Pain Type')
        fbs = st.text_input('Fasting Blood Sugar >120')
        exang = st.text_input('Exercise Induced Angina')
        ca = st.text_input('Major Vessels')
        thal = st.text_input('Thal (0,1,2)')

    if st.button('Heart Disease Test Result'):
        user_input = [
            float(age), float(sex), float(cp), float(trestbps),
            float(chol), float(fbs), float(restecg), float(thalach),
            float(exang), float(oldpeak), float(slope), float(ca), float(thal)
        ]

        prediction = heart_disease_model.predict([user_input])[0]

        try:
            risk = heart_disease_model.predict_proba([user_input])[0][1] * 100
        except:
            risk = 100 if prediction == 1 else 0

        if float(age) > 45 and float(trestbps) > 140 and float(chol) > 240:
            risk = max(risk, 80)

        st.subheader("Heart Disease Risk Score")
        show_risk_bar(risk)

        if risk > 60:
            st.error("High Risk of Heart Disease")
            show_hospitals_if_needed("Heart Disease", risk, city)
            show_therapy_modules("Heart Disease")
        elif risk > 30:
            st.warning("Moderate Risk of Heart Disease")
        else:
            st.success("Low Risk of Heart Disease")

# ===================== PARKINSON PAGE =====================
if selected == "Parkinsons Prediction":

    st.markdown("<div class='fade-in'><h1>Parkinson's Disease Prediction using ML</h1></div>", unsafe_allow_html=True)

    cols = st.columns(5)
    inputs = []

    fields = [
        'Fo', 'Fhi', 'Flo', 'Jitter%', 'JitterAbs', 'RAP',
        'PPQ', 'DDP', 'Shimmer', 'Shimmer(dB)', 'APQ3',
        'APQ5', 'APQ', 'DDA', 'NHR', 'HNR',
        'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE'
    ]

    for i, field in enumerate(fields):
        with cols[i % 5]:
            inputs.append(st.text_input(field))

    if st.button("Parkinson's Test Result"):
        user_input = [float(x) for x in inputs]

        prediction = parkinsons_model.predict([user_input])[0]

        try:
            risk = parkinsons_model.predict_proba([user_input])[0][1] * 100
        except:
            risk = 100 if prediction == 1 else 0

        st.subheader("Parkinson's Risk Score")
        show_risk_bar(risk)

        if risk > 60:
            st.error("High Risk of Parkinson's Disease")
            show_hospitals_if_needed("Parkinson", risk, city)
            show_therapy_modules("Parkinson")
        elif risk > 30:
            st.warning("Moderate Risk of Parkinson's Disease")
        else:
            st.success("Low Risk of Parkinson's Disease")
