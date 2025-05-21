import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

st.set_page_config(page_title="ESP32 Weather Station", layout="centered")
st.title("📡 ESP32 Weather Station - Latest Data")

# ✅ Step 1: Load Firebase secrets from Streamlit secrets
try:
    firebase_conf = dict(st.secrets["firebase"])
    database_url = firebase_conf.pop("database_url")  # Remove database_url from the credentials dict

    # ✅ Step 2: Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_conf)
        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

    # ✅ Step 3: Fetch data from Firebase
    ref = db.reference("weather-data")
    all_data = ref.get()

    if not all_data:
        st.warning("No weather data found in the database.")
    else:
        # Get latest record
        latest_key = max(all_data.keys())
        latest_data = all_data[latest_key]

        # Display it
        st.subheader("🌤️ Latest Weather Data")
        st.json(latest_data)

        # Optional: Convert all data to table
        st.subheader("📊 All Weather Data")
        df = pd.DataFrame.from_dict(all_data, orient="index")
        df.index = pd.to_datetime(df.index, unit='s')
        st.dataframe(df.sort_index(ascending=False))

except KeyError:
    st.error("❌ Firebase credentials or database URL not found in secrets!")
except Exception as e:
    st.error(f"❌ Error: {e}")