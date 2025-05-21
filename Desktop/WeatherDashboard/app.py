import streamlit as st
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import datetime
import json

# ✅ Load from Streamlit secrets
try:
    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIAL_JSON"])
    database_url = st.secrets["DATABASE_URL"]
except KeyError:
    st.error("❌ Firebase credentials or database URL not found in secrets!")
    st.stop()

# ✅ Set Streamlit page config
st.set_page_config(page_title="ESP32 Weather Station", layout="wide")

# ✅ Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {'databaseURL': database_url})

# ✅ Auto-refresh every 60s
st_autorefresh(interval=60000, key="weatherdata_refresh")

# ✅ Get data
def get_latest_data():
    try:
        ref = db.reference('/devices')
        devices = ref.get()

        if not devices:
            return None, "❌ No devices found."

        device_id = list(devices.keys())[0]
        records = devices[device_id].get('records', {})

        if not records:
            return None, "⚠️ No records found under the device."

        valid_data = {}
        for k, v in records.items():
            try:
                dt = datetime.strptime(k, "%Y-%m-%d_%H:%M:%S")
                valid_data[dt] = v
            except ValueError:
                continue

        if not valid_data:
            return None, "⚠️ No valid timestamped data found."

        df = pd.DataFrame.from_dict(valid_data, orient='index')
        df.index.name = "Timestamp"
        df.sort_index(inplace=True)

        return df, None

    except Exception as e:
        return None, f"❌ Error: {e}"

# ✅ Streamlit UI
st.title("📡 ESP32 Weather Station - Latest Data")

df, error_msg = get_latest_data()

if error_msg:
    st.warning(error_msg)
elif df is not None:
    latest = df.iloc[-1]
    st.success(f"✅ Latest data from: `{df.index[-1]}`")
    st.json(latest.to_dict())

    st.subheader("📊 Historical Data (Last 24 Records)")
    st.dataframe(df.tail(24))