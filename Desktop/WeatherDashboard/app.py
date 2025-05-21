import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import json

st.set_page_config(page_title="ESP32 Weather Station", layout="centered")
st.title("📡 ESP32 Weather Station - Latest Data")

try:
    # ✅ 1. Read JSON string and parse to dict
    cred_json = st.secrets["FIREBASE_CREDENTIAL_JSON"]
    firebase_conf = json.loads(cred_json)
    database_url = st.secrets["database_url"]

    # ✅ 2. Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_conf)
        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

    # ✅ 3. Fetch and show latest data
    ref = db.reference("weather-data")
    all_data = ref.get()

    if not all_data:
        st.warning("No weather data found.")
    else:
        latest_key = max(all_data.keys())
        latest_data = all_data[latest_key]

        st.subheader("🌤️ Latest Weather Data")
        st.json(latest_data)

        st.subheader("📊 All Weather Data")
        df = pd.DataFrame.from_dict(all_data, orient="index")
        df.index = pd.to_datetime(df.index, unit='s')
        st.dataframe(df.sort_index(ascending=False))

except KeyError:
    st.error("❌ Firebase credentials or database URL not found in secrets!")
except ValueError as e:
    st.error(f"❌ ValueError: {e}")
except Exception as e:
    st.error(f"❌ Unexpected Error: {e}")