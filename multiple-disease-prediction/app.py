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

# ===================== LOAD MODELS =====================
working_dir = os.path.dirname(os.path.abspath(__file__))

diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))

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
                st.success("💡 Click 'Open in Google Maps' to view ratings & full details.")

                for hospital in hospitals:

                    maps_link = f"https://www.google.com/maps/search/?api=1&query={hospital['lat']},{hospital['lon']}"
                    directions_link = f"https://www.google.com/maps/dir/?api=1&destination={hospital['lat']},{hospital['lon']}"

                    st.markdown(f"""
                    ---
                    ### 🏥 {hospital['name']}
                    📍 Distance: **{hospital['distance']} km**  
                    🏠 Address: {hospital['address']}  
                    ☎ Contact: {hospital['phone']}  

                    🔗 [Open in Google Maps]({maps_link})  
                    🧭 [Get Directions]({directions_link})
                    """)
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

# =====================================================
# ================= DIABETES PAGE =====================
# =====================================================
if selected == 'Diabetes Prediction':

    st.title('Diabetes Prediction using Hybrid ML')

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

        st.subheader(f"Diabetes Risk Score: {risk:.2f}%")

        if risk > 60:
            st.error("High Risk of Diabetes")
            show_hospitals_if_needed("Diabetes", risk, city)
        elif risk > 30:
            st.warning("Moderate Risk of Diabetes")
        else:
            st.success("Low Risk of Diabetes")

# =====================================================
# =============== HEART DISEASE PAGE ==================
# =====================================================
if selected == 'Heart Disease Prediction':

    st.title('Heart Disease Prediction using Hybrid ML')

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

        st.subheader(f"Heart Disease Risk Score: {risk:.2f}%")

        if risk > 60:
            st.error("High Risk of Heart Disease")
            show_hospitals_if_needed("Heart Disease", risk, city)
        elif risk > 30:
            st.warning("Moderate Risk of Heart Disease")
        else:
            st.success("Low Risk of Heart Disease")

# =====================================================
# ================= PARKINSONS PAGE ===================
# =====================================================
if selected == "Parkinsons Prediction":

    st.title("Parkinson's Disease Prediction using ML")

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

        st.subheader(f"Parkinson's Risk Score: {risk:.2f}%")

        if risk > 60:
            st.error("High Risk of Parkinson's Disease")
            show_hospitals_if_needed("Parkinson", risk, city)
        elif risk > 30:
            st.warning("Moderate Risk of Parkinson's Disease")
        else:
            st.success("Low Risk of Parkinson's Disease")