import streamlit as st
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import datetime

# 1) Configure page
st.set_page_config(page_title="ESP32 Weather Station", layout="wide")

# 2) Auto-refresh
st_autorefresh(interval=60000, key="weatherdata_refresh")

# 3) Load secrets directly as dict
firebase_conf = st.secrets["firebase"]
database_url = st.secrets["database_url"]

# 4) Initialize Firebase once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_conf)
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})

# 5) Function to fetch latest data
def get_latest_data():
    try:
        devices = db.reference("/devices").get()
        if not devices:
            return None, "❌ No devices found."
        device_id = next(iter(devices))
        records = devices[device_id].get("records", {})
        if not records:
            return None, "⚠️ No records under that device."

        valid = {}
        for ts, vals in records.items():
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d_%H:%M:%S")
                valid[dt] = vals
            except ValueError:
                pass

        if not valid:
            return None, "⚠️ No valid timestamped data."

        df = pd.DataFrame.from_dict(valid, orient="index")
        df.index.name = "Timestamp"
        df.sort_index(inplace=True)
        return df, None

    except Exception as e:
        return None, f"❌ Error: {e}"

# 6) UI
st.title("📡 ESP32 Weather Station - Latest Data")

df, err = get_latest_data()
if err:
    st.warning(err)
elif df is not None:
    latest = df.iloc[-1]
    st.success(f"✅ Latest data from: {df.index[-1]}")
    st.json(latest.to_dict())
    st.subheader("📊 Historical Data (Last 24 Records)")
    st.dataframe(df.tail(24))